import re
from typing import NamedTuple
import string
import textwrap

import matplotlib.patches as patches
import numpy as np
from matplotlib import ticker
from matplotlib.collections import PatchCollection
from matplotlib.transforms import Affine2D
import matplotlib.pyplot as plt
import seaborn as sns
from icecream import ic

from gnomecode.encoders import FixedWeightEncoder


def matplotlib_to_color_list(cmap, num_entries):
    h = 1.0 / (num_entries - 1)
    pl_colorscale = []

    for k in range(num_entries):
        # C = np.array(cmap(k * h)[:3]) * 255
        C = cmap(k * h)
        # C = np.array(cmap(k * h)) * 255
        # C = list(C.astype(np.uint8).astype(np.uint8))
        # pl_colorscale.append([k * h, 'rgb' + str((int(C[0]), int(C[1]), int(C[2])))])
        pl_colorscale.append(C)

    return pl_colorscale


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

def new_rect(box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k',
             facecolor='none', alpha=1.0, clip_on=False, label=None, zorder=1):
    # add rectangle at corner position and rotate by angle
    return patches.Rectangle((box_x, box_y), box_width, box_height, angle=angle, linewidth=linewidth,
                             edgecolor=edgecolor,
                             facecolor=facecolor, clip_on=clip_on, alpha=alpha, label=label, zorder=zorder)


def add_text_rect(ax, box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k', fontsize=8,
                  facecolor='none', text_str=None, aligned_text=False, alpha=1.0, text_v_offset=-0.01, clip_on=False,
                  label=None, zorder=1, add_patch=True):
    # Add Rectangle

    # create rectangle
    rect = new_rect(box_x, box_y, box_width, box_height, angle=angle, linewidth=linewidth,
                    edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, clip_on=clip_on,
                    label=label, zorder=zorder)
    # add to axes
    if add_patch:
        ax.add_patch(rect)

    # Add Text
    if text_str is not None:

        # data space coordinates to find new point after rotated
        fixed_point_rotation = Affine2D().rotate_deg_around(box_x, box_y, angle)

        # put angle within +180/-180
        normalized_angle = angle
        if angle > 0:
            while normalized_angle > 180:
                normalized_angle -= 360
        elif angle < 0:
            while normalized_angle < -180:
                normalized_angle += 360

        # angle the textbox nicely
        if aligned_text:
            text_angle = normalized_angle
            if abs(text_angle) > 90:
                text_angle += 180
        else:
            text_angle = 0

        # space the text box nicely so it fits no matter orientation
        # nice centering depends on orientation of text in the figure
        if aligned_text:

            # upper quadrants and bottom quadrants have different text orientation and adjustment
            if abs(normalized_angle) > 90:
                # upper quadrant adjustment
                rect_center_pos = [box_x + box_width / 2, box_y + box_height * 0.5 - text_v_offset]
            else:
                # bottom quadrant adjustment
                rect_center_pos = [box_x + box_width / 2, box_y + box_height * 0.5 + text_v_offset]
        else:
            rect_center_pos = [box_x + box_width / 2, box_y + box_height * 0.5]

        # rotate around rectangle corner
        text_pos = fixed_point_rotation.transform(rect_center_pos)

        # unaligned text uses standard vertical offset in axes frame
        if not aligned_text:
            text_pos[1] += text_v_offset

        # add text box to center of rectangle
        ax.text(text_pos[0], text_pos[1], text_str, rotation=text_angle, rotation_mode='anchor',
                fontsize=fontsize, va='center', ha='center', clip_on=clip_on, alpha=alpha, zorder=zorder + 2)

    return rect


