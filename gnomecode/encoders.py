from collections.abc import Iterable

import numpy as np
from intervals import FloatInterval as I
from line_profiler_pycharm import profile

# Scikit-Learn's numpy array input validation and reformatting that we've found useful in the past
# #from sklearn.utils.validation import check_X_y, check_array

__all__ = ["_EncoderBase", "_IntervalEncoder", "_PlaceCellEncoder", "_PeriodicEncoder"] \
          + ["MultiEncoder", ] + ["RandomizedPlaceCellEncoder", ] + ["FixedWeightEncoder", "TaperingWeightEncoder"] \
          + ["PeriodicCellEncoder", "PeriodicScalarEncoder"]


# abstract superclass of all encoders
class _EncoderBase:
    """
    Variants:
    - bounded or unbounded input domain
    - single or repeated input domain regions (receptive field)
    - input region defined by Bravais lattice: 1) point unit ball or 2) primitive unit cell
    - encoding of input domain is 1) partition, 2) covering, 3) packing, or 4) sampling (overlaps + gaps)

    """

    def __init__(self, oob_method="silent", lower_bound=0, upper_bound=1, seed=None):
        """
        Constructor code

        """

        # Out-Of-Bound methods: ["clamp", "exception", "modulo", "silent"]
        self.oob_method = oob_method
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.input_width = self.upper_bound - self.lower_bound

        if seed is None:
            self.rng = np.random.RandomState()
        else:
            self.rng = np.random.RandomState(seed=seed)

    def _input(self, X):

        # enforces well-formed input with options,
        # here input should be 2D array where X.shape == (num_samples, num_features)
        # X = check_array(X, ensure_2d=True)

        if self.oob_method == "exception" and (np.any(X > self.upper_bound) or np.any(X < self.lower_bound)):
            raise Exception("Attempting to encode input value out of bounds of interval [%.2f,%.2f)" % (
                    self.lower_bound, self.upper_bound))

        elif self.oob_method == "clamp":
            x_clamp = X
            x_clamp = np.where(x_clamp >= self.upper_bound, self.upper_bound - 1e-10, x_clamp)
            x_clamp = np.where(x_clamp < self.lower_bound, self.lower_bound + 1e-10, x_clamp)
            X = x_clamp

        elif self.oob_method == "modulo":
            # value with respect to lower bound
            x_rel = X - self.lower_bound

            # values modulo this input interval length
            x_modulo = np.mod(x_rel, self.input_width)

            # back into real coordinates within fund. region
            x_fund_region = x_modulo + self.lower_bound

            X = x_fund_region

        elif self.oob_method == "silent":
            # do nothing
            pass

        else:
            raise Exception("Undefined out-of-bounds method: '%s'" % self.oob_method)

        return X

    def config(self):
        """
        Specialized configuration code for each variant

        :return:
        """

    def encode(self, X):
        """
        transform one or many values from the input domain into the output encoding

        :return:
        """
        return None


