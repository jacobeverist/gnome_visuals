import numpy as np

__all__ = ["gnome_similarity", "count_similarity"]

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


