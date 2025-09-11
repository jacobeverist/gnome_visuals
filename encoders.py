from collections.abc import Iterable

from intervals import FloatInterval as I
from line_profiler_pycharm import profile
import numpy as np

# Scikit-Learn's numpy array input validation and reformatting that we've found useful in the past
# #from sklearn.utils.validation import check_X_y, check_array

__all__ = ["_EncoderBase", "_IntervalEncoder", "_PlaceCellEncoder", "_PeriodicEncoder"] \
          + ["MultiEncoder", ] + ["RandomizedPlaceCellEncoder", "PlaceCellEncoder"] + ["FixedWeightEncoder",
                                                                                       "TaperingWeightEncoder"] \
          + ["PeriodicCellEncoder", "PeriodicScalarEncoder"]


# abstract superclass of all encoders
class _EncoderBase:
    """
    Base class for encoding numerical data.

    This class defines the framework for encoding input data values within a bounded
    interval. It includes functionality for handling out-of-bound values according to
    various predefined methods. The class is designed to be extensible for specialized
    encodings through subclassing.

    Attributes:
        oob_method (str): Specifies how out-of-bound values are handled. Supported values are
            "clamp", "exception", "modulo", and "silent".
        lower_bound (float): Minimum value of the input domain.
        upper_bound (float): Maximum value of the input domain.
        input_width (float): Width of the input domain, calculated as the difference
            between `upper_bound` and `lower_bound`.
        rng (np.random.RandomState): Random number generator used for obtaining random
            values, initialized with the provided seed or a default random state.

    Variants:
    - bounded or unbounded input domain
    - single or repeated input domain regions (receptive field)
    - input region defined by Bravais lattice: 1) point unit ball or 2) primitive unit cell
    - encoding of input domain is 1) partition, 2) covering, 3) packing, or 4) sampling (overlaps + gaps)


    """

    def __init__(self, oob_method="silent", lower_bound=0.0, upper_bound=1.0, seed=None):
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
    """A class representing a Multi-Encoder to combine multiple encoder configurations.

    MultiEncoder supports managing and configuring multiple sub-encoders within a unified framework.
    It accounts for view bounds, input bounds, and generates regions for encoding purposes. Users can
    define boundaries, centers, and weights of regions for a variety of applications involving
    multidimensional encoding. This class facilitates the computation of concatenated encodings
    and supports dynamic reconfiguration of sub-encoders.

    Attributes:
        encoders (list): List of sub-encoders used within MultiEncoder.
        w (int): Width configuration parameter used in region processing.
        l (float): Length configuration parameter defining certain encoder constraints.
        n (int): Total count of bins across all sub-encoders.
        xmin (float|None): Minimum view boundary for encoding values.
        xmax (float|None): Maximum view boundary for encoding values.
        x_pad (float|None): Additional padding applied to view boundaries.
        lower_bound (float|None): Minimum allowable input range derived from sub-encoders.
        upper_bound (float|None): Maximum allowable input range derived from sub-encoders.
        L (floaT|None): Total span between the lower and upper bounds of input values.
        region_boundaries (list): Boundaries defining unique regions in encoding.
        region_centers (list): Centers of each encoding region.
        region_codes (list): Encoded values corresponding to region centers.
        region_weights (list): Relative weights of regions based on encoding.
        region_deltas (list): Differences between sequential region boundaries.
        bins (list): All bins consolidated from sub-encoders.
        regions (list): Unique regions intersected by bins from sub-encoders.
        region_sizes (list): Sizes of regions based on differences in boundaries.
        region_indices (list): Indices of active regions based on encoding results.
        is_init (bool): Indicates if the MultiEncoder has been properly initialized.
    """
    def __init__(self, xmin=None, xmax=None, x_pad=None, **kwargs):

        # superclass constructor
        super().__init__(**kwargs)

        self.encoders = []

        self.w = 3
        self.l = 0.1
        self.n = 0

        # view size and bounds
        if xmax is not None and xmin is not None:
            if xmax <= xmin:
                raise Exception("xmax %0.2f should be greater than xmin %0.2f" % (xmax, xmin))

        self.xmin = xmin
        self.xmax = xmax
        self.x_pad = x_pad

        # bounds here refer to the pre-configured input range and are not hard stops on the encoder capability.
        self.lower_bound = None
        self.upper_bound = None

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

    def set_view(self, xmin, xmax):

        if xmax <= xmin:
            raise Exception("xmax %0.2f should be greater than xmin %0.2f" % (xmax, xmin))

        self.xmin = xmin
        self.xmax = xmax

        # recompute all regions
        self.config()

    def set_x_pad(self, x_pad):
        self.x_pad = x_pad

        # recompute all regions
        self.config()

    @profile
    def add_encoder(self, encoder):
        self.encoders.append(encoder)
        self.config()

    @profile
    def config(self):

        # computer lower_bound and upper_bound
        self.compute_input_bounds()

        # if not already set, generate xmin and xmax
        self.compute_view_bounds()

        self.L = self.compute_L()
        self.n = self.compute_n()

        # each subencoder view should be bounded by the greater of view bounds and input bounds
        xmax = self.xmax if self.xmax > self.upper_bound else self.upper_bound
        xmin = self.xmin if self.xmin < self.lower_bound else self.lower_bound

        # if periodic encoder, recompute regions with new bounds
        for encoder in self.encoders:

            try:
                # set new view parameters
                if encoder.xmin > xmin or encoder.xmax < xmax:
                    try:
                        encoder.set_view(xmin, xmax)
                    except AttributeError:
                        encoder.xmin = xmin
                        encoder.xmax = xmax
            except AttributeError:
                # xmin/xmax don't exist
                pass

            # generate regions with new view
            try:
                encoder.generate_regions()
            except AttributeError:
                pass

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

    def compute_view_bounds(self):

        if self.xmax is None:
            self.xmax = self.upper_bound

        if self.xmin is None:
            self.xmin = self.lower_bound

        if self.x_pad is not None:
            self.xmax = max(self.upper_bound + self.x_pad, self.xmax)
            self.xmin = min(self.lower_bound - self.x_pad, self.xmin)

    def compute_input_bounds(self):
        upper_bound = max([self.encoders[k].upper_bound for k in range(len(self.encoders))])
        lower_bound = min([self.encoders[k].lower_bound for k in range(len(self.encoders))])

        if self.upper_bound is None or upper_bound > self.upper_bound:
            self.upper_bound = upper_bound

        if self.lower_bound is None or lower_bound < self.lower_bound:
            self.lower_bound = lower_bound

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
    Encodes numeric values into overlapping binary representations using interval
    boundaries and specified encoding configurations.

    This class is used to transform numeric inputs into a binary encoded output
    based on specified intervals (bins). Either the number of bins ('n') or the
    size of each bin ('l') must be specified, but not both. Interval boundaries
    and encoding rules can be customized as required.

    Attributes:
        n (int): Number of bins used in the encoding process. Applicable if 'l'
            is not provided.
        l (float): Size of each bin in the encoding process. Applicable if 'n'
            is not provided.
        L (float): Total size of the interval domain.
        w (int): Number of overlapping bins per encoded point.
        lower_bound (float): The lower bound of the interval domain.
        upper_bound (float or None): The upper bound of the interval domain.
        input_width (float): The total width of the input interval.
        bins (list): List of bins representing the defined intervals.
        bin_sizes (list): Sizes of individual bins.
        regions (list): Interval-based regions.
        region_centers (list): Centroid values for each region.
        region_sizes (list): Size of each region.
        region_indices (list): Indices of regions.
        region_boundaries (list): Boundaries of each region.
        region_codes (list): Encoded binary representation for each region.
        region_weights (list): Binary weights associated with each encoded region.
        region_deltas (list): Number of boundary crossings at each region's boundary.


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

        # regions as intervals
        self.regions = []

        # region centroids
        self.region_centers = []

        # region sizes
        self.region_sizes = []

        # region indices
        self.region_indices = []

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
    """Base periodic encoder.

    This class provides a mechanism for encoding continuous periodic features into a numerical
    representation suitable for machine learning models. Encodings divide the range of values into bins
    and regions based on periodic cycles, allowing operations that benefit from understanding periodic
    properties. The implementation accommodates flexible intervals, customizable boundaries, and various
    bins and periods for processing data. It ensures that congruent bins are properly handled, and boundaries
    are managed efficiently. Initializes and manages internal structures relevant for encoding while providing
    functionalities to compute and retrieve regions for the encoded input.

    Attributes:
        xmin (float): Lower bound of the input range.
        xmax (float): Upper bound of the input range.
        lower_bound (float): Lower bound of the interval for encoding.
        upper_bound (float): Upper bound of the interval for encoding.
        input_width (float): Width of the interval for encoding.
        n (int): Number of bins used in the encoding.
        periods (list): List of periods defining the repeating intervals for encoding.
        origins (list): List of origins for the starting point of each period.
        bins (list): List of bins used in the encoder.
        bin_sizes (list): List containing sizes of each bin.
        straddles (list): Specifies whether each bin straddles the boundaries of their fundamental region.
        fund_regions (list): Fundamental regions associated with each bin and period configuration.
        bin_congruence (list): Collection of congruent bins including multiples outside the fundamental regions.
        region_boundaries (list): Boundaries that partition the space into unique regions for encoding.
        region_centers (list): Centroids or middle points of computed regions.
        regions (list): Intervals representing unique regions derived from bins, boundaries, and congruences.
        region_sizes (list): Sizes of the unique regions in the encoding schema.
        region_codes (list): Encoded values associated with each unique region.
        region_weights (list): Weight of region codes computed from active encoded values.
        region_indices (list): Sparse indices of encoding elements for each region.
        region_deltas (list): Number of boundary crossings at each region boundary.

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

        # regions as intervals
        self.regions = []

        # region sizes
        self.region_sizes = []

        # region encodings
        self.region_codes = []

        # weight of region codes
        self.region_weights = []

        # region indices
        self.region_indices = []

        # number of boundary crossings at each region boundary
        self.region_deltas = []

    def generate_regions(self):

        # region boundaries and congruent bins
        self.bin_congruence, self.region_boundaries = self._generate_periodic_features(self.xmin,
                                                                                       self.xmax, self.bins,
                                                                                       self.periods)

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
    Encodes input data into periodic bins based on given parameters.

    The PeriodicCellEncoder class provides functionality for creating and
    managing periodic bins within a specified interval. It allows for the
    division of the input space into discrete bins (fundamental regions)
    using configurable parameters such as bin size, number of bins, periods,
    and origins. It also supports random or fixed placement of bins.

    Attributes:
        l_frac (float): Fraction of the period used for bin size calculation.
        min_l (float): Minimum allowed bin size within the input interval.
        max_l (float): Maximum allowed bin size within the input interval.
        n (int): Number of bins to divide the input interval into.
        max_period (float): Maximum period of the bins within the input interval.
        min_period (float): Minimum period of the bins within the input interval.
        period (float or None): Period of the bins if explicitly specified,
            otherwise calculated dynamically based on other inputs.
        origin (float): Origin point for bin placement within the input interval.
        origins (list[float]): List of origins for bin placements, either shared
            or randomly distributed based on configuration.
        periods (numpy.ndarray): Array of periods assigned to each bin.
        fund_regions (list): List of fundamental regions for each bin defined
            within the input interval.
        bin_sizes (numpy.ndarray): Array of sizes for each bin, calculated as a
            fraction of the period.
        straddles (numpy.ndarray): Boolean array indicating whether each bin
            straddles the boundaries of its fundamental region.
        bins (list): Finalized list of bins with their boundaries.


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

    def __init__(self, n=1, l=None, period=None, min_period=None, max_period=None,
                 origin=None, do_rand=False, **kwargs):
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

        self.period = period
        if self.period is not None:
            if not isinstance(self.period, (int, float)) or not self.period > 0.0:
                raise Exception("Period must be positive number")

        # origin mid-point of input interval
        if isinstance(origin, (float, int)) and (self.lower_bound <= origin <= self.upper_bound):
            self.origin = origin
        else:
            self.origin = self.lower_bound + self.input_width / 2.0

        if do_rand:
            # create random placements of bins within input interval
            self.origins = self.rng.uniform(self.lower_bound, self.upper_bound, self.n)
        else:
            # placements use the same origin
            self.origins = [self.origin for _ in range(self.n)]

        # modulus of grid cell, period
        if self.period is None:
            self.periods = np.linspace(self.min_period, self.max_period, self.n)
        else:
            self.periods = np.repeat(self.period, self.n)

        # fundamental regions for each period
        self.fund_regions = [I.closed_open(self.origins[c], self.origins[c] + self.periods[c]) for c in range(self.n)]

        # sizes of bins
        region_frac = np.repeat(self.l_frac, self.n)
        self.bin_sizes = np.multiply(region_frac, self.periods)

        # create n random points in interval as bin centroids
        # bin_lowers = self.rng.uniform(self.origin, self.origin + self.periods, self.n)
        # bin_lowers = np.array(self.origins) + self.periods - self.bin_sizes
        bin_lowers = np.array(self.origins)

        # True/False whether bin straddles fund. region boundary
        # whether bin straddles the boundaries of their fundamental region
        self.straddles = np.array(
                [False if (bin_lowers[k] + self.bin_sizes[k]) in self.fund_regions[k] else True for k in range(self.n)])

        # compute bins in their fundamental regions
        self.bins = [I.closed_open(bin_lowers[k], bin_lowers[k] + self.bin_sizes[k]) for k in range(0, self.n)]

        if len(self.bins) < 1:
            raise Exception("Encoder as configured doesn't allocate any bins")

        # generate all unique regions within xmin/xmax view
        self.generate_regions()


class PeriodicScalarEncoder(_PeriodicEncoder):
    """
    Represents a periodic scalar encoder used for encoding cyclic data into a set of bins.

    This encoder is designed to divide a cyclic period into multiple bins, enabling periodic input
    values to be mapped to discrete ranges or regions. It supports configuration of the number of bins,
    the weight per bin, and the length of the cyclic period. The class is aimed at handling periodic
    data effectively in scenarios requiring cyclic representations, such as date/time encodings or
    angles.

    Attributes:
        n (int): Number of bins into which the period is divided.
        w (int): Weight associated with each bin. Must be a positive integer.
        period (float): Length of the cyclic period. Must be a positive number and less than the input
            range size.
        origins (list): List containing the starting points of each bin in the input range.
        periods (numpy.ndarray): Repeated values of the period for each bin.
        fund_regions (list): Closed-open intervals representing fundamental regions for each bin.
        bin_sizes (numpy.ndarray): Sizes of individual bins, calculated based on the period and
            number of bins.
        straddles (numpy.ndarray): Boolean values indicating if a bin straddles the boundary of the
            fundamental region.
        bins (list): Closed-open intervals representing the bins in their respective fundamental regions.
    """
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

        # generate all unique regions within xmin/xmax view
        self.generate_regions()


class _PlaceCellEncoder(_EncoderBase):
    """
    arbitrary collection of single bins in a specified input domain
    - Encoder Type Options
        - place cell

    Represents a place cell encoder that transforms input values from a specified
    domain into an encoded representation using binning logic.

    This class is used for interval-based encoding where the input domain is
    divided into discrete bins. Each input value can be transformed into a binary
    representation based on whether it belongs to specific bins. Configurable
    parameters include the number of bins, bin size, interval bounds, and input
    constraints.

    Attributes:
        lower_bound (float): The lower bound of the interval for encoding. All
            input values are expected to be within the range [lower_bound,
            upper_bound].
        upper_bound (float): The upper bound of the interval for encoding. All
            input values are expected to be within the range [lower_bound,
            upper_bound].
        L (float): The size of the interval, calculated as upper_bound -
            lower_bound.
        l (float): The size of each bin for encoding. If not specified during
            initialization, it defaults to 10% of the interval size.
        n (int): The number of bins used for encoding. Represents the number of
            binary outputs.
        bins (list): A list representing the discrete bins defined over the input
            interval.
        regions (list): A list representing predefined regions within the
            encoding interval.
        region_sizes (list): A list of sizes corresponding to each region.
        region_boundaries (list): A list of boundary values for each region.
        region_centers (list): A list of center points for each region.
        region_codes (list): A list of binary codes corresponding to each region.
        region_indices (list): A list of indices mapping regions to specific bins.
        region_weights (list): A list of weights assigned to each region for
            encoding purposes.
        region_deltas (list): A list of differences or variances associated with
            each region.

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
        if not isinstance(n, int) or n < 0:
            raise Exception("Number of bins 'n' must be non-negative integer.")
        self.n = n

        self.bins = []
        self.regions = []
        self.region_sizes = []
        self.region_boundaries = []
        self.region_centers = []
        self.region_codes = []
        self.region_indices = []
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
    """
    Encodes spatial positions into a set of overlapping regions to facilitate discretization.

    The RandomizedPlaceCellEncoder class extends a base encoder and provides functionality for
    encoding spatial positions into randomly generated regions based on certain bounding intervals.
    This process is utilized for mapping continuous spatial data into discrete regions, which can
    be useful in applications such as machine learning and reinforcement learning.

    Attributes:
        bins (list[I.closed_open]): List of randomly generated bins representing continuous
            intervals within the specified bounds.
        region_boundaries (ndarray): Array of boundary points for the regions, sorted in
            ascending order.
        region_centers (ndarray): Array of center points for each region, calculated as the
            midpoints between region boundaries.
        regions (list[I.closed_open]): List of unique regions, represented as intervals
            intersected by combinations of the bins.
        region_sizes (ndarray): Array of half-differences between adjacent region boundary
            points, representing the size of each region.
        region_codes (ndarray): Encoded representation of all region centers, where codes
            represent active bins for a given center point.
        region_weights (ndarray): Count of active bins for each region center, indicating
            the frequency of region activation.
        region_indices (list[tuple]): List of tuples, where each tuple contains the indices of
            bins actively intersecting the corresponding region.
        region_deltas (ndarray): Number of boundary crossings for each region. Calculated based on
            changes observed in active bins between adjacent regions.
    """
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
        # def get_boundaries(x):
        #     return np.maximum(x - self.l / 2.0, self.lower_bound), np.minimum(x + self.l / 2.0, self.upper_bound)

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