class MultiEncoder(_EncoderBase):

    def __init__(self, upper_bound=None, lower_bound=None, **kwargs):

        # superclass constructor
        super().__init__(**kwargs)

        self.encoders = []

        self.w = 3
        self.l = 0.1
        self.n = 0
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.L = None
        self.region_boundaries = []
        self.region_centers = []
        self.region_codes = []
        self.region_weights = []
        self.region_deltas = []
        self.bins = []
        self.regions = []
        self.region_sizes = []
        self.region_indices = []

        self.is_init = False

    @profile
    def add_encoder(self, encoder):
        self.encoders.append(encoder)
        self.config()

    @profile
    def config(self):

        self.upper_bound = self.compute_upper_bound()
        self.lower_bound = self.compute_lower_bound()
        self.L = self.compute_L()
        self.n = self.compute_n()

        self.region_boundaries, self.region_deltas = self.compute_boundaries()

        # find region centers between boundary points
        self.region_centers = self.region_boundaries[:-1] + np.diff(self.region_boundaries) / 2

        self.bins = []
        for encoder in self.encoders:
            self.bins += encoder.bins

        if len(self.bins) < 1:
            raise Exception("Encoder as configured doesn't allocate any bins")

        # unique regions intersected by combinations of bins
        self.regions = [I.closed_open(self.region_boundaries[i], self.region_boundaries[i + 1]) for i in
                        range(0, len(self.region_boundaries) - 1)]

        self.region_sizes = np.diff(self.region_boundaries) / 2

        self.is_init = True

        # compute codes for each center point
        self.region_codes = self.encode(self.region_centers)

        # compute weights for each region
        self.region_weights = np.count_nonzero(self.region_codes, axis=1)

        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]

    @profile
    def encode(self, X):
        if not self.is_init:
            raise Exception("Multi-Encoder is not properly configured.")

        # encode value for each subencoder and concatenate result
        if isinstance(X, np.ndarray):
            codes_by_encoder = [encoder.encode(X) for encoder in self.encoders]
            codes_by_value = np.concatenate(codes_by_encoder, axis=1)
        else:
            codes_by_encoder = [encoder.encode(X) for encoder in self.encoders]
            codes_by_value = np.concatenate(codes_by_encoder)

        return codes_by_value

    def compute_lower_bound(self):
        lower_bound = min([self.encoders[k].lower_bound for k in range(len(self.encoders))])

        if self.lower_bound is None or lower_bound < self.lower_bound:
            return lower_bound
        else:
            return self.lower_bound

    def compute_upper_bound(self):
        upper_bound = max([self.encoders[k].upper_bound for k in range(len(self.encoders))])

        if self.upper_bound is None or upper_bound > self.upper_bound:
            return upper_bound
        else:
            return self.upper_bound

    def compute_L(self):
        L = self.upper_bound - self.lower_bound
        return L

    def compute_n(self):
        # n_tuple = tuple([encoder.n for encoder in self.encoders])
        total_n = sum([encoder.n for encoder in self.encoders])
        return total_n

    def compute_boundaries(self):

        # merge boundaries from each of the sub-encoders
        delta_count = {}
        for encoder in self.encoders:
            boundaries = encoder.region_boundaries
            region_deltas = encoder.region_deltas

            for i in range(len(boundaries)):
                key = boundaries[i]
                cnt = region_deltas[i]
                try:
                    delta_count[key] += cnt
                except:
                    delta_count[key] = cnt

        sorted_boundaries = sorted(list(delta_count.keys()))
        sorted_deltas = [delta_count[k] for k in sorted_boundaries]

        # find pairs of boundary points that are near enough to each other to be considered identical
        # remove these as duplicates and merge delta counts
        unique_boundaries = []
        unique_delta_count = {}
        boundary_groups = []

        # find groups of near boundaries
        j = 0
        while j < len(sorted_boundaries):
            boundary_group = [j]
            last_k = j + 1
            for k in range(j + 1, len(sorted_boundaries)):
                bound_diff = abs(sorted_boundaries[j] - sorted_boundaries[k])
                last_k = k

                if bound_diff < 0.001:
                    boundary_group.append(k)
                else:
                    break
            boundary_groups.append(boundary_group)
            j = last_k

        # merge groups into single bounaries
        for boundary_group in boundary_groups:

            # singleton
            if len(boundary_group) == 1:
                index = boundary_group[0]
                key = sorted_boundaries[index]
                unique_boundaries.append(key)
                unique_delta_count[key] = sorted_deltas[index]

            # multiple boundaries to be merged
            else:
                # find val with smallest number of digits
                min_index = -1
                min_count = 1e100
                for index in boundary_group:
                    float_val = sorted_boundaries[index]
                    char_count = len(str(float_val))
                    if char_count < min_count:
                        min_count = char_count
                        min_index = index

                min_key = sorted_boundaries[min_index]

                unique_boundaries.append(min_key)
                unique_delta_count[min_key] = 0
                for index in boundary_group:
                    unique_delta_count[min_key] += sorted_deltas[index]

        unique_deltas = [unique_delta_count[k] for k in unique_boundaries]

        return unique_boundaries, unique_deltas

    """
    # getter methods
    
    def get_w(self):
        w_tuple = tuple([encoder.w for encoder in self.encoders])
        return w_tuple

    def get_l(self):
        l_tuple = tuple([self.encoders[k].l for k in range(len(self.encoders))])
        return l_tuple

    def get_region_centers(self):
        return self.region_centers

    def get_region_codes(self):
        return self.region_codes

    def get_region_weights(self):
        return self.region_weights

    def get_region_deltas(self):
        return self.region_deltas
    """

    """
    # property decorators
    
    w = property(get_w)
    n = property(get_n)
    l = property(get_l)
    L = property(get_L)
    lower_bound = property(get_lower_bound)
    upper_bound = property(get_upper_bound)
    boundaries = property(get_boundaries)
    region_centers = property(get_region_centers)
    region_codes = property(get_region_codes)
    region_weights = property(get_region_weights)
    """