def compute_bin_arrangement(encoder_w, encoder_bins, xmin=0.0, xmax=1.0, clip_on=True, do_folded_bins=False):
    """
    Computes arrangements for a set of bins and returns their visual representation as a list of
    rectangle specifications. The function handles clipping, shrinking, padding, and folding of bins based
    on the provided parameters.

    Args:
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
    box_height = 1

    # shrink the bins by this amount as a way to create space padding between bins
    x_shrink = 0.004
    y_shrink = 0.3

    # FIXME: find and optimize bottleneck for large n

    bin_id_count = 0
    draw_y = 0.0
    min_y = 1
    max_y = 0

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
            box_y_arg = box_y + y_shrink / 2.0
            box_width_arg = box_width - x_shrink
            box_height_arg = box_height - y_shrink

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


def draw_interval_encoder_bins(ax, encoder, colors, xmin=None, xmax=None, clip_on=True, fontsize=8, bin_linewidth=1.0,
                               draw_regions=False, draw_h_grid=True, draw_region_by_encoder=True,
                               do_folded_bins=False, label_bins=False, grid_label_size=8):
    # constants
    box_height = 1

    encoder_count = 0
    bin_id_count = 0
    draw_y = 0.0
    min_y = 1
    max_y = 0

    draw_bound_y = 0
    prev_bound_y = 0

    encoder_boundaries = [draw_bound_y, ]

    bin_count = 0
    patches = []

    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound

    grid_colors = [colors[j] for j in range(n_grids)]

    # convert class name to spaced words and wrap around
    grid_label = textwrap.fill(
            "(%d) %s" %
            (0, re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1',
                             encoder.__class__.__name__)
             ),
            12)

    bin_rects = compute_bin_arrangement(encoder.w, encoder.bins, xmin=xmin, xmax=xmax, clip_on=clip_on,
                                        do_folded_bins=do_folded_bins)

    for k in range(len(bin_rects)):
        r = bin_rects[k]

        if label_bins:
            bin_text_str = str(bin_id_count)
        else:
            bin_text_str = None

        rect = add_text_rect(ax, r['box_x'], r['box_y'], r['box_width'], r['box_height'],
                             alpha=1.0, facecolor=grid_colors[encoder_count],
                             text_str=bin_text_str, clip_on=clip_on, linewidth=bin_linewidth,
                             fontsize=fontsize, label=grid_label if bin_count == 0 else None,
                             add_patch=False)
        patches.append(rect)

        # compute min and max y
        if r['box_y'] < min_y:
            min_y = r['box_y']
        if r['box_y'] + r['box_height'] > max_y:
            max_y = r['box_y'] + r['box_height']

        bin_count += 1
        bin_id_count += 1

        # if folding, compute the row after this encoder from the max_y
        # update draw_y to maximum y so far
        # draw_y = max_y

    # drawing boundaries
    e_boundaries = encoder.region_boundaries
    draw_bound_y = draw_y

    # draw vertical region boundaries within an encoder section
    if draw_region_by_encoder:
        ax.vlines(x=e_boundaries, ymin=prev_bound_y, ymax=draw_bound_y, alpha=0.2, linewidth=0.5, color='k',
                  zorder=-1)

    # draw horizontal boundaries between bin rows and encoder sections
    if draw_h_grid:

        # strong line between encoder sections
        ax.hlines(y=prev_bound_y, xmin=xmin, xmax=xmax, alpha=1.0, linewidth=1.5, color='k', zorder=-1)

        # weak lines between bin rows, for both folded and unfolded bins
        curr_y = prev_bound_y
        while curr_y < draw_bound_y:
            ax.hlines(y=curr_y, xmin=xmin, xmax=xmax, alpha=0.5, linewidth=0.5, color='k', zorder=-1)
            curr_y += box_height
            # print(draw_bound_y, prev_bound_y, curr_y )

    # set the this as boundary line to the next encoder section
    encoder_boundaries.append(draw_bound_y)
    prev_bound_y = draw_bound_y
    encoder_count += 1

    # encoder horizontal dividers and the mid-point between each divider
    encoder_boundaries = np.array(encoder_boundaries)
    encoder_centers = encoder_boundaries[:-1] + np.diff(encoder_boundaries) / 2

    # strong line between encoder sections
    if draw_h_grid:
        ax.hlines(y=draw_bound_y, xmin=xmin, xmax=xmax, alpha=1.0, linewidth=1.5, color='k', zorder=-1)

    # add any rectangles if they've been collected
    if len(patches) > 0:
        ax.add_collection(PatchCollection(patches, match_original=True))

    # draw the composite region boundaries of all the encoders together
    if draw_regions:
        boundaries = encoder.region_boundaries
        for k in range(len(boundaries)):
            ax.vlines(x=boundaries[k], ymin=0, ymax=max_y, alpha=0.2, linewidth=0.5, color='k', zorder=-1)
            # ax.vlines(x=boundaries[k], ymin=0, ymax=n_bits, alpha=0.2, linewidth=0.5, color='k', zorder=-1)
        # n_bits = encoder.n
        # for k in range(n_bits + 1):
        #    ax.hlines(y=k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    # ticks correspond to encoder horizontal dividers and
    # tick labels are vertically centered to encoder region with an integer label for the i'th encoder
    ax.yaxis.set_major_locator(ticker.FixedLocator(encoder_boundaries))
    ax.yaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_minor_locator(ticker.FixedLocator(encoder_centers))
    ax.yaxis.set_minor_formatter(ticker.FixedFormatter([grid_label,]))
    # ax.yaxis.set_tick_params(which="minor", labelrotation=-45, labelsize=8)
    ax.yaxis.set_tick_params(which="minor", labelsize=grid_label_size)

    for tick in ax.yaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
    for label in ax.get_yticklabels(minor=True):
        label.set_verticalalignment('center')

    ax.set_ylim(min_y - 0.1, max_y + 0.1)
    ax.set_ylabel("Encoding Bins\non Interval")

    return max_y, min_y


def draw_periodic_encoder_bins(ax, encoder, colors, xmin=None, xmax=None, clip_on=True, fontsize=8, bin_linewidth=1.0,
                               draw_regions=False, draw_h_grid=True, draw_h_border=True, draw_region_by_encoder=True,
                               draw_folded_bins=False, label_bins=False, grid_label_size=8, grid_labels=None):
    # constants
    bin_alpha = 1
    cong_alpha = 0.3
    fund_alpha = 0.1
    box_height = 1

    # shrink the the bins by this amount
    x_shrink = 0.004
    y_shrink = 0.3

    # FIXME: find and optimize bottleneck for large n

    n_bits = encoder.n
    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound

    # try:
    #     sub_encoders = encoder.encoders
    # except:
    #     sub_encoders = [encoder]

    sub_encoders = [encoder]
    n_grids = len(sub_encoders)
    grid_names = string.ascii_uppercase[:n_grids]

    keys = list(range(n_grids))
    keys.sort()

    grid_colors = [colors[j] for j in range(n_grids)]

    # convert class name to spaced words and wrap around
    if grid_labels is None:
        grid_labels = [
                textwrap.fill(
                        "(%d) %s" %
                        (keys[j], re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1',
                                         sub_encoders[j].__class__.__name__)
                         ),
                        12)
                for j in range(n_grids)]

    encoder_count = 0
    bin_id_count = 0
    draw_y = 0.0
    min_y = 1
    max_y = 0

    draw_bound_y = 0
    prev_bound_y = 0

    encoder_boundaries = [draw_bound_y, ]

    bin_count = 0
    patches = []

    # cycle through each sub-encoder and draw the bins of each
    for e in sub_encoders:

        # look to see if there are fundamental regions to plot
        try:
            _ = e.fund_regions
            do_fund_regions = True
        except:
            do_fund_regions = False

        # look to see if there are congruent bins to plot
        try:
            _ = e.bin_congruence
            do_cong_bins = True
        except:
            do_cong_bins = False

        try:
            # the weight parameter of the encoder if it exists
            # an integer indicating number of simultaneous bits that are active
            encoder_w = e.w

            # if bins overlap due to w > 1, then whether to draw them
            # folded together or whether to draw them each on their own row
            if draw_folded_bins:
                do_folded_bins = True
            else:
                do_folded_bins = False
        except:
            encoder_w = 1
            do_folded_bins = False

        # base position of where the encoder bins will be drawn
        encoder_y = draw_y

        # cycle through each bin of this sub-encoder and figure out how to draw them
        # if overlapping, folded or unfolded
        # if periodic, whether to draw the fundamental regions and the congruent bins
        for k in range(len(e.bins)):
            b = e.bins[k]
            bin_upper_bound = b.upper
            bin_lower_bound = b.lower

            box_x = bin_lower_bound

            # if folding, alternate row so they are snug together
            if do_folded_bins:
                box_y = encoder_y + (k % encoder_w) * box_height

                # if last set of bins, let them place above encoder_w so no overlap with first bins
                last_norm_bin = len(e.bins) - encoder_w
                if do_cong_bins and encoder_w > 1 and k > last_norm_bin:
                    box_y = encoder_y + (last_norm_bin % encoder_w) * box_height + (k - last_norm_bin) * box_height
            else:
                box_y = draw_y

            # length of bin
            box_width = bin_upper_bound - bin_lower_bound

            # clip the bin if it hits visual boundary, or dont draw altogether if beyond range
            draw_bin = True
            if clip_on:
                try:
                    box_x, box_width = clip_bin(bin_lower_bound, bin_upper_bound, xmin, xmax)
                except:
                    draw_bin = False

            # only add label to first rectangle of encoder's bins (used by legend)
            grid_label = None
            if bin_count == 0:
                grid_label = grid_labels[encoder_count]

            if label_bins:
                bin_text_str = str(bin_id_count)
            else:
                bin_text_str = None

            # draw bin
            if draw_bin:
                rect = add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                                     box_height - y_shrink, alpha=1.0, facecolor=grid_colors[encoder_count],
                                     text_str=bin_text_str, clip_on=clip_on, linewidth=bin_linewidth,
                                     fontsize=fontsize, label=grid_label, add_patch=False)
                # print("draw", bin_text_str, grid_label, rect)
                patches.append(rect)

            # draw congruent bins if exist
            if do_cong_bins:

                congruent_bins = e.bin_congruence[k]

                # draw each congruent bin if it is within view
                for j in range(len(congruent_bins)):
                    cb = congruent_bins[j]
                    bin_upper_bound = cb.upper
                    bin_lower_bound = cb.lower

                    box_x = bin_lower_bound
                    box_width = bin_upper_bound - bin_lower_bound

                    draw_cong_bin = True
                    if clip_on:
                        try:
                            box_x, box_width = clip_bin(bin_lower_bound, bin_upper_bound, xmin, xmax)
                        except:
                            draw_cong_bin = False

                    # draw bin
                    if draw_cong_bin:
                        rect = add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                                             box_height - y_shrink, alpha=cong_alpha, clip_on=True, add_patch=False,
                                             facecolor=grid_colors[encoder_count], linewidth=bin_linewidth)
                        patches.append(rect)

            # draw fundamental region if exist
            if do_fund_regions:
                fund_region = e.fund_regions[k]
                fund_upper_bound = fund_region.upper
                fund_lower_bound = fund_region.lower

                box_x = fund_lower_bound

                draw_fund_bin = True

                if do_folded_bins:

                    # assumes that fund regions of each cell in this encoder are identical
                    # FIXME: test are fund. regions the same, else don't do folding of periodic bins
                    if k >= encoder_w:
                        draw_fund_bin = False

                    # if last set of bins, let them place above encoder_w
                    last_norm_bin = len(e.bins) - encoder_w
                    if do_cong_bins and encoder_w > 1 and k > last_norm_bin:
                        draw_fund_bin = True

                box_width = fund_upper_bound - fund_lower_bound

                if clip_on:
                    try:
                        box_x, box_width = clip_bin(fund_lower_bound, fund_upper_bound, xmin, xmax)
                    except:
                        draw_fund_bin = False

                if draw_fund_bin:
                    rect = new_rect(box_x, box_y, box_width, box_height, alpha=fund_alpha,
                                    facecolor='k', clip_on=clip_on, linewidth=0.0, zorder=9)
                    patches.append(rect)

                if draw_region_by_encoder:
                    # add vertical line for each congruence region boundary
                    # multiply boundary points for each cell outside of fundamental region
                    region_multiples = []
                    x_lower = fund_region.lower

                    # add original
                    region_multiples.append(x_lower)

                    x_lower = x_lower + e.periods[k]
                    while x_lower < xmax:
                        region_multiples.append(x_lower)
                        x_lower = x_lower + e.periods[k]

                    x_lower = fund_region.lower
                    x_lower = x_lower - e.periods[k]
                    while x_lower >= xmin:
                        region_multiples.append(x_lower)
                        x_lower = x_lower - e.periods[k]

                    ax.vlines(x=region_multiples, ymin=box_y, ymax=box_y + box_height, alpha=1.0, linewidth=1,
                              color='k',
                              zorder=9)

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

        # drawing boundaries
        e_boundaries = e.region_boundaries
        draw_bound_y = draw_y

        # draw vertical region boundaries within an encoder section
        if draw_region_by_encoder:
            ax.vlines(x=e_boundaries, ymin=prev_bound_y, ymax=draw_bound_y, alpha=0.2, linewidth=0.5, color='k',
                      zorder=-1)

        # draw horizontal boundaries between bin rows and encoder sections
        if draw_h_grid:

            # strong line between encoder sections
            ax.hlines(y=prev_bound_y, xmin=xmin, xmax=xmax, alpha=1.0, linewidth=1.5, color='k', zorder=-1)

            # weak lines between bin rows, for both folded and unfolded bins
            curr_y = prev_bound_y
            while curr_y < draw_bound_y:
                ax.hlines(y=curr_y, xmin=xmin, xmax=xmax, alpha=0.5, linewidth=0.5, color='k', zorder=-1)
                curr_y += box_height
                # print(draw_bound_y, prev_bound_y, curr_y )

        # set the this as boundary line to the next encoder section
        encoder_boundaries.append(draw_bound_y)
        prev_bound_y = draw_bound_y
        encoder_count += 1

    # encoder horizontal dividers and the mid-point between each divider
    encoder_boundaries = np.array(encoder_boundaries)
    encoder_centers = encoder_boundaries[:-1] + np.diff(encoder_boundaries) / 2

    # strong line between encoder sections
    if draw_h_grid:
        ax.hlines(y=draw_bound_y, xmin=xmin, xmax=xmax, alpha=1.0, linewidth=1.5, color='k', zorder=-1)

    # add any rectangles if they've been collected
    if len(patches) > 0:
        ax.add_collection(PatchCollection(patches, match_original=True))

    # draw the composite region boundaries of all the encoders together
    if draw_regions:
        boundaries = encoder.region_boundaries
        for k in range(len(boundaries)):
            ax.vlines(x=boundaries[k], ymin=0, ymax=max_y, alpha=0.2, linewidth=0.5, color='k', zorder=-1)
            # ax.vlines(x=boundaries[k], ymin=0, ymax=n_bits, alpha=0.2, linewidth=0.5, color='k', zorder=-1)
        # n_bits = encoder.n
        # for k in range(n_bits + 1):
        #    ax.hlines(y=k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    # ticks correspond to encoder horizontal dividers and
    # tick labels are vertically centered to encoder region with an integer label for the i'th encoder
    ax.yaxis.set_major_locator(ticker.FixedLocator(encoder_boundaries))
    ax.yaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_minor_locator(ticker.FixedLocator(encoder_centers))
    ax.yaxis.set_minor_formatter(ticker.FixedFormatter(grid_labels))
    # ax.yaxis.set_tick_params(which="minor", labelrotation=-45, labelsize=8)
    ax.yaxis.set_tick_params(which="minor", labelsize=grid_label_size)

    for tick in ax.yaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
    for label in ax.get_yticklabels(minor=True):
        label.set_verticalalignment('center')

    ax.set_ylim(min_y - 0.1, max_y + 0.1)
    ax.set_ylabel("Encoding Bins\non Interval")

    return max_y, min_y


if __name__ == "__main__":
    encoder = FixedWeightEncoder(n=17, w=3)

    fig, axes = plt.subplots(2, 1, num=1, figsize=(10, 7), dpi=300, gridspec_kw={'height_ratios': [1, 1]},
                             constrained_layout=True)
    ax0 = axes[0]
    ax1 = axes[1]

    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)
    plotly_colorscale = matplotlib_to_color_list(cmap, 255)
    # colors = cmap.colors

    # colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors

    # n_bits = encoder.n
    n_grids = 1
    x_pad = 0.1

    xmin = encoder.lower_bound - x_pad
    xmax = encoder.upper_bound + x_pad

    # encoder_colors = plotly_colorscale[0:n_grids]
    # encoder_colors = cmap[0:n_grids]
    encoder_colors = plotly_colorscale  # [0:n_grids]
    draw_folded_bins = True
    fontsize = 8

    # draw encoder bins
    draw_interval_encoder_bins(ax0, encoder, encoder_colors, fontsize=fontsize, xmin=xmin, xmax=xmax, draw_h_grid=False,
                               bin_linewidth=0.5, clip_on=False, draw_regions=True, draw_region_by_encoder=False,
                               do_folded_bins=draw_folded_bins, label_bins=True)

    plt.show()
