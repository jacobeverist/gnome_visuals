import numpy as np

__all__ = ["gnome_similarity", "count_similarity", "clip_bin"]


def clip_bin(bin_lower, bin_upper, lower_bound, upper_bound):
    """

    :param bin_lower: lower bound of bin
    :param bin_upper: upper bound of bin
    :param lower_bound: lower bound of interval
    :param upper_bound: upper bound of interval
    :return: 2-tuple (bin_lower, bin_width)
    """

    # FIXME: don't handle case where bin is larger than input interval

    do_draw = True

    # box_x, box_width = self._clip(box_x, box_width, lower_bound, upper_bound, bin_upper_bound)
    # case 1: bin exceeds lower bound
    if bin_lower < lower_bound:
        bin_lower = lower_bound

        # bin completely outside of input interval
        if bin_upper < lower_bound:
            bin_upper = lower_bound
            do_draw = False

    # case 2: bin exceeds interval upper bound
    elif bin_upper > upper_bound:
        bin_upper = upper_bound

        # bin completely outside of input interval
        if bin_lower >= upper_bound:
            bin_lower = upper_bound
            do_draw = False

    # case 3: bin within interval bounds
    else:
        # do nothing
        pass

    if not do_draw:
        raise Exception("Bin not within clipped input interval.  Has zero width.")

    bin_width = bin_upper - bin_lower

    return bin_lower, bin_width

def gnome_similarity(X_gnomes, ref_gnomes):
    """Gnome similarity score.

    Asymmetric score with respect to X_gnomes

    :param X_gnomes: array_like
        An array with shape (n_samples, n_features).

    :param ref_gnomes: array_like
        An array with shape (n_samples, n_features).

    :return: array
        An array of scores from 0.0 to 1.0 with shape (n_samples)

    """

    # FIXME: Normalize based on ref_gnomes bit count, not X_gnomes

    sum_scores = np.dot(X_gnomes.astype(int), ref_gnomes.T.astype(int))
    l1_norm = np.count_nonzero(X_gnomes, axis=1)

    # replace any 0 values with 1
    l1_norm[l1_norm == 0] = 1

    normalized_scores = np.divide(sum_scores, l1_norm[:, np.newaxis])

    return normalized_scores

def count_similarity(X_gnomes, ref_gnomes):
    """Count similarity score. Number of common bits between X_gnomes element and ref_gnomes element.

    :param X_gnomes: An array with shape (n_samples, n_features).
    :type X_gnomes: list | np.array

    :param ref_gnomes: An array with shape (n_samples, n_features).
    :type ref_gnomes: list | np.array

    :return: An array of scores from 0 to n_features with shape (n_samples)
    :rtype: np.array

    """

    # FIXME: Normalize?

    sum_scores = np.dot(X_gnomes.astype(int), ref_gnomes.T.astype(int))

    return sum_scores