class _IntervalEncoder(_EncoderBase):
    """
    use appropriate encoder parameter equation and fill in any missing parameter
    - Encoder Type Options
        - fixed_weight, tapering_weight, upper_bound, lower_bound
        - optional offset parameter that shifts the bounds
    - Encoder Parameters
        - w, l, L, n (3 independent, 1 dependent, 3DOF)
            - L computed from upper_bound and lower_bound
            - throw exception if provided parameters don't evaluate to equivalence with equation
            - computing missing parameter if underspecified
    - compute step_size, distance between the minimum boundaries of consecutive bins (DERIVED)

    For encoders that are UNIFORM and BOUNDED, we give the corresponding parameter equations.

    We define the following parameters:
    - 'w' is weight,
    - 'n' is number of bins,
    = 'L' is size of interval,
    - 'l' is bin size.

    We define the equations as follows:
    - for fixed weight, overlapping bins, imbricating code
        - w=1: l=L/n
        - w>1: l=(w*L)/(n-w+1)

    - for tapering weight, all bins proper subset of interval
        - w=1: l=L/n
        - w>1: l=(w*L)/(n+w-1)

    TODO:
    - compute and return sequence of unique code values from a to b
        - convert path through input domain to unique input samples to code sequence

    + calculate and return all the change-point boundaries
        + boundaries with: gaps, no gaps, and overlaps
        + length between boundaries
        - cartesian product of overlapping regions (granulated regions)

    + calculate region features
        + center-points of regions
        + encoded value of region
        + code weight per region
        - similarity score for some exemplar for each region

    + out-of-bounds behavior for bounded encoders
        + throw exception
        + clamp input to upper or lower bound

    + fixed weight vs. tapering weight encoder
        + fixed weight: some regions are out-of-bounds to ensure constant weight
        + tapering weight: all regions are within region bounds

    """

    @profile
    def __init__(self, n=None, l=None, L=1.0, w=1, lower_bound=0, upper_bound=None, **kwargs):
        """
        Required: must provide either 'n' or 'l', but not both.

        :param n: number of bins, number of bits, either 'n' or 'l' required, but not both
        :param l: size of bin, either 'n' or 'l' required, but not both
        :param L: size of interval, if provided, upper_bound must not be set
        :param w: weight, number of overlapping bins per point, number of bits set
        :param lower_bound: lower bound of interval, default '0'
        :param upper_bound: upper bound of interval, if provided, 'L' must not be set
        :param clamped_input: if True, input out-of-interval is rounded to nearest bound
        :param raise_out_of_bounds: if True, raise exception if input out-of-interval
        """

        # superclass constructor
        super().__init__(**kwargs)

        # weight
        if not isinstance(w, int) or w < 1:
            raise Exception("Weight 'w' must be a positive integer")
        else:
            self.w = w

        # interval size and bounds
        self.lower_bound = lower_bound
        if upper_bound is not None:
            if upper_bound <= lower_bound:
                raise Exception(
                        "upper_bound %0.2f should be greater than lower_bound %0.2f" % (upper_bound, lower_bound))
            # upper bound provided, so arg 'L' is ignored
            self.upper_bound = upper_bound
            self.L = self.upper_bound - self.lower_bound
        else:
            # upper bound not provided, so is computed from arg 'L'
            self.L = L
            self.upper_bound = self.lower_bound + self.L

        self.input_width = self.upper_bound - self.lower_bound

        # number and size of bins
        if n is None and l is not None:
            if l <= 0 or l > self.L:
                raise Exception("Bin size 'l' must be greater than 0, but less than 'L'.")
        elif n is not None and l is None:
            if not isinstance(n, int) or n < 1:
                raise Exception("Number of bins 'n' must be positive integer.")
        else:
            raise Exception("For arguments 'n' and 'l', one and only one must be provided.")

        # number of bins
        self.n = 0

        # bins
        self.bins = []

        # sizes of bins
        self.bin_sizes = []

        # region boundaries
        self.region_boundaries = []

        # region centroids
        self.region_centers = []

        # region encodings
        self.region_codes = []

        # weight of region codes
        self.region_weights = []

        # number of boundary crossings at each region boundary
        self.region_deltas = []

        self.n = n
        self.l = l

        self.config()

    @profile
    def encode(self, X):
        """
        transform one or many values from the input domain into the output encoding

        :return:
        """

        X = self._input(X)

        # list of values to encode
        if isinstance(X, Iterable):
            gnomes = []
            for x in X:
                gnomes.append(np.array([1 if x in b else 0 for b in self.bins]))
            return np.array(gnomes)
        else:
            gnome = np.array([1 if X in b else 0 for b in self.bins])
            return gnome


