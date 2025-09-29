import numpy as np

__all__ = ["gnome_similarity", "count_similarity", "count_difference", "clip_bin"]



def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0 / (pl_entries - 1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = np.array(cmap(k * h)[:3]) * 255
        C = list(C.astype(np.uint8).astype(np.uint8))
        pl_colorscale.append([k * h, 'rgb' + str((int(C[0]), int(C[1]), int(C[2])))])

    return pl_colorscale



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


def count_difference(X_gnomes, ref_gnomes):
    """Count difference score. Essentially the Hamming distance without normalization.
       Number of bits that are flipped between X_gnomes element and ref_gnomes element.

    :param X_gnomes: An array with shape (n_samples, n_features).
    :type X_gnomes: list | np.array

    :param ref_gnomes: An array with shape (n_samples, n_features).
    :type ref_gnomes: list | np.array

    :return: An array of scores from 0 to n_features with shape (n_samples)
    :rtype: np.array

    """

    #print("shape:", X_gnomes.shape, ref_gnomes.T.shape)

    # generate distance matrix:
    B = np.rot90(X_gnomes[:, :, None], 1, (1, 2))  # [:,:,None] is needed to add a dimension
    C = np.rot90(np.rot90(ref_gnomes[:, :, None], 1, (1, 2)), 1, (0, 1))  # [:,:,None] is needed to add a dimension


    # result = np.sqrt(np.sum((B - C) ** 2, axis=2))
    result = np.count_nonzero(np.logical_xor(B, C), axis=2)

    """
    print("B------", B.shape)
    print(B)
    print("C------", C.shape)
    print(C)
    print("result--", result.shape)
    print(result)

    print("B:", B.shape)
    print("C:", C.shape)
    print("result:", result.shape)
    """
    #print(result)


    # sum_scores = np.dot(X_gnomes.astype(int), ref_gnomes.T.astype(int))
    #sum_scores = np.matmul(X_gnomes.astype(int), ref_gnomes.T.astype(int))
    #print(sum_scores.shape)

    #diff_compare = np.not_equal(X_gnomes[..., np.newaxis], ref_gnomes.T)
    #print(diff_compare.shape)

    #diff_bits = np.logical_xor(X_gnomes.astype(bool), ref_gnomes.T.astype(bool))
    # diff_scores = np.count_nonzero(X_gnomes.astype(int) != ref_gnomes.T.astype(int))
    #diff_scores = np.count_nonzero(X_gnomes.astype(int) != ref_gnomes.astype(int))

    #return diff_bits

    return result
