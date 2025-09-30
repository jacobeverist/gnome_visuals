from typing import NamedTuple


### GEOMETRY OF ARRANGING BINS

class ClippedBin(NamedTuple):
    """Represents a clipped bin with its lower bound and width."""
    lower: float
    width: float


def _is_bin_completely_below_interval(bin_upper: float, interval_lower: float) -> bool:
    """Check if the bin is completely below the interval's lower bound."""
    return bin_upper < interval_lower


def _is_bin_completely_above_interval(bin_lower: float, interval_upper: float) -> bool:
    """Check if the bin is completely above the interval's upper bound."""
    return bin_lower >= interval_upper


def clip_bin(bin_lower: float, bin_upper: float, lower_bound: float, upper_bound: float) -> ClippedBin:
    """Check and resize bin so that it fits within the input interval.

    :param bin_lower: lower bound of bin
    :param bin_upper: upper bound of bin
    :param lower_bound: lower bound of interval
    :param upper_bound: upper bound of interval
    :return: ClippedBin with clipped lower bound and bin width
    :raises ValueError: if bin is completely outside the interval
    """
    # FIXME: don't handle case where bin is larger than input interval

    clipped_lower = bin_lower
    clipped_upper = bin_upper

    # Case 1: bin exceeds or is below the interval lower bound
    if bin_lower < lower_bound:
        clipped_lower = lower_bound

        if _is_bin_completely_below_interval(bin_upper, lower_bound):
            raise ValueError("Bin is completely below the interval and has zero width after clipping.")

        clipped_upper = bin_upper

    # Case 2: bin exceeds or is above the interval upper bound
    elif bin_upper > upper_bound:
        clipped_upper = upper_bound

        if _is_bin_completely_above_interval(bin_lower, upper_bound):
            raise ValueError("Bin is completely above the interval and has zero width after clipping.")

        clipped_lower = bin_lower

    # Case 3: bin is completely within interval bounds (no adjustment needed)

    bin_width = clipped_upper - clipped_lower
    return ClippedBin(lower=clipped_lower, width=bin_width)


def compute_bin_arrangement(encoder_w, encoder_bins, box_height=1.0, draw_y=0.0, xmin=0.0, xmax=1.0, clip_on=True,
                            do_folded_bins=False):
    """
    Computes arrangements for a set of bins and returns their visual representation as a list of
    rectangle specifications. The function handles clipping, shrinking, padding, and folding of bins based
    on the provided parameters.

    Args:
        box_height: Float, height of each bin box. Defaults to 1.0.
        encoder_w: Integer, number of simultaneous active bins in the encoder.
        encoder_bins: List of bins represented as objects with `lower` and `upper` attributes.
        xmin: Float, the minimum visual x-coordinate boundary. Defaults to 0.0.
        xmax: Float, the maximum visual x-coordinate boundary. Defaults to 1.0.
        clip_on: Boolean, determines whether bins are clipped within the [xmin, xmax] range. Defaults to True.
        do_folded_bins: Boolean, specifies if bins should be folded (stacked vertically in rows). Defaults to False.

    Returns:
        List[dict]: A list of dictionaries where each dictionary contains parameters for rectangle
        representation (`box_x`, `box_y`, `box_width`, `box_height`) of a bin.

    Raises:
        Exception: Raised when clipping fails during bin arrangement.
    """

    # constants
    box_height = box_height

    # shrink the bins by this amount as a way to create space padding between bins
    x_shrink = 0.004
    y_shrink = 0.3

    bin_id_count = 0
    # draw_y = 0.0
    min_y = 1e100
    max_y = -1e100

    bin_count = 0
    bin_rects = []

    # base position of where the encoder bins will be drawn
    encoder_y = draw_y

    # cycle through each bin of this encoder and figure out how to draw them
    # if overlapping, folded or unfolded
    for k in range(len(encoder_bins)):
        b = encoder_bins[k]
        bin_upper_bound = b.upper
        bin_lower_bound = b.lower

        box_x = bin_lower_bound

        # if folding, alternate row so they are snug together
        if do_folded_bins:
            box_y = encoder_y + (k % encoder_w) * box_height
        else:
            box_y = draw_y

        # length of bin
        box_width = bin_upper_bound - bin_lower_bound

        # clip the bin if it hits visual boundary, or dont draw altogether if beyond range
        draw_bin = True
        if clip_on:
            try:
                box_x, box_width = clip_bin(bin_lower_bound, bin_upper_bound, xmin, xmax)
            except Exception as e:
                draw_bin = False

        # draw bin
        if draw_bin:
            box_x_arg = box_x + x_shrink / 2.0
            box_y_arg = box_y + (box_height * y_shrink) / 2.0
            box_width_arg = box_width - x_shrink
            box_height_arg = box_height - (box_height * y_shrink)

            rect_params = dict(box_x=box_x_arg, box_y=box_y_arg, box_width=box_width_arg, box_height=box_height_arg)

            bin_rects.append(rect_params)

        bin_count += 1
        bin_id_count += 1

        # compute min and max y
        if box_y < min_y:
            min_y = box_y
        if box_y + box_height > max_y:
            max_y = box_y + box_height

        # if folding, compute the row after this encoder from the max_y
        # update draw_y to maximum y so far
        draw_y = max_y

    return bin_rects


def get_min_max_y_of_bin_rects(bin_rects):
    max_y = 0.0
    min_y = 1e100
    for r in bin_rects:
        if r['box_y'] < min_y:
            min_y = r['box_y']
        if r['box_y'] + r['box_height'] > max_y:
            max_y = r['box_y'] + r['box_height']
    return min_y, max_y


def compute_simple_bins(encoder, box_height, draw_y, xmin=None, xmax=None, clip_on=True, do_folded_bins=False):
    bin_rects = compute_bin_arrangement(encoder.w, encoder.bins, box_height=box_height, draw_y=draw_y, xmin=xmin, xmax=xmax,
                                        clip_on=clip_on,
                                        do_folded_bins=do_folded_bins)

    encoder_min_y, encoder_max_y = get_min_max_y_of_bin_rects(bin_rects)

    return bin_rects, encoder_min_y, encoder_max_y


### VISUALS


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from icecream import ic
    from gnomecode.encoders import FixedWeightEncoder

    encoder = FixedWeightEncoder(n=17, w=3)

    fig, axes = plt.subplots(2, 1, num=1, figsize=(10, 7), dpi=300, gridspec_kw={'height_ratios': [1, 1]},
                             constrained_layout=True)
    ax0 = axes[0]
    ax1 = axes[1]

    # n_bits = encoder.n
    n_grids = 1
    x_pad = 0.1

    xmin = encoder.lower_bound - x_pad
    xmax = encoder.upper_bound + x_pad

    draw_folded_bins = True
    fontsize = 8

    result, draw_min_y, draw_max_x = compute_simple_bins(encoder, 1.0, 0.0, xmin=xmin, xmax=xmax, clip_on=False,
                                                         do_folded_bins=draw_folded_bins)
    print(draw_min_y, draw_max_x)
    ic(result)