class _PeriodicEncoder(_EncoderBase):
    """
    collection of periodic, grid-like bins within a specified input interval
    - Encoder Type Options
        - grid cell

    # TODO: create variants with different distributions of offset, periods, and bin sizes, either uniform or random

    # TODO: bin sizes must be less than region period, distribute either by fraction of region, absolute size,
    # TODO: or bin size drives region period

    # TODO: offset = where in fund. region the center of the bin is situated
    # TODO: origin = where the lower bound of the fundamental region is located
    # TODO: period = length of fundamental region
    # TODO: bin_size = length of bin, less than period
    # TODO: duty_cycle = percent of region that bin fills

    # TODO: types of distribution
    # TODO: n samples between min and max of values using some random distribution
    # TODO: linear uniform distribution of n values between min and max
    # TODO: vary periods but constant bin size, or vice versa

    """

    # base periodic encoder
    def __init__(self, lower_bound=0.0, upper_bound=1.0, xmin=0.0, xmax=1.0, **kwargs):
        """
        :param lower_bound: lower bound of interval, default '0'
        :param upper_bound: upper bound of interval, default '1'
        :param xmin: lower bound of input range, default '0'
        :param xmax: upper bound of input range, default '1'
        """

        # superclass constructor
        super().__init__(oob_method="silent", **kwargs)

        # view size and bounds
        if xmax <= xmin:
            raise Exception("xmax %0.2f should be greater than xmin %0.2f" % (xmax, xmin))

        self.xmin = xmin
        self.xmax = xmax

        # interval size and bounds
        if upper_bound <= lower_bound:
            raise Exception("upper_bound %0.2f should be greater than lower_bound %0.2f" % (upper_bound, lower_bound))

        # bounds here refer to the pre-configured input range and are not hard stops on the encoder capability.
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.input_width = self.upper_bound - self.lower_bound

        # number of bins
        self.n = 0

        # periods
        self.periods = []

        # origins for starting point of each period, analogous to phase offset
        self.origins = []

        # bins
        self.bins = []

        # sizes of bins
        self.bin_sizes = []

        # whether bin straddles the boundaries of their fundamental region
        self.straddles = []

        # fundamental regions
        self.fund_regions = []

        # congruent bins
        self.bin_congruence = []

        # region boundaries
        self.region_boundaries = []

        # region centroids
        self.region_centers = []

        # region encodings
        self.region_codes = []

        # weight of region codes
        self.region_weights = []

        # number of boundary crossings at each region boundary
        self.region_deltas = []

    @profile
    def _is_x_in_periodic_bin(self, x_input, origin, period, b, is_straddle):

        # TODO: optimize this bin-checking calculation
        # TODO: create two arrays, one for upper bounds, and one for lower bounds

        # x_region = np.mod(x_input-origin, period) + origin
        # x1 = x_region
        # x2 = x_region + period
        # bl = b.lower
        # bu = b.upper
        # is_in_bin = (x1 >= bl and x1 < bu)
        #                or (is_straddle and (x2 >= bl and x2 < bu))
        # return is_in_bin

        # value with respect to fund. region origin
        x_offset = x_input - origin

        # values modulo a period
        x_modulo = np.mod(x_offset, period)

        # back into real coordinates within fund. region
        x_region = x_modulo + origin

        if x_region in b:
            return True

        # if this bin overlaps upper boundary of its fundamental region, check near the lower boundary too
        elif is_straddle and (x_region + period) in b:
            return True
        else:
            return False

    @profile
    def _generate_periodic_features(self, xmin, xmax, bins, periods):

        # xmin, xmax, bins, periods
        n = len(bins)
        bin_sizes = [b.length for b in bins]

        # generating congruent bins
        bin_congruence = []

        # multiply boundary points for each cell outside of fundamental region
        bin_lower_multiples = []
        for k in range(n):
            bin_multiples = []
            b = bins[k]
            x_lower = b.lower

            x_lower = x_lower + periods[k]
            while x_lower < xmax:
                x_upper = x_lower + bin_sizes[k]
                if x_upper > xmax:
                    x_upper = xmax
                bin_multiples.append((x_lower, x_upper))
                x_lower = x_lower + periods[k]

            x_upper = b.upper
            x_upper = x_upper - periods[k]
            while x_upper >= xmin:
                x_lower = x_upper - bin_sizes[k]
                if x_lower < xmin:
                    x_lower = xmin
                bin_multiples.append((x_lower, x_upper))
                x_upper = x_upper - periods[k]

            # copy congruent bins without original
            congruent_bins = []
            for cong_bounds in bin_multiples:
                congruent_bins.append(I.closed_open(cong_bounds[0], cong_bounds[1]))

            congruent_bins = sorted(congruent_bins)

            bin_congruence.append(congruent_bins)

            # add original
            x_lower = b.lower
            x_upper = b.upper
            if x_upper > xmax:
                x_upper = xmax
            if x_lower < xmin:
                x_lower = xmin
            bin_multiples.append((x_lower, x_upper))

            bin_multiples = sorted(bin_multiples)

            # add to complete collection of bins
            bin_lower_multiples += bin_multiples

        region_boundaries = np.array(bin_lower_multiples)

        # record region boundary points
        region_boundaries = np.concatenate(region_boundaries)
        region_boundaries = np.concatenate(([xmin], region_boundaries, [xmax]))
        region_boundaries = np.sort(region_boundaries)

        sorted_boundaries = region_boundaries

        # find pairs of boundary points that are near enough to each other to be considered identical
        # remove these as duplicates and merge delta counts
        unique_boundaries = []
        boundary_groups = []

        # find groups of near boundaries
        j = 0
        while j < len(sorted_boundaries):
            boundary_group = [j]
            last_k = j + 1
            for k in range(j + 1, len(sorted_boundaries)):
                bound_diff = abs(sorted_boundaries[j] - sorted_boundaries[k])

                if bound_diff < 0.001:
                    boundary_group.append(k)
                else:
                    break

                # last_k set here to handle both break termination and end-of-array termination
                last_k = k + 1

            boundary_groups.append(boundary_group)
            j = last_k

        # merge groups into single boundaries
        for boundary_group in boundary_groups:
            # print("group:", boundary_group)

            # singleton
            if len(boundary_group) == 1:
                index = boundary_group[0]
                min_key = sorted_boundaries[index]
                unique_boundaries.append(min_key)

            # multiple boundaries to be merged
            else:
                # find val with smallest number of digits
                min_index = -1
                min_count = 1e100
                for index in boundary_group:
                    float_val = sorted_boundaries[index]
                    char_count = len(str(float_val))
                    if char_count < min_count:
                        min_count = char_count
                        min_index = index
                min_key = sorted_boundaries[min_index]

                # create smallest digit boundary value
                unique_boundaries.append(min_key)

        unique_boundaries = np.array(unique_boundaries)

        return bin_congruence, unique_boundaries

    @profile
    def encode(self, X):
        """
        transform one or many values from the input domain into the output encoding

        :return:
        """

        # check well-formed and handle out-of-bounds conditions
        _X = self._input(X)

        # list of values to encode
        if isinstance(_X, Iterable):
            gnomes = []
            for x in _X:
                gnome = np.array(
                        [int(self._is_x_in_periodic_bin(x, self.origins[k], self.periods[k],
                                                        self.bins[k],
                                                        self.straddles[k]))
                         for k in range(self.n)])
                gnomes.append(gnome)
            return np.array(gnomes)
        else:
            gnome = np.array(
                    [int(self._is_x_in_periodic_bin(_X, self.origins[k], self.periods[k],
                                                    self.bins[k],
                                                    self.straddles[k])) for k in range(self.n)])
            return gnome


