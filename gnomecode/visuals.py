import string
from fractions import Fraction

import matplotlib as mpl
import matplotlib.axes
import matplotlib.patches as patches
import numpy as np
import numpy.ma as ma
import seaborn as sns
from intervals import FloatInterval as I
from matplotlib import ticker
from matplotlib.collections import PatchCollection
from matplotlib.transforms import Affine2D

from .helpers import *

__all__ = ["draw_bits_by_data", "draw_multi_encoder_bins", "draw_decomposition", "draw_barcode", "draw_delta_count",
           "draw_similarity", "draw_similarity_heatmap", "draw_projected_self_similarity", "draw_code_self_similarity",
           "draw_features"]

# printing boolean arrays neatly
np.set_printoptions(
        precision=3, suppress=True, threshold=1000000, linewidth=400,
        formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


def draw_bits_by_data(ax: mpl.axes.Axes, encoder, draw_uniform_samples=False, draw_region_bits=False,
                      draw_boundaries=False, draw_bit_grid=True, permute_bits=False, xmin=None, xmax=None, clip_on=True,
                      box_height=1, num_samples=150, x_pad=0.002, y_pad=0.15, y_margin=0.5):
    """

    :param draw_uniform_samples:
    :param draw_region_bits:
    :param draw_boundaries:
    :param draw_bit_grid:
    :param permute_bits:
    :param box_height:
    :param num_samples:
    :param x_pad:
    :param y_pad:
    :param ax: mpl.axes.Axes
    :param encoder: gnomecode.encoders.EncoderBase
    :param xmin: float | None
    :param xmax: float | None
    :param clip_on: bool
    """

    # TODO: + optionally permutate bits to show non-local vs. sorted visualization
    # TODO: + sampled bits option, showing bits in grid instead of bars representing the bins
    # TODO: - properly clip and no-clip the bits beyond the interval

    n_bits = encoder.n

    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound
    interval_length = upper_bound - lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound

    # print("draw_bits:", xmin, xmax)

    # scale y-axis to number of bits
    ax.yaxis.set_major_locator(ticker.IndexLocator(5, 0))
    ax.yaxis.set_minor_locator(ticker.IndexLocator(1, 0))
    ax.set_ylim(-y_margin, n_bits + y_margin)
    ax.set_xlim(xmin, xmax)

    indices = np.random.permutation(np.arange(n_bits))

    if draw_uniform_samples and draw_region_bits:
        raise Exception("Both sampling and regions selected, only one permitted.")

    if draw_uniform_samples:
        # 150 samples is about right for square-ish bit plotting
        # sample_spacing = interval_length / num_samples
        sample_spacing = (xmax - xmin) / num_samples

        # shrink the the boxes by this amount
        y_shrink = y_pad * 2.0
        x_shrink = sample_spacing / 5.0

        # internal bin-boundary transition points
        equidist_points = np.linspace(xmin, xmax, endpoint=True, num=num_samples + 1)

        # record region center points
        sample_points = equidist_points[:-1] + np.diff(equidist_points) / 2
        X_points = sample_points.reshape(-1, 1)

        # encodings
        X_gnomes = encoder.encode(X_points)

        for k in range(len(X_points)):
            x_val = float(X_points[k])
            gnome_code = X_gnomes[k]
            sample_upper_bound = x_val + sample_spacing / 2.0
            sample_lower_bound = x_val - sample_spacing / 2.0
            box_x = sample_lower_bound
            box_width = sample_spacing

            do_draw = True

            if clip_on:
                try:
                    # box_x, box_width = clip_bin(sample_lower_bound, sample_upper_bound, lower_bound, upper_bound)
                    box_x, box_width = clip_bin(sample_lower_bound, sample_upper_bound, xmin, xmax)
                except:
                    do_draw = False

            if do_draw:

                patches = []

                for j in range(len(gnome_code)):
                    gnomelet = gnome_code[j]

                    if gnomelet:
                        if permute_bits:
                            box_y = indices[j] * box_height
                        else:
                            box_y = j * box_height

                        x_adj = box_x + x_shrink / 2.0
                        y_adj = box_y + y_shrink / 2.0
                        w_adj = box_width - x_shrink
                        h_adj = box_height - y_shrink

                        # create box representing the bin
                        rect = new_rect(x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor='k', clip_on=clip_on,
                                        linewidth=0.2)
                        patches.append(rect)

                ax.add_collection(PatchCollection(patches, match_original=True))

    elif draw_region_bits:

        # shrink the the boxes by this amount
        y_shrink = y_pad * 2.0
        x_shrink = x_pad * 2.0

        # record region center points
        sample_points = encoder.region_centers
        X_points = sample_points.reshape(-1, 1)

        # encodings
        X_gnomes = encoder.region_codes

        region_widths = np.diff(encoder.region_boundaries)

        for k in range(len(X_points)):
            x_val = float(X_points[k])
            gnome_code = X_gnomes[k]

            sample_upper_bound = x_val + region_widths[k] / 2.0
            sample_lower_bound = x_val - region_widths[k] / 2.0
            box_x = sample_lower_bound
            box_width = region_widths[k]

            do_draw = True

            if clip_on:
                try:
                    box_x, box_width = clip_bin(sample_lower_bound, sample_upper_bound, xmin, xmax)
                except:
                    do_draw = False

            if do_draw:
                patches = []
                for j in range(len(gnome_code)):
                    gnomelet = gnome_code[j]

                    if gnomelet:
                        if permute_bits:
                            box_y = indices[j] * box_height
                        else:
                            box_y = j * box_height

                        box_width_shrunk = box_width - x_shrink
                        x_shrink_adj = x_shrink
                        if box_width_shrunk < x_shrink:
                            x_shrink_adj = 0.4 * box_width

                        x_adj = box_x + x_shrink_adj / 2.0
                        y_adj = box_y + y_shrink / 2.0
                        w_adj = box_width - x_shrink_adj
                        h_adj = box_height - y_shrink

                        # create box representing the bin
                        rect = new_rect(x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor='k', clip_on=clip_on,
                                        linewidth=0.2)
                        patches.append(rect)

                ax.add_collection(PatchCollection(patches, match_original=True))

    else:
        # draw the bins
        y_index = 0

        # shrink the the bins by this amount
        x_shrink = x_pad * 2.0
        y_shrink = y_pad * 2.0

        patches = []

        for bin in encoder.bins:
            bin_upper_bound = bin.upper
            bin_lower_bound = bin.lower

            # FIXME: adjust borders of bins to within [x_min,x_max]
            # FIXME: extend bins adjacent to interval bounds to either x_min or x_max
            # FIXME: make this a different function, plots the bin receptive fields based on encoder clamping behavior

            box_x = bin_lower_bound
            box_width = bin_upper_bound - bin_lower_bound

            do_draw = True

            if clip_on:
                try:
                    box_x, box_width = clip_bin(bin_lower_bound, bin_upper_bound, xmin, xmax)
                except:
                    do_draw = False

            if do_draw:

                if permute_bits:
                    box_y = indices[y_index] * box_height
                else:
                    box_y = y_index * box_height

                box_width_shrunk = box_width - x_shrink
                x_shrink_adj = x_shrink
                if box_width_shrunk < x_shrink:
                    x_shrink_adj = 0.4 * box_width

                x_adj = box_x + x_shrink_adj / 2.0
                y_adj = box_y + y_shrink / 2.0
                w_adj = box_width - x_shrink_adj
                h_adj = box_height - y_shrink

                print("create rect:", y_index, x_adj, y_adj, w_adj, h_adj)

                # create box representing the bin
                rect = new_rect(x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor='k', clip_on=clip_on, linewidth=0.2)
                patches.append(rect)

            y_index += 1

        ax.add_collection(PatchCollection(patches, match_original=True))

    if draw_boundaries:
        boundaries = encoder.region_boundaries
        for k in range(len(boundaries)):
            ax.vlines(x=boundaries[k], ymin=0, ymax=n_bits, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    if draw_bit_grid:
        for k in range(n_bits + 1):
            ax.hlines(y=k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)


def draw_multi_encoder_bins(ax, encoder, xmin=None, xmax=None, clip_on=True, spacing=1, fontsize=8, bin_linewidth=1,
                            draw_regions=False,
                            draw_h_grid=True, draw_h_border=True, draw_region_by_encoder=True, label_bins=False):
    # constants
    bin_alpha = 1
    cong_alpha = 0.3
    fund_alpha = 0.1
    box_height = 1

    # FIXME: find and optimize bottleneck for large n

    # OTHER VISUALS
    # grid horizontal lines
    # grid border horizontal lines
    # interval boundary vertical lines
    # region vertical lines by individual encoder
    # region vertical lines by multi-encoder combinations

    # bin labels
    # bin borders
    # bin colors
    # generate boundaries and region codes and scores outside interval bounds, up to (xmin, xmax)
    # y-axis tick locator resolution (count by x)

    n_bits = encoder.n
    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound

    ax.yaxis.set_major_locator(ticker.IndexLocator(5, 0))
    ax.set_ylim(-0.1, n_bits + 0.1)
    ax.set_ylabel("Encoding Bins\non Interval")

    try:
        sub_encoders = encoder.encoders
    except:
        sub_encoders = [encoder]

    n_grids = len(sub_encoders)
    grid_names = string.ascii_uppercase[:n_grids]

    keys = list(range(n_grids))
    keys.sort()

    colors = sns.color_palette("muted", n_colors=n_grids)
    grid_label_templates = [prefix + "%d" for prefix in grid_names]
    grid_colors = [colors[j] for j in range(n_grids)]

    # grid_colors = ['k',] + grid_colors

    grid_labels = ["%d,%d" % (keys[j], spacing) for j in range(n_grids)]

    encoder_count = 0
    bin_id_count = 0
    draw_y = 0.0
    min_y = 1
    max_y = 0

    bin_count = 0
    patches = []

    for e in sub_encoders:

        # look to see if there are fundamental regions to plot
        try:
            foo = e.fund_regions
            do_fund_regions = True
        except:
            do_fund_regions = False

        # look to see if there are congruent bins to plot
        try:
            foo = e.bin_congruence
            do_cong_bins = True
        except:
            do_cong_bins = False

        for k in range(len(e.bins)):
            bin = e.bins[k]
            bin_upper_bound = bin.upper
            bin_lower_bound = bin.lower

            box_x = bin_lower_bound
            box_y = draw_y
            box_width = bin_upper_bound - bin_lower_bound

            draw_bin = True
            if clip_on:
                try:
                    box_x, box_width = clip_bin(bin_lower_bound, bin_upper_bound, xmin, xmax)
                except:
                    draw_bin = False

            # shrink the the bins by this amount
            x_shrink = 0.004
            y_shrink = 0.3

            # only add label to first rectangle of encoder's bins
            grid_label = None
            if bin_count == 0:
                grid_label = grid_labels[encoder_count]

            # draw bin
            if draw_bin:
                if label_bins:
                    add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                                  box_height - y_shrink, alpha=1.0, facecolor=grid_colors[encoder_count],
                                  text_str=str(bin_id_count), clip_on=clip_on, linewidth=bin_linewidth,
                                  fontsize=fontsize,
                                  label=grid_label)
                else:
                    rect = new_rect(box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                                    box_height - y_shrink, alpha=1.0, facecolor=grid_colors[encoder_count],
                                    clip_on=clip_on, linewidth=bin_linewidth)
                    patches.append(rect)

            # draw congruent bins if exist
            if do_cong_bins:

                bin = e.bins[k]
                congruent_bins = []
                x_lower = bin.lower

                # generate congruent bins instead of using encoder generated versions (e.bin_congruence)
                x_lower = x_lower + e.periods[k]
                while x_lower < xmax:
                    congruent_bins.append(I.closed_open(x_lower, x_lower + e.bin_sizes[k]))
                    x_lower = x_lower + e.periods[k]

                x_upper = bin.upper
                x_upper = x_upper - e.periods[k]

                while x_upper >= xmin:
                    congruent_bins.append(I.closed_open(x_upper - e.bin_sizes[k], x_upper))
                    x_upper = x_upper - e.periods[k]

                for j in range(len(congruent_bins)):
                    bin = congruent_bins[j]
                    bin_upper_bound = bin.upper
                    bin_lower_bound = bin.lower

                    box_x = bin_lower_bound
                    box_y = draw_y
                    box_width = bin_upper_bound - bin_lower_bound

                    draw_cong_bin = True
                    if clip_on:
                        try:
                            box_x, box_width = clip_bin(bin_lower_bound, bin_upper_bound, xmin, xmax)
                        except:
                            draw_cong_bin = False

                    # shrink the the bins by this amount
                    x_shrink = 0.004
                    y_shrink = 0.3

                    # draw bin
                    if draw_cong_bin:
                        if label_bins:
                            add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                                          box_height - y_shrink, alpha=cong_alpha, facecolor=grid_colors[encoder_count],
                                          clip_on=True, linewidth=bin_linewidth, fontsize=fontsize, zorder=10)
                        else:
                            rect = new_rect(box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                                            box_height - y_shrink, alpha=cong_alpha,
                                            facecolor=grid_colors[encoder_count],
                                            clip_on=True, linewidth=bin_linewidth, zorder=10)
                            patches.append(rect)

            # draw fundamental region if exist
            if do_fund_regions:
                fund_region = e.fund_regions[k]
                fund_upper_bound = fund_region.upper
                fund_lower_bound = fund_region.lower

                box_x = fund_lower_bound
                box_y = draw_y
                box_width = fund_upper_bound - fund_lower_bound

                draw_fund_bin = True
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
            draw_y += box_height

            if box_y < min_y:
                min_y = box_y

            if box_y + box_height > max_y:
                max_y = box_y + box_height

        encoder_count += 1

    if len(patches) > 0:
        ax.add_collection(PatchCollection(patches, match_original=True))

    draw_bound_y = 0
    prev_bound_y = 0

    if draw_h_border:
        ax.hlines(y=draw_bound_y, xmin=xmin, xmax=xmax, alpha=1.0, linewidth=0.5, color='k', zorder=-1)

    for e in sub_encoders:
        e_boundaries = e.region_boundaries
        draw_bound_y += box_height * len(e.bins)

        if draw_region_by_encoder:
            ax.vlines(x=e_boundaries, ymin=prev_bound_y, ymax=draw_bound_y, alpha=0.2, linewidth=0.5, color='k',
                      zorder=-1)

        if draw_h_grid:
            for k in range(len(e.bins)):
                ax.hlines(y=prev_bound_y + k, xmin=xmin, xmax=xmax, alpha=0.5, linewidth=0.5, color='k', zorder=-1)

            ax.hlines(y=draw_bound_y, xmin=xmin, xmax=xmax, alpha=1.0, linewidth=0.5, color='k', zorder=-1)

        prev_bound_y = draw_bound_y

    if draw_regions:
        boundaries = encoder.region_boundaries
        n_bits = encoder.n
        for k in range(len(boundaries)):
            ax.vlines(x=boundaries[k], ymin=0, ymax=n_bits, alpha=0.2, linewidth=0.5, color='k', zorder=-1)
        for k in range(n_bits + 1):
            ax.hlines(y=k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    return max_y, min_y


def draw_decomposition(ax, boundaries, text_v_offset=-0.01):
    x_point_vals = []
    y_point_vals = []
    for j in range(0, len(boundaries)):
        x_point_vals.append(boundaries[j])
        y_point_vals.append(boundaries[j])

    # number of points
    num_points = len(x_point_vals)

    frac_sum = Fraction(0)

    for j in range(1, num_points):
        origin_point = (x_point_vals[j - 1], 0.0)
        width = x_point_vals[j] - x_point_vals[j - 1]
        height = 1

        frac = Fraction(str(width)).limit_denominator(1000)
        frac_sum = frac_sum + frac
        text_str = "%d\n--\n%d" % (frac.numerator, frac.denominator)

        # create rectangle with text inside
        add_text_rect(ax, origin_point[0], origin_point[1], width, height, angle=0, linewidth=1.5, edgecolor='k',
                      fontsize=8, facecolor='none', alpha=1.0, text_str=text_str, text_v_offset=text_v_offset)


def draw_barcode(ax, X_gnomes):
    """
    Draw barcode image of encodings

    :param ax:
    :param X_gnomes:
    :return:
    """

    state_data = np.rot90(X_gnomes, k=-1, axes=(1, 0))
    barprops = dict(cmap='binary', interpolation='nearest', aspect='auto',
                    extent=[0, state_data.shape[1], 0, state_data.shape[0]])
    img = ax.imshow(state_data, **barprops)


def draw_delta_count(ax, boundary_x, grid_delta_counts):
    """
    Draw histogram plot of number of crossings

    :param ax:
    :param boundary_x:
    :param grid_delta_counts:
    :return:
    """

    tick_points_x = []
    tick_points_y = []

    for k in range(len(grid_delta_counts)):
        count = grid_delta_counts[k]
        x_val = boundary_x[k]

        tick_points_x += [x_val for j in range(count)]
        tick_points_y += [j + 1 for j in range(count)]

    # FIXME: does this scatter() belong here?
    ax.scatter(tick_points_x, tick_points_y, color='k')
    ax.bar(tick_points_x, tick_points_y, color='k')


def draw_similarity(ax, encoder, ref_points, colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True):
    """
    Draw count similarity of reference values to existing encodings

    :param ax:
    :param encoder:
    :param ref_points:
    :param colors:
    :param draw_regions:
    :param draw_h_grid:
    :param draw_v_values:
    :return:
    """
    boundaries = encoder.region_boundaries
    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    # region_codes = self.encode(self.region_centers)
    X_gnomes = encoder.region_codes

    # reference points for comparison
    ref_gnomes = encoder.encode(ref_points)

    # count similarity scores
    scores2 = count_similarity(X_gnomes, ref_gnomes)

    # for plotting purposes
    X_point_lower = lower_bound - 0.5
    X_point_upper = upper_bound + 0.5
    X_gnome_lower = encoder.encode(X_point_lower).reshape(1, -1)
    X_gnome_upper = encoder.encode(X_point_upper).reshape(1, -1)
    X_gnomes_extended = np.concatenate(
            (X_gnome_lower, X_gnomes, X_gnome_upper), axis=0)
    boundaries_extended = np.concatenate(
            ([lower_bound - 1.0], encoder.region_boundaries, [upper_bound + 1.0]))

    scores_extended = count_similarity(X_gnomes_extended, ref_gnomes)

    # data to plot
    max_score = np.max(scores2)

    # scale y-axis to maximum of weight
    ax.set_ylim(-0.1, max_score + 2)
    ax.yaxis.set_major_locator(ticker.IndexLocator(2, 1))
    ax.set_ylabel("Similarity of\nExample Values")

    # plot similarity scores for each reference value
    for k in range(len(ref_points)):
        boundaries_x = boundaries_extended
        scores_y = np.append(scores_extended[:, k], [scores_extended[-1, k], ])

        ax.step(boundaries_x, scores_y, where='post', color=colors[k], label=float(ref_points[k]))
        ax.fill_between(boundaries_x, -1, scores_y, step='post', color=colors[k], alpha=0.3, zorder=1)

    if draw_v_values:
        # draw vertical line indicating reference value on x-axis
        for k in range(len(ref_points)):
            ax.axvline(x=ref_points[k], ymax=3.2, alpha=1.0, linewidth=1.5, color=colors[k], linestyle='--',
                       clip_on=False)

    if draw_regions:
        # draw boundaries between each region
        for k in range(len(boundaries)):
            ax.axvline(x=boundaries[k], alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    if draw_h_grid:
        for k in range(max_score + 3):
            ax.hlines(y=k, xmin=lower_bound - 0.1, xmax=upper_bound + 0.1, alpha=0.2, linewidth=0.5, color='k',
                      zorder=-1)

    # show legend for each example value
    handles, labels = ax.get_legend_handles_labels()
    handles.reverse()
    labels.reverse()
    legend = ax.legend(handles, labels, title="Similarity of", ncol=2, fontsize=8, title_fontsize=8)


def draw_similarity_heatmap(ax, encoder, ref_point, colors, draw_regions=True,
                            draw_v_values=True, clip_on=True, xmin=None, xmax=None):
    """
    Draw count similarity of reference values to existing encodings

    :param ax:
    :param encoder:
    :param ref_point:
    :param colors:
    :param draw_regions:
    :param draw_v_values:
    :return:
    """

    # FIXME: generate extra regions and similarity scores up to xmin and xmax

    boundaries = encoder.region_boundaries
    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound

    # reference points for comparison
    ref_gnome = encoder.encode(ref_point)

    X_gnomes = encoder.region_codes

    # count similarity scores
    scores2 = count_similarity(X_gnomes, ref_gnome)

    # maximum data score for normalization
    max_score = np.max(scores2)

    # scale y-axis to boundaries of axes
    ax.tick_params(**{'right': False, 'labelright': False})
    ax.set_ylabel("Similarity of\nExample Values")

    ymin, ymax = ax.get_ybound()
    ax.set_ylim(ymin, ymax)

    box_height = ymax - ymin

    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)

    # shrink the boxes by this amount
    # x_shrink = x_pad * 2.0
    x_shrink = 0

    # record region center points
    sample_points = encoder.region_centers
    X_points = sample_points.reshape(-1, 1)

    region_widths = np.diff(encoder.region_boundaries)

    patches = []
    for k in range(len(X_points)):
        x_val = float(X_points[k])
        score = scores2[k][0] / max_score

        sample_upper_bound = x_val + region_widths[k] / 2.0
        sample_lower_bound = x_val - region_widths[k] / 2.0
        box_x = sample_lower_bound
        box_width = region_widths[k]

        do_draw = True

        # check there's a positive width rectangle to draw within axes bounds
        if clip_on:
            try:
                box_x, box_width = clip_bin(sample_lower_bound, sample_upper_bound, xmin, xmax)
            except:
                do_draw = False

        if do_draw:
            # box_y = 0
            box_y = ymin

            box_width_shrunk = box_width - x_shrink
            x_shrink_adj = x_shrink
            if box_width_shrunk < x_shrink:
                x_shrink_adj = 0.4 * box_width

            x_adj = box_x + x_shrink_adj / 2.0
            y_adj = box_y
            w_adj = box_width - x_shrink_adj
            # h_adj = box_height
            h_adj = box_height

            # print("color:", score, cmap(score))

            # create box representing the bin
            rect = new_rect(x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor=cmap(score), clip_on=clip_on,
                            linewidth=0)
            patches.append(rect)

    ax.add_collection(PatchCollection(patches, match_original=True))

    # plot similarity scores for each reference value
    # boundaries_x = boundaries_extended
    # scores_y = np.append(scores_extended, [scores_extended[-1], ])
    # ax.step(boundaries_x, scores_y, where='post', color=colors[0], label=float(ref_point))
    # ax.fill_between(boundaries_x, -1, scores_y, step='post', color=colors[0], alpha=0.3, zorder=1)

    if draw_v_values:
        # draw vertical line indicating reference value on x-axis
        ax.axvline(x=ref_point, ymin=ymin, ymax=3.2, alpha=1.0, linewidth=1.5, color=colors[0], linestyle='--',
                   clip_on=False, zorder=23)

        # ax.axvline(x=encoder.upper_bound, ymax=4.3, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    if draw_regions:
        # draw boundaries between each region
        for k in range(len(boundaries)):
            ax.axvline(x=boundaries[k], alpha=0.9, linewidth=0.5, color='k', zorder=3)
            # ax.axvline(x=boundaries[k], alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    # show legend for each example value
    # handles, labels = ax.get_legend_handles_labels()
    # handles.reverse()
    # labels.reverse()
    # legend = ax.legend(handles, labels, title="Similarity of", ncol=2, fontsize=8, title_fontsize=8)


def draw_features(ax, encoder, colors, markersize=4, draw_regions=False, draw_h_grid=True, draw_legend=True):
    """
    Features Subplot (Boundaries, Weight, Crossings)

    :param ax:
    :param encoder:
    :param lower_bound:
    :param upper_bound:
    :param colors:
    :param markersize:
    :param draw_regions:
    :param draw_h_grid:
    :return:
    """

    # boundaries and crossings
    boundaries = encoder.region_boundaries
    deltas = encoder.region_deltas
    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    # Data for Features
    bin_weights = encoder.region_weights
    max_bin_weight = max(bin_weights)
    bin_weights_y = np.append(bin_weights, [bin_weights[-1], ])

    # scale y-axis properties
    ax.set_ylim(-0.1, max_bin_weight + 2)
    ax.yaxis.set_major_locator(ticker.IndexLocator(2, 0))
    ax.set_ylabel("Features of\nEncodings")

    # set central ordinal value on y-axis for swarmplot
    bottom, top = ax.get_ylim()
    swarm_ordinal = (top - bottom) / 2.0 + bottom

    # points repeated for each delta count
    repeat_boundaries = []
    for k in range(len(deltas)):
        count = deltas[k]
        for j in range(count):
            repeat_boundaries.append(boundaries[k])

    # ordinal number that we want swarm points to be plotted on the y-axis
    y_vals = [swarm_ordinal for k in range(len(repeat_boundaries))]

    # NOTE: hacked seaborn by adding a second category with ordinal number out of plot range.
    #  Enables swarm points beyond unit category range
    #  This point is plotted, but not seen since '-100' is far out of axes y-range
    repeat_boundaries.append(0.0)
    y_vals.append(-100)

    # do swarm plot
    sns.swarmplot(x=repeat_boundaries, y=y_vals, orient='h', color=colors[0], ax=ax, size=markersize, native_scale=True,
                  legend=False, label="Crossings")

    # remove extra category
    repeat_boundaries.pop(-1)
    y_vals.pop(-1)

    if draw_regions:
        # draw grid lines representing boundaries between regions
        ax.axvline(x=boundaries[0], alpha=0.2, linewidth=0.5, color='k', zorder=-1, label="Boundary")
        for k in range(1, len(boundaries)):
            ax.axvline(x=boundaries[k], alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    if draw_h_grid:
        for k in range(0, max_bin_weight + 3):
            ax.hlines(y=k, xmin=lower_bound - 0.1, xmax=upper_bound + 0.1, alpha=0.2, linewidth=0.5, color='k',
                      zorder=-1)

    # draw gnome weights
    ax.step(boundaries, bin_weights_y, where='post', color=colors[1], alpha=0.6, zorder=1, label="Weight")
    ax.fill_between(boundaries, -1, bin_weights_y, step='post', color=colors[1], alpha=0.3, zorder=1)

    # legend labels and handles
    handles1, labels1 = ax.get_legend_handles_labels()

    # remove the hackish category label, so we only have one "Crossings" in the legend
    min_category = -1
    min_elements = 1e100
    for k in range(len(labels1)):
        if labels1[k] == "Crossings":
            handle = handles1[k]
            num_points = len(handle.get_offsets())
            if num_points < min_elements:
                min_elements = num_points
                min_category = k
    handles1.pop(min_category)
    labels1.pop(min_category)

    if draw_legend:
        # plot legend for property data
        legend = ax.legend(handles1, labels1, title="Features", ncol=3, fontsize=8, title_fontsize=9)


def draw_code_self_similarity(ax, encoder, triangle=False, annot=True):
    # sampled points over the space
    X_gnomes1 = encoder.region_codes

    diagonal_scores = count_similarity(X_gnomes1, X_gnomes1)
    max_count = np.max(diagonal_scores)

    # Generate a mask for the upper triangle
    if triangle:
        shape_mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    else:
        shape_mask = np.zeros_like(diagonal_scores, dtype=bool)
    mask = shape_mask

    # omit zero text data
    scores_text = diagonal_scores.astype('|S10')
    if annot:
        annot_data = np.where(diagonal_scores > 0, scores_text, '')
    else:
        annot_data = False

    # Generate a custom diverging colormap
    # cmap = sns.diverging_palette(230, 20, as_cmap=True)
    # cmap = sns.color_palette("rocket_r", as_cmap=True)
    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)

    num_points = X_gnomes1.shape[0]

    linewidths = 0
    fontsize = 0

    if num_points < 80:
        linewidths = 2. / num_points
        fontsize = 32. * 8. / num_points
    else:
        annot_data = False

    # find closest tick count to 20
    tick_counts = [5, 10, 50, 100, 500, 100, 500, 1000]

    minDist = 1e100
    tick_index = -1
    for k in range(len(tick_counts)):
        result = abs(20.0 - num_points / tick_counts[k])
        print(k, tick_counts[k], result)

        if result < minDist:
            minDist = result
            tick_index = k

    print("suggested tick count:", tick_counts[tick_index], num_points)
    #print(diagonal_scores)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(diagonal_scores, ax=ax, mask=mask, cmap=cmap, vmax=max_count, fmt="s",
                square=True, linewidths=linewidths, cbar_kws={"shrink": .5}, annot=annot_data,
                xticklabels=tick_counts[tick_index], yticklabels=tick_counts[tick_index],
                annot_kws={"fontsize": fontsize})