class PlaceCellEncoder(_PlaceCellEncoder):
    """
    Represents a Place Cell Encoder for encoding spatial information based on structured place cell regions.

    This class allows the creation and modification of place cell regions, which are bounded spatial intervals
    representing receptive fields. It provides methods for adding new cells, reconfiguring the regions, and
    computing boundaries and related properties. Designed for computational models involving place cells and
    spatial navigation.

    Attributes:
        bins (list): A list of intervals defining the bins or receptive fields of place cells.
        region_boundaries (numpy.ndarray): Array of region boundary points derived from defined bins.
        region_centers (numpy.ndarray): Array of center points of the regions between boundaries.
        regions (list): List of intervals representing unique regions defined by combinations of bins.
        region_sizes (numpy.ndarray): Array of sizes for each region, computed using region boundaries.
        region_codes (numpy.ndarray): Encoded representation of the region center points.
        region_weights (numpy.ndarray): Weights or occurrences of non-zero elements per region.
        region_indices (list): Indices of non-zero elements for regions within the region code matrix.
        region_deltas (numpy.ndarray): Number of boundary crossings at each boundary point.
    """
    # def __init__(self, regions, **kwargs):
    #    """
    #    :param regions: list of intervals or 2-tuples that indicate bins/RFs of place cells
    #    """
    #     if isinstance(regions, list):
    #         pass
    #     else:
    #         if isinstance(regions, (I, tuple)):
    #             pass

    # make empty config
    def __init__(self, **kwargs):
        super().__init__(n=0, **kwargs)

    def config(self):
        """
        Empty config, do nothing to start

        :return:
        """
        pass

    def add_cell(self, lower, upper):
        """
        add a place cell

        :param lower:
        :param upper:
        :return:
        """
        # add as bin and recompute
        self.bins.append(I.closed_open(lower, upper))

        self.reconfigure()

    def reconfigure(self):
        """
        reconfigure with new cell

        :return:
        """

        bin_centers = np.array([b.lower + (b.upper-b.lower)/2.0 for b in self.bins])

        # print("bins:", self.bins)
        # print("bin_centers:", bin_centers)

        # self.region_boundaries, self.region_deltas = self.compute_boundaries()

        # record region boundary points
        # def get_boundaries(x):
        #     return np.maximum(x - self.l / 2.0, self.lower_bound), np.minimum(x + self.l / 2.0, self.upper_bound)

        # get_boundaries = lambda x: (
        #         np.maximum(x - self.l / 2.0, self.lower_bound), np.minimum(x + self.l / 2.0, self.upper_bound))

        # get_boundaries = lambda x: (
        #         np.maximum(x.lower, self.lower_bound), np.minimum(x.upper, self.upper_bound))
        # region_boundaries = get_boundaries(self.bins)

        # np.maximum(x.lower, self.lower_bound), np.minimum(x.upper, self.upper_bound))

        region_boundaries = [(max(b.lower, self.lower_bound), min(b.upper, self.upper_bound)) for b in self.bins]

        # print("1", region_boundaries)
        region_boundaries = np.concatenate(region_boundaries)
        # print("2", region_boundaries)
        region_boundaries = np.concatenate(([self.lower_bound], region_boundaries, [self.upper_bound]))
        # print("3", region_boundaries)
        region_boundaries = np.sort(region_boundaries)
        # print("4", region_boundaries)
        self.region_boundaries = region_boundaries
        # print("5", self.region_boundaries)

        # remove duplicates
        self.region_boundaries = self.compute_boundaries()



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



        #print(self.encode(0.05))

        # print(self.bins)
        # print("boundaries:", self.region_boundaries)
        # print("centers:", self.region_centers)
        # print("weights:", self.region_weights)
        # print("codes:", self.region_codes)


    def compute_boundaries(self):



        # merge boundaries from each of the sub-encoders
        # delta_count = {}
        boundaries = self.region_boundaries
        # region_deltas = self.region_deltas

        # for i in range(len(boundaries)):
        #     key = boundaries[i]
        #     cnt = region_deltas[i]
        #     try:
        #         delta_count[key] += cnt
        #     except:
        #         delta_count[key] = cnt

        sorted_boundaries = np.sort(boundaries)

        # sorted_boundaries = sorted(boundaries)
        # sorted_boundaries = sorted(list(delta_count.keys()))
        # sorted_deltas = [delta_count[k] for k in sorted_boundaries]

        # find pairs of boundary points that are near enough to each other to be considered identical
        # remove these as duplicates and merge delta counts
        unique_boundaries = []
        # unique_delta_count = {}
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
                # unique_delta_count[key] = sorted_deltas[index]

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
                # unique_delta_count[min_key] = 0
                # for index in boundary_group:
                #     unique_delta_count[min_key] += sorted_deltas[index]

        # unique_deltas = [unique_delta_count[k] for k in unique_boundaries]

        return unique_boundaries

        # return unique_boundaries, unique_deltas
        #

        #         region_boundaries = np.array(bin_lower_multiples)
        #
        #         # record region boundary points
        #         region_boundaries = np.concatenate(region_boundaries)
        #         region_boundaries = np.concatenate(([xmin], region_boundaries, [xmax]))
        #         region_boundaries = np.sort(region_boundaries)
        #
        #         sorted_boundaries = region_boundaries
        #
        #         # find pairs of boundary points that are near enough to each other to be considered identical
        #         # remove these as duplicates and merge delta counts
        #         unique_boundaries = []
        #         boundary_groups = []
        #
        #         # find groups of near boundaries
        #         j = 0
        #         while j < len(sorted_boundaries):
        #             boundary_group = [j]
        #             last_k = j + 1
        #             for k in range(j + 1, len(sorted_boundaries)):
        #                 bound_diff = abs(sorted_boundaries[j] - sorted_boundaries[k])
        #
        #                 if bound_diff < 0.001:
        #                     boundary_group.append(k)
        #                 else:
        #                     break
        #
        #                 # last_k set here to handle both break termination and end-of-array termination
        #                 last_k = k + 1
        #
        #             boundary_groups.append(boundary_group)
        #             j = last_k
        #
        #         # merge groups into single boundaries
        #         for boundary_group in boundary_groups:
        #             # print("group:", boundary_group)
        #
        #             # singleton
        #             if len(boundary_group) == 1:
        #                 index = boundary_group[0]
        #                 min_key = sorted_boundaries[index]
        #                 unique_boundaries.append(min_key)
        #
        #             # multiple boundaries to be merged
        #             else:
        #                 # find val with smallest number of digits
        #                 min_index = -1
        #                 min_count = 1e100
        #                 for index in boundary_group:
        #                     float_val = sorted_boundaries[index]
        #                     char_count = len(str(float_val))
        #                     if char_count < min_count:
        #                         min_count = char_count
        #                         min_index = index
        #                 min_key = sorted_boundaries[min_index]
        #
        #                 # create smallest digit boundary value
        #                 unique_boundaries.append(min_key)
        #
        #         unique_boundaries = np.array(unique_boundaries)
        #
        #         return bin_congruence, unique_boundaries