class PeriodicCellEncoder(_PeriodicEncoder):
    """
    collection of periodic, grid-like bins within a specified input interval
    - Encoder Type Options
        - grid cell

    # TODO: create variants with different distributions of offset, periods, and bin sizes, either uniform or random

    # TODO: bin sizes must be less than region period, distribute either by fraction of region, absolute size,
    # TODO: or bin size drives region period

    # TODO: offset = where in fund. region the center of the bin is situated
    # TODO: origin = where the lower bound of the fundamental region is located
    # TODO: period = length of fundamental region
    # TODO: bin_size = length of bin, less than period
    # TODO: duty_cycle = percent of region that bin fills

    # TODO: types of distribution
    # TODO: n samples between min and max of values using some random distribution
    # TODO: linear uniform distribution of n values between min and max
    # TODO: vary periods but constant bin size, or vice versa

    """

    def __init__(self, n=1, l=None, min_period=None, max_period=None,
                 **kwargs):
        """

        :param n: number of bins, number of bits
        :param l: size of bin, if unspecified, l is random for each bin
        :param min_period:
        :param max_period:
        :param kwargs:
        """

        # superclass constructor
        super().__init__(**kwargs)

        # size of bins
        self.l_frac = 0.25

        if l is not None:
            if l <= 0 or l > self.input_width:
                raise Exception("Bin size 'l' must be greater than 0, but less than 'L'.")
            self.min_l = l - 1e-100
            self.max_l = l + 1e-100
            # self.l = l
        else:
            self.min_l = self.input_width * 0.05
            self.max_l = self.input_width * 0.10
            # 5% of size of input interval

        # number of bins
        if not isinstance(n, int) or n < 1:
            raise Exception("Number of bins 'n' must be positive integer.")
        self.n = n

        # max period 50% of input interval
        self.max_period = max_period
        if self.max_period is None:
            self.max_period = 0.5 * self.input_width

        self.min_period = min_period
        if self.min_period is None:
            self.min_period = self.min_l

        # check max and min period constraints
        if self.max_period <= self.min_period:
            raise Exception("Max period must be greater than min period")

        if self.max_period <= 0 or self.min_period <= 0:
            raise Exception("Period max and min must be positive")

        # origin mid-point of input interval
        self.origin = self.lower_bound + self.input_width / 2.0
        self.origins = [self.origin for _ in range(self.n)]

        # modulus of grid cell, period
        self.periods = np.linspace(self.min_period, self.max_period, self.n)

        # fundamental regions for each period
        self.fund_regions = [I.closed_open(self.origin, self.origin + self.periods[c]) for c in range(self.n)]

        # sizes of bins
        region_frac = np.repeat(self.l_frac, self.n)
        self.bin_sizes = np.multiply(region_frac, self.periods)

        # create n random points in interval as bin centroids
        bin_lowers = self.rng.uniform(self.origin, self.origin + self.periods, self.n)

        # True/False whether bin straddles fund. region boundary
        # whether bin straddles the boundaries of their fundamental region
        self.straddles = np.array(
                [False if (bin_lowers[k] + self.bin_sizes[k]) in self.fund_regions[k] else True for k in range(self.n)])

        # compute bins in their fundamental regions
        self.bins = [I.closed_open(bin_lowers[k], bin_lowers[k] + self.bin_sizes[k]) for k in range(0, self.n)]

        if len(self.bins) < 1:
            raise Exception("Encoder as configured doesn't allocate any bins")

        self.bin_congruence, self.region_boundaries = self._generate_periodic_features(self.xmin,
                                                                                       self.xmax, self.bins,
                                                                                       self.periods)
        #self.bin_congruence, self.region_boundaries = self._generate_periodic_features(self.lower_bound,
        #                                                                               self.upper_bound, self.bins,
        #                                                                               self.periods)

        # record region center points
        self.region_centers = self.region_boundaries[:-1] + np.diff(self.region_boundaries) / 2

        # unique regions intersected by combinations of bins
        self.regions = [I.closed_open(self.region_boundaries[i], self.region_boundaries[i + 1]) for i in
                        range(0, len(self.region_boundaries) - 1)]

        self.region_sizes = np.diff(self.region_boundaries) / 2

        self.region_codes = self.encode(self.region_centers)

        self.region_weights = np.count_nonzero(self.region_codes, axis=1)

        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]

        deltas = []
        for k in range(1, len(self.region_codes)):
            w0 = self.region_codes[k - 1]
            w1 = self.region_codes[k]
            hdist = np.count_nonzero(w1 != w0)
            deltas.append(hdist)

        # number of boundary crossings at each boundary point
        self.region_deltas = np.concatenate(
                ([self.region_weights[0]], deltas, [self.region_weights[-1]]))

        # print("boundaries:", len(self.region_boundaries))
        # print(self.region_boundaries)
        # print("deltas:", len(self.region_deltas))
        # print(self.region_deltas)