def draw_projected_self_similarity(ax, encoder, triangle=False, annot=True, cbar=True, cbar_ax=None):
    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)
    X_gnomes1 = encoder.region_codes
    X_gnomes2 = encoder.encode(X_points)

    x_vals = encoder.region_boundaries
    y_vals = encoder.region_boundaries

    x_centers = encoder.region_centers
    y_centers = encoder.region_centers

    x_sizes = encoder.region_sizes
    y_sizes = encoder.region_sizes

    diagonal_scores = count_similarity(X_gnomes1, X_gnomes2)
    max_count = np.max(diagonal_scores)

    # Generate a mask for the upper triangle
    if triangle:
        mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    else:
        mask = np.zeros_like(diagonal_scores, dtype=bool)

    masked_scores = ma.array(diagonal_scores, mask=mask)

    # Generate a custom diverging colormap
    # cmap = sns.diverging_palette(230, 20, s=75, l=50, as_cmap=True)
    # cmap = sns.diverging_palette(230, 20, s=100, as_cmap=True)
    # cmap = sns.color_palette("rocket_r", as_cmap=True)
    # cmap = sns.color_palette("Reds", as_cmap=True)
    # cmap = sns.light_palette("red", as_cmap=True)
    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)

    # Recenter a divergent colormap
    """
    if True:
        # noinspection PyUnreachableCode
        vmax = max_count
        vmin = 0
        # center = mean_count
        center = 0
        # Copy bad values
        # in mpl<3.2 only masked values are honored with "bad" color spec
        # (see https://github.com/matplotlib/matplotlib/pull/14257)
        bad = cmap(np.ma.masked_invalid([np.nan]))[0]

        # under/over values are set for sure when cmap extremes
        # do not map to the same color as +-inf
        under = cmap(-np.inf)
        over = cmap(np.inf)
        under_set = under != cmap(0)
        over_set = over != cmap(cmap.N - 1)

        vrange = max(vmax - center, center - vmin)
        normlize = mpl.colors.Normalize(center - vrange, center + vrange)
        cmin, cmax = normlize([vmin, vmax])
        cc = np.linspace(cmin, cmax, 256)
        new_cmap = mpl.colors.ListedColormap(cmap(cc))
        new_cmap.set_bad(bad)
        if under_set:
            new_cmap.set_under(under)
        if over_set:
            new_cmap.set_over(over)

        cmap = new_cmap
    """

    num_points = X_points.shape[0]

    if num_points < 80:
        linewidth = 2. / num_points
    else:
        linewidth = 0

    # seaborn data-mangling (converts to dataframe everything)
    # plot_data = np.asarray(data)
    # data = pd.DataFrame(plot_data)
    # mask = _matrix_mask(data, mask) # Validate the mask and convert to DataFrame
    # plot_data = np.ma.masked_where(np.asarray(mask), plot_data)
    # mesh = ax.pcolormesh(plot_data, cmap=cmap, **kws)

    mesh = ax.pcolormesh(x_vals, y_vals, masked_scores, vmax=max_count, vmin=0, edgecolor='1.0', linewidth=linewidth,
                         cmap=cmap)

    if cbar:
        # add colorbar to the figure, creating a separate axes and repositioning original axes
        cb = ax.figure.colorbar(mesh, ax=ax, cax=cbar_ax, shrink=0.5)  # , spacing="uniform", drawedges=True)
        cb.outline.set_linewidth(0)

    # add text box to center of each rectangle indicating count similarity
    if annot:

        # code to change the color of the text depending on cell color
        # lum = relative_luminance(color)
        # text_color = ".15" if lum > .408 else "w"
        text_color = ".15"
        # text_color = "w"

        for i in range(len(x_centers)):
            x = x_centers[i]
            x_size = x_sizes[i]

            for j in range(len(y_centers)):
                y = y_centers[j]
                y_size = y_sizes[j]
                score = masked_scores[j, i]

                min_size = min(x_size, y_size)

                draw_text = True
                if num_points < 80:
                    fontsize = min_size * 4. * 32. / 0.2
                else:
                    fontsize = 0
                    draw_text = False

                if draw_text and score is not np.ma.masked and score > 0:
                    ax.text(x, y, str(score), horizontalalignment='center', verticalalignment='center',
                            fontsize=fontsize, color=text_color)


def new_rect(box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k',
             facecolor='none', alpha=1.0, clip_on=False, label=None, zorder=1):
    # add rectangle at corner position and rotate by angle
    return patches.Rectangle((box_x, box_y), box_width, box_height, angle=angle, linewidth=linewidth,
                             edgecolor=edgecolor,
                             facecolor=facecolor, clip_on=clip_on, alpha=alpha, label=label, zorder=zorder)


def add_text_rect(ax, box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k', fontsize=8,
                  facecolor='none', text_str=None, aligned_text=False, alpha=1.0, text_v_offset=-0.01, clip_on=False,
                  label=None, zorder=None):
    # Add Rectangle

    # create rectangle
    rect = new_rect(box_x, box_y, box_width, box_height, angle=angle, linewidth=linewidth,
                    edgecolor=edgecolor, facecolor=facecolor, alpha=alpha, clip_on=clip_on,
                    label=label, zorder=zorder)
    # add to axes
    ax.add_patch(rect)

    # Add Text

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
            fontsize=fontsize, va='center', ha='center', clip_on=clip_on, alpha=alpha, zorder=zorder)