class FixedWeightEncoder(_IntervalEncoder):
    """
    FixedWeightEncoder class is designed for encoding with fixed weights while maintaining certain
    invariants in the intervals. It ensures that the bins created adhere to constraints such as
    overlapping bins or imbricating code, while calculating derived parameters like step size and
    region boundaries/centers.

    The class automatically computes undetermined attributes (`n` or `l`) based on predefined
    equations, ensuring a consistent and robust encoding structure. Additionally, it prepares bin
    configurations, region boundaries, centers, weights, and other crucial encoding details.

    Attributes:
        n (int): The number of bins used in the encoder. Must follow the condition `n >= 2w`.
        l (float): Length of intervals, calculated or provided depending on the configuration.
        w (int): Weight of the encoder, representing the number of overlapping bins or intervals.
        L (float): Total length or range of the encoding space.
        lower_bound (float): The starting point of the encoding range.
        upper_bound (float): The ending point of the encoding range.
        region_boundaries (list[float]): Boundary points dividing the encoding range into partitions.
        region_centers (list[float]): Center points of each region within defined boundaries.
        bins (list): List of bin intervals defining the encoding configuration.
        regions (list): List of unique regions intersected by combinations of bins.
        region_sizes (list[float]): List containing sizes of each region.
        region_codes (list): Encoded representations for region centers.
        region_weights (list[int]): The count of non-zero codes for each region.
        region_indices (list[tuple[int]]): Indices of regions as tuples from non-zero codes.
        region_deltas (list[int]): Deltas representing changes at boundaries and transitions of regions.
    """
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
        step_size = self.L / num_partitions

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

        self.region_sizes = [step_size, ] * len(self.region_centers)
        self.region_codes = self.encode(self.region_centers)
        self.region_weights = np.count_nonzero(self.region_codes, axis=1)
        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]
        self.region_deltas = np.ones(len(self.region_boundaries), dtype=int)
        self.region_deltas[0] = self.w
        self.region_deltas[-1] = self.w