class PeriodicScalarEncoder(_PeriodicEncoder):

    def __init__(self, n=8, w=1, period=0.5, **kwargs):
        """
        1 period, multiple bins

        :param n: (int) number of bins to divide the period into
        :param periods: (array-like or float) length(s) of cyclic period
        """

        # superclass constructor
        super().__init__(**kwargs)

        # weight
        if not isinstance(w, int) or w < 1:
            raise Exception("Weight 'w' must be a positive integer")
        else:
            self.w = w

        # number of bins
        if not isinstance(n, int) or n < 1:
            raise Exception("Number of bins 'n' must be positive integer.")
        self.n = n

        if not (isinstance(period, float) or isinstance(period, int)) or period <= 0 or period > self.input_width:
            raise Exception("Period must be positive number and less than the input range size")

        self.period = period

        # origins are mid-point of input range
        # self.origins = [self.lower_bound + self.input_width / 2.0 for k in range(self.n)]

        # origins are lower bound of input range
        self.origins = [self.lower_bound for _ in range(self.n)]

        # fixed modulus for each grid cell
        self.periods = np.repeat(self.period, self.n)

        # fundamental regions for each period (NOTE: should all be identical)
        self.fund_regions = [I.closed_open(self.origins[k], self.origins[k] + self.periods[k]) for k in range(self.n)]

        # bin sizes are period divided into n equal regions
        self.bin_sizes = np.repeat(self.w * self.period / self.n, self.n)

        # starting point for each bin (NOTE: periods should all be identical)
        bin_lowers = [self.origins[k] + self.periods[k] * float(k) / self.n for k in range(self.n)]

        # True/False whether bin straddles fund. region boundary
        self.straddles = np.array(
                [False if (bin_lowers[k] + self.bin_sizes[k]) in self.fund_regions[k] else True for k in range(self.n)])

        # compute bins in their fundamental regions
        self.bins = [I.closed_open(bin_lowers[k], bin_lowers[k] + self.bin_sizes[k]) for k in range(0, self.n)]

        # region boundaries and congruent bins
        self.bin_congruence, self.region_boundaries = self._generate_periodic_features(self.xmin,
                                                                                       self.xmax, self.bins,
                                                                                       self.periods)
        #self.bin_congruence, self.region_boundaries = self._generate_periodic_features(self.lower_bound,
        #                                                                               self.upper_bound, self.bins,
        #                                                                               self.periods)

        # record region center points
        self.region_centers = self.region_boundaries[:-1] + np.diff(self.region_boundaries) / 2

        # unique regions intersected by combinations of bins
        self.regions = [I.closed_open(self.region_boundaries[i], self.region_boundaries[i + 1]) for i in
                        range(0, len(self.region_boundaries) - 1)]

        # size of unique regions
        self.region_sizes = np.diff(self.region_boundaries) / 2

        # encoding for each region
        self.region_codes = self.encode(self.region_centers)

        # weight for each region
        self.region_weights = np.count_nonzero(self.region_codes, axis=1)

        # sparse indices of encoding for each region
        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]

        deltas = []
        for k in range(1, len(self.region_codes)):
            w0 = self.region_codes[k - 1]
            w1 = self.region_codes[k]
            hdist = np.count_nonzero(w1 != w0)
            deltas.append(hdist)

        # number of boundary crossings at each boundary point
        self.region_deltas = np.concatenate(
                ([self.region_weights[0]], deltas, [self.region_weights[-1]]))

        # print("boundaries:", len(self.region_boundaries))
        # print(self.region_boundaries)
        # print("deltas:", len(self.region_deltas))
        # print(self.region_deltas)


class _PlaceCellEncoder(_EncoderBase):
    """
    arbitrary collection of single bins in a specified input domain
    - Encoder Type Options
        - place cell

    """

    def __init__(self, n=1, l=None, lower_bound=0, upper_bound=1, **kwargs):
        """
        :param n: number of bins, number of bits
        :param l: size of bin, if unspecified, l is random for each bin
        :param lower_bound: lower bound of interval, default '0'
        :param upper_bound: upper bound of interval, default '1'
        :param clamped_input: if True, input out-of-interval is rounded to nearest bound
        :param raise_out_of_bounds: if True, raise exception if input out-of-interval
        """

        # superclass constructor
        super().__init__(**kwargs)

        # interval size and bounds
        if upper_bound <= lower_bound:
            raise Exception("upper_bound %0.2f should be greater than lower_bound %0.2f" % (upper_bound, lower_bound))
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.L = self.upper_bound - self.lower_bound

        # size of bins
        if l is not None:
            if l <= 0 or l > self.L:
                raise Exception("Bin size 'l' must be greater than 0, but less than 'L'.")
            self.l = l
        else:
            # 10% of size of input interval
            self.l = self.L * 0.1

        # number of bins
        if not isinstance(n, int) or n < 1:
            raise Exception("Number of bins 'n' must be positive integer.")
        self.n = n

        self.bins = []
        self.region_boundaries = []
        self.region_centers = []
        self.region_codes = []
        self.region_weights = []
        self.region_deltas = []

        self.config()

    def encode(self, X):
        """
        transform one or many values from the input domain into the output encoding

        :return:
        """

        # enforces well-formed input with options,
        # X = check_array(X, ensure_2d=True)

        # here input should be 2D array where X.shape == (num_samples, num_features)
        X = self._input(X)

        # list of values to encode
        if isinstance(X, Iterable):
            gnomes = []
            for x in X:
                gnomes.append(np.array([1 if x in b else 0 for b in self.bins]))
            return np.array(gnomes)
        else:
            gnome = np.array([1 if X in b else 0 for b in self.bins])
            return gnome


class RandomizedPlaceCellEncoder(_PlaceCellEncoder):

    def config(self):
        """
        - create n random bins in specified interval

        :return:
        """

        rand = self.rng

        # create n random points in interval as bin centroids
        bin_centers = rand.uniform(self.lower_bound, self.upper_bound, self.n)

        # compute bins
        self.bins = [I.closed_open(bin_centers[c] - self.l / 2.0, bin_centers[c] + self.l / 2.0) for c
                     in range(0, self.n)]

        if len(self.bins) < 1:
            raise Exception("Encoder as configured doesn't allocate any bins")

        # record region boundary points
        get_boundaries = lambda x: (
                np.maximum(x - self.l / 2.0, self.lower_bound), np.minimum(x + self.l / 2.0, self.upper_bound))
        region_boundaries = get_boundaries(bin_centers)
        region_boundaries = np.concatenate(region_boundaries)
        region_boundaries = np.concatenate(([self.lower_bound], region_boundaries, [self.upper_bound]))
        region_boundaries = np.sort(region_boundaries)
        self.region_boundaries = region_boundaries

        # record region center points
        self.region_centers = self.region_boundaries[:-1] + np.diff(self.region_boundaries) / 2

        # unique regions intersected by combinations of bins
        self.regions = [I.closed_open(self.region_boundaries[i], self.region_boundaries[i + 1]) for i in
                        range(0, len(self.region_boundaries) - 1)]

        self.region_sizes = np.diff(self.region_boundaries) / 2

        self.region_codes = self.encode(self.region_centers)

        self.region_weights = np.count_nonzero(self.region_codes, axis=1)

        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]

        # self.region_deltas = np.concatenate(
        #        ([self.region_weights[0]], np.abs(np.diff(self.region_weights)), [self.region_weights[-1]]))

        deltas = []
        for k in range(1, len(self.region_codes)):
            w0 = self.region_codes[k - 1]
            w1 = self.region_codes[k]
            hdist = np.count_nonzero(w1 != w0)
            deltas.append(hdist)

        # number of boundary crossings at each boundary point
        self.region_deltas = np.concatenate(
                ([self.region_weights[0]], deltas, [self.region_weights[-1]]))