class TaperingWeightEncoder(_IntervalEncoder):
    """
    Encodes intervals into bins and calculates related weights, regions, and steps
    based on tapering and boundary conditions.

    This class adjusts the creation of bins based on the tapering weight, which could
    vary given the input parameters. The bins are equidistant within the parameters'
    scope, ensuring the calculated regions and their boundaries follow the defined
    tapering formula. The configuration ensures algebraic consistency and checks
    invariants such as the condition `n >= 2w`.

    Attributes:
        n (Optional[int]): The number of bins to be created, calculated if unspecified.
        l (Optional[float]): The length of each bin, computed if unspecified.
        w (int): Weight parameter affecting bin allocation and length calculation.
        L (float): Total length of the interval to be divided into bins.
        lower_bound (float): Starting point of the interval.
        upper_bound (float): Ending point of the interval.
        region_boundaries (np.ndarray): Points defining the boundaries of the
            regions derived from the bins.
        region_centers (np.ndarray): Center points of the regions determined from
            the boundaries.
        bins (List[interval]): List of bins represented as closed-open intervals.
        regions (List[interval]): List of regions as unique intervals intersected
            by combinations of the bins.
        region_sizes (List[float]): Sizes of the regions created from boundary
            calculations.
        region_codes (np.ndarray): Encoded center points for the regions.
        region_weights (np.ndarray): Count of non-zero weights in the encoded regions.
        region_indices (List[Tuple[int]]): Indices of non-zero weights for each region.
        region_deltas (np.ndarray): Array of delta values (e.g., ones) associated
            with the regions.
    """
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
        step_size = self.L / num_partitions

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

        self.region_sizes = [step_size, ] * len(self.region_centers)
        self.region_codes = self.encode(self.region_centers)
        self.region_weights = np.count_nonzero(self.region_codes, axis=1)
        self.region_indices = [tuple(np.nonzero(region)[0]) for region in self.region_codes]
        self.region_deltas = np.ones(len(self.region_boundaries), dtype=int)