class FixedWeightEncoder(_IntervalEncoder):

    def config(self):
        """
        - compute 'n' or 'l' depending on which is unspecified
        - compute step_size, distance between the minimum boundaries of consecutive bins (DERIVED)

        We define the equations as follows:
        - for fixed weight, overlapping bins, imbricating code
            - w=1: l=L/n
            - w>1: l=(w*L)/(n-w+1)

        # Compute either 'l' or 'n', algebra to show formula
        l=(w*L)/(n-w+1)
        (n-w+1)*l = w*L
        n*l-w*l+l = w*L
        n*l = w*L + w*l - l
        n = (w*L + w*l - l) / l
        n = w*L/l + w - 1

        :return:
        """

        if self.n is None:
            self.n = (self.w * self.L) / self.l + self.w - 1
        else:
            self.l = (self.w * self.L) / (self.n - self.w + 1)

        # INVARIANT: n >= 2w
        if 2 * self.w > self.n:
            raise Exception("n=%d,w=%d does not satisfy condition n > 2w" % (self.n, self.w))

        # compute step size for subsequent bins
        num_partitions = self.n - (self.w - 1)
        self.step_size = self.L / num_partitions

        # internal bin-boundary transition points
        equidist_points = np.linspace(self.lower_bound, self.upper_bound, endpoint=True, num=num_partitions + 1)

        # record region boundary points
        self.region_boundaries = equidist_points

        # record region center points
        self.region_centers = self.region_boundaries[:-1] + np.diff(self.region_boundaries) / 2

        bin_steps = list(equidist_points)

        self.bins = []
        self.bins = [I.closed_open(bin_steps[0], bin_steps[c]) for c in range(1, self.w)]
        self.bins += [I.closed_open(bin_steps[c], bin_steps[c + self.w]) for c in range(0, len(bin_steps) - self.w)]
        self.bins += [I.closed_open(bin_steps[c], bin_steps[-1]) for c in
                      range(len(bin_steps) - self.w, len(bin_steps) - 1)]

        if len(self.bins) < 1:
            raise Exception("Encoder as configured doesn't allocate any bins")

        # unique regions intersected by combinations of bins
        self.regions = [I.closed_open(self.region_boundaries[i], self.region_boundaries[i + 1]) for i in
                        range(0, len(self.region_boundaries) - 1)]

        self.region_sizes = [self.step_size, ] * len(self.region_centers)
        self.region_codes = self.encode(self.region_centers)
        self.region_weights = np.count_nonzero(self.region_codes, axis=1)
        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]
        self.region_deltas = np.ones(len(self.region_boundaries), dtype=int)
        self.region_deltas[0] = self.w
        self.region_deltas[-1] = self.w


class TaperingWeightEncoder(_IntervalEncoder):

    def config(self):
        """
        - compute 'n' or 'l' depending on which is unspecified
        - compute step_size, distance between the minimum boundaries of consecutive bins (DERIVED)

        We define the equations as follows:
        - for tapering weight, all bins proper subset of interval
            - w=1: l=L/n
            - w>1: l=(w*L)/(n+w-1)

        # Compute either 'l' or 'n', algebra to show formula
        l=(w*L)/(n+w-1)
        (n+w-1)*l = w*L
        n*l+w*l-l = w*L
        n*l = w*L - w*l + l
        n = (w*L - w*l + l) / l
        n = w*L/l - w + 1

        :return:
        """

        if self.n is None:
            self.n = (self.w * self.L) / self.l - self.w + 1
        else:
            self.l = (self.w * self.L) / (self.n + self.w - 1)

        # INVARIANT: n >= 2w
        if 2 * self.w > self.n:
            raise Exception("n=%d,w=%d does not satisfy condition n > 2w" % (self.n, self.w))

        # compute step size for subsequent bins
        num_partitions = self.n + self.w - 1
        self.step_size = self.L / num_partitions

        # internal bin-boundary transition points
        equidist_points = np.linspace(self.lower_bound, self.upper_bound, endpoint=True, num=num_partitions + 1)

        # record region boundary points
        self.region_boundaries = equidist_points

        # record region center points
        self.region_centers = self.region_boundaries[:-1] + np.diff(self.region_boundaries) / 2

        bin_steps = list(equidist_points)
        self.bins = [I.closed_open(bin_steps[c], bin_steps[c + self.w]) for c in range(0, len(bin_steps) - self.w)]

        if len(self.bins) < 1:
            raise Exception("Encoder as configured doesn't allocate any bins")

        # unique regions intersected by combinations of bins
        self.regions = [I.closed_open(self.region_boundaries[i], self.region_boundaries[i + 1]) for i in
                        range(0, len(self.region_boundaries) - 1)]

        self.region_sizes = [self.step_size, ] * len(self.region_centers)
        self.region_codes = self.encode(self.region_centers)
        self.region_weights = np.count_nonzero(self.region_codes, axis=1)
        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]
        self.region_deltas = np.ones(len(self.region_boundaries), dtype=int)
