from matplotlib import ticker
from matplotlib.transforms import Affine2D
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.axes
import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns
import string

import numpy as np
from fractions import Fraction

from .helpers import *

# printing boolean arrays neatly
np.set_printoptions(
    precision=3, suppress=True, threshold=1000000, linewidth=400,
    formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


def draw_bits_by_data(ax: mpl.axes.Axes, encoder, draw_uniform_samples=False, draw_region_bits=False,
                      draw_boundaries=True, draw_bit_grid=True, permute_bits=False, xmin=None, xmax=None, clip_on=True,
                      box_height=1, num_samples=150, x_pad=0.002, y_pad=0.15):
    """

    :param ax: mpl.axes.Axes
    :param encoder: encoders.encoders.EncoderBase
    :param xmin: float | None
    :param xmax: float | None
    :param clip_on: bool
    """

    # TODO: optionally permutate bits to show non-local vs. sorted visualization
    # TODO: sampled bits option, showing bits in grid instead of bars representing the bins
    # TODO: properly clip and no-clip the bits beyond the interval

    n_bits = encoder.n

    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound
    interval_length = upper_bound - lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound


    # scale y-axis to number of bits
    ax.yaxis.set_major_locator(ticker.IndexLocator(5, 0))
    ax.set_ylim(-0.5, n_bits + 0.5)
    ax.set_ylabel("Bit Encoding vs.\nReal Value")
    ax.set_xlim(xmin, xmax)

    indices = np.random.permutation(np.arange(n_bits))

    if draw_uniform_samples and draw_region_bits:
        raise Exception("Both sampling and regions selected, only one permitted.")

    if draw_uniform_samples:
        # 150 samples is about right for square-ish bit plotting
        sample_spacing = interval_length / num_samples

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
                # case 1: bin exceeds lower bound
                if sample_lower_bound < lower_bound:
                    sample_lower_bound = lower_bound

                    if sample_upper_bound < lower_bound:
                        # TODO: box_width should be zero, so don't draw
                        sample_upper_bound = lower_bound
                        do_draw = False

                    box_x = sample_lower_bound
                    box_width = sample_upper_bound - sample_lower_bound

                # case 2: bin exceeds interval upper bound
                elif sample_upper_bound > upper_bound:
                    sample_upper_bound = upper_bound

                    if sample_lower_bound > upper_bound:
                        # TODO: box_width should be zero, so don't draw
                        sample_lower_bound = upper_bound
                        do_draw = False

                    box_x = sample_lower_bound
                    box_width = sample_upper_bound - sample_lower_bound

                # case 3: bin within interval bounds
                else:
                    # change nothing
                    pass

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
                        rect = add_rect(ax, x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor='k', clip_on=clip_on, linewidth=0.2)
                        patches.append(rect)

                ax.add_collection(PatchCollection(patches, match_original=True))

    elif draw_region_bits:

        # shrink the the boxes by this amount
        y_shrink = y_pad * 2.0
        x_shrink = x_pad * 2.0

        # record region center points
        sample_points = encoder.region_centers
        X_points = sample_points.reshape(-1, 1)

        print("X_points:", X_points.shape)

        # encodings
        X_gnomes = encoder.region_codes
        print("X_gnomes:", X_gnomes.shape)

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
                # case 1: bin exceeds lower bound
                if sample_lower_bound < lower_bound:
                    sample_lower_bound = lower_bound

                    if sample_upper_bound < lower_bound:
                        # TODO: box_width should be zero, so don't draw
                        sample_upper_bound = lower_bound
                        do_draw = False

                    box_x = sample_lower_bound
                    box_width = sample_upper_bound - sample_lower_bound

                # case 2: bin exceeds interval upper bound
                elif sample_upper_bound > upper_bound:
                    sample_upper_bound = upper_bound

                    if sample_lower_bound > upper_bound:
                        # TODO: box_width should be zero, so don't draw
                        sample_lower_bound = upper_bound
                        do_draw = False

                    box_x = sample_lower_bound
                    box_width = sample_upper_bound - sample_lower_bound

                # case 3: bin within interval bounds
                else:
                    # change nothing
                    pass

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
                        rect = add_rect(ax, x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor='k', clip_on=clip_on, linewidth=0.2)
                        patches.append(rect)

                ax.add_collection(PatchCollection(patches, match_original=True))

    else:
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

                # case 1: bin exceeds lower bound
                if bin_lower_bound < lower_bound:
                    bin_lower_bound = lower_bound

                    if bin_upper_bound < lower_bound:
                        # TODO: box_width should be zero, so don't draw
                        bin_upper_bound = lower_bound
                        do_draw = False

                    box_x = bin_lower_bound
                    box_width = bin_upper_bound - bin_lower_bound

                # case 2: bin exceeds interval upper bound
                elif bin_upper_bound > upper_bound:
                    bin_upper_bound = upper_bound

                    if bin_lower_bound > upper_bound:
                        # TODO: box_width should be zero, so don't draw
                        bin_lower_bound = upper_bound
                        do_draw = False

                    box_x = bin_lower_bound
                    box_width = bin_upper_bound - bin_lower_bound

                # case 3: bin within interval bounds
                else:
                    # change nothing
                    pass

            if do_draw:

                # if permute_bits:
                #    box_y = indices[j] * box_height
                # else:
                #    box_y = j * box_height

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

                # create box representing the bin
                rect = add_rect(ax, x_adj, y_adj, w_adj, h_adj, alpha=1, facecolor='k', clip_on=clip_on, linewidth=0.2)
                patches.append(rect)

        ax.add_collection(PatchCollection(patches, match_original=True))
        y_index += 1

    if draw_boundaries:
        boundaries = encoder.region_boundaries
        for k in range(len(boundaries)):
            ax.vlines(x=boundaries[k], ymin=0, ymax=n_bits, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    if draw_bit_grid:
        for k in range(n_bits + 1):
            ax.hlines(y=k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)


def draw_encoder_bins(ax, encoder, xmin=None, xmax=None, clip_on=True, spacing=1, fontsize=8):
    # def add_text_rect(ax, box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k', fontsize=8,
    #              facecolor='none', text_str=None, aligned_text=False, alpha=1.0, text_v_offset=-0.01):

    min_y = 1
    max_y = 0

    n_bits = encoder.n
    boundaries = encoder.region_boundaries

    upper_bound = encoder.upper_bound
    lower_bound = encoder.lower_bound

    if xmax is None:
        xmax = upper_bound
    if xmin is None:
        xmin = lower_bound

    keys = [0, ]
    keys.sort()

    n_grids = 1
    grid_names = string.ascii_uppercase[:n_grids]

    colors = sns.color_palette("muted", n_colors=n_grids)
    grid_label_templates = [prefix + "%d" for prefix in grid_names]
    grid_colors = [colors[j] for j in range(n_grids)]

    grid_labels = ["%d,%d" % (keys[j], spacing) for j in range(n_grids)]

    encoder_count = 0
    bin_id_count = 0
    draw_y = 0.0
    # box_height = 0.3
    box_height = 1

    top_right_points_x = []
    top_right_points_y = []

    bin_count = 0

    # for i in range(0, len(encoder.region_boundaries)-1):
    for bin in encoder.bins:
        bin_upper_bound = bin.upper
        bin_lower_bound = bin.lower
        # lower_bound = encoder.region_boundaries[i]
        # upper_bound = encoder.region_boundaries[i+1]

        box_x = bin_lower_bound
        box_y = draw_y
        box_width = bin_upper_bound - bin_lower_bound

        # print("bin id, bin lower, bin upper, bin size:", bin_id_count, bin_lower_bound, bin_upper_bound, box_width)

        if clip_on:
            # case 1: bin exceeds lower bound
            if box_x < lower_bound:
                box_x = lower_bound
                box_width = bin_upper_bound - box_x

            # case 2: bin exceeds interval upper bound
            elif box_x + box_width > upper_bound:
                box_width = upper_bound - box_x

            # case 3: bin within interval bounds
            else:
                # do nothing
                pass

        """
        # only add label to first rectangle of encoder's bins
        if bin_count == 0:
            add_text_rect(ax, box_x, box_y, box_width, box_height, alpha=1, facecolor=grid_colors[encoder_count],
                          text_str=str(bin_id_count), clip_on=clip_on, linewidth=0.2, fontsize=fontsize,
                          label=grid_labels[encoder_count])
        else:
            add_text_rect(ax, box_x, box_y, box_width, box_height, alpha=1, facecolor=grid_colors[encoder_count],
                          text_str=str(bin_id_count), clip_on=clip_on, linewidth=0.2, fontsize=fontsize)
        # text_str=grid_label_templates[encoder_count] % bin_count, clip_on=clip_on, linewidth=0.2)
        """

        # shrink the the bins by this amount
        x_shrink = 0.004
        y_shrink = 0.3

        # only add label to first rectangle of encoder's bins
        if bin_count == 0:
            add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                          box_height - y_shrink, alpha=0.8, facecolor=grid_colors[encoder_count],
                          text_str=str(bin_id_count), clip_on=clip_on, linewidth=0.2, fontsize=fontsize,
                          label=grid_labels[encoder_count])
        else:
            add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                          box_height - y_shrink, alpha=0.8, facecolor=grid_colors[encoder_count],
                          text_str=str(bin_id_count), clip_on=clip_on, linewidth=0.2, fontsize=fontsize)
        # text_str=grid_label_templates[encoder_count] % bin_count, clip_on=clip_on, linewidth=0.2)

        bin_count += 1
        bin_id_count += 1
        draw_y += box_height

        if box_y < min_y:
            min_y = box_y

        if box_y + box_height > max_y:
            max_y = box_y + box_height

        # top_right_points_x.append(box_x+box_width)
        # top_right_points_y.append(box_y+box_height)

    # draw_y += box_height
    encoder_count += 1
    draw_y = box_height * encoder_count * spacing

    # ax.scatter(top_right_points_x, top_right_points_y, s=0.01)

    for k in range(len(boundaries)):
        ax.vlines(x=boundaries[k], ymin=0, ymax=n_bits, alpha=0.2, linewidth=0.5, color='k', zorder=-1)
    for k in range(n_bits + 1):
        ax.hlines(y=k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    return max_y, min_y


def draw_multi_encoder_bins(ax, encoder, xmin=None, xmax=None, clip_on=True, spacing=1, fontsize=8, draw_regions=False,
                            draw_h_grid=True, draw_h_border=True, draw_region_by_encoder=True):
    min_y = 1
    max_y = 0

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

    grid_labels = ["%d,%d" % (keys[j], spacing) for j in range(n_grids)]

    encoder_count = 0
    bin_id_count = 0
    draw_y = 0.0
    box_height = 1

    bin_count = 0



    for e in sub_encoders:
        for bin in e.bins:
            bin_upper_bound = bin.upper
            bin_lower_bound = bin.lower

            box_x = bin_lower_bound
            box_y = draw_y
            box_width = bin_upper_bound - bin_lower_bound

            if clip_on:
                # case 1: bin exceeds lower bound
                if box_x < lower_bound:
                    box_x = lower_bound
                    box_width = bin_upper_bound - box_x

                # case 2: bin exceeds interval upper bound
                elif box_x + box_width > upper_bound:
                    box_width = upper_bound - box_x

                # case 3: bin within interval bounds
                else:
                    # do nothing
                    pass

            # shrink the the bins by this amount
            x_shrink = 0.004
            y_shrink = 0.3

            # only add label to first rectangle of encoder's bins
            if bin_count == 0:
                add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                              box_height - y_shrink, alpha=0.8, facecolor=grid_colors[encoder_count],
                              text_str=str(bin_id_count), clip_on=clip_on, linewidth=0.2, fontsize=fontsize,
                              label=grid_labels[encoder_count])
            else:
                add_text_rect(ax, box_x + x_shrink / 2.0, box_y + y_shrink / 2.0, box_width - x_shrink,
                              box_height - y_shrink, alpha=0.8, facecolor=grid_colors[encoder_count],
                              text_str=str(bin_id_count), clip_on=clip_on, linewidth=0.2, fontsize=fontsize)
            # text_str=grid_label_templates[encoder_count] % bin_count, clip_on=clip_on, linewidth=0.2)

            bin_count += 1
            bin_id_count += 1
            draw_y += box_height

            if box_y < min_y:
                min_y = box_y

            if box_y + box_height > max_y:
                max_y = box_y + box_height

        encoder_count += 1
        #draw_y = box_height * encoder_count * spacing

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
                ax.hlines(y=prev_bound_y + k, xmin=xmin, xmax=xmax, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

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

        # text_v_offset = min(-0.1, -height / 1.2)
        # text_v_offset = min(-0.1, -height*0.55)
        # text_v_offset = 0.0

        frac = Fraction(str(width)).limit_denominator(1000)
        # print("%s" % str(frac))
        frac_sum = frac_sum + frac
        text_str = "%d\n--\n%d" % (frac.numerator, frac.denominator)
        # text_str += "\n\n\n%.2f" % width
        # text_str = "%d\n\u2014\n%d" % (frac.numerator, frac.denominator)

        # create rectangle with text inside
        # add_text_rect(ax1, origin_point[0], origin_point[1], width, height, angle=0, linewidth=1.5, edgecolor='k',
        #              fontsize=8, facecolor='none', text_str="%.2f" % width, alpha=1.0,
        #              text_v_offset=text_v_offset)

        add_text_rect(ax, origin_point[0], origin_point[1], width, height, angle=0, linewidth=1.5, edgecolor='k',
                      fontsize=8, facecolor='none', alpha=1.0, text_str=text_str, text_v_offset=text_v_offset)

    # print("total sum = %s" % str(frac_sum))


def draw_decomposition2(ax, boundaries, height=1, text_v_offset=-0.01):
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

        # text_v_offset = min(-0.1, -height / 1.2)
        # text_v_offset = min(-0.1, -height*0.55)
        # text_v_offset = 0.0

        frac = Fraction(str(width)).limit_denominator(1000)
        # print("%s" % str(frac))
        frac_sum = frac_sum + frac
        text_str = "%d\n--\n%d" % (frac.numerator, frac.denominator)
        # text_str += "\n\n\n%.2f" % width
        # text_str = "%d\n\u2014\n%d" % (frac.numerator, frac.denominator)

        # create rectangle with text inside
        # add_text_rect(ax1, origin_point[0], origin_point[1], width, height, angle=0, linewidth=1.5, edgecolor='k',
        #              fontsize=8, facecolor='none', text_str="%.2f" % width, alpha=1.0,
        #              text_v_offset=text_v_offset)

        # add_text_rect(ax, origin_point[0], origin_point[1], width, height, angle=0, linewidth=1.5, edgecolor='k',
        add_text_rect(ax, origin_point[0], origin_point[1], width, height, angle=0, linewidth=0, edgecolor='k',
                      fontsize=8, facecolor='none', alpha=1.0, text_str=text_str, text_v_offset=text_v_offset)

    # print("total sum = %s" % str(frac_sum))


def draw_encoding(ax, X_gnomes):
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

    # ax.scatter(tick_points_x, tick_points_y, color='k')

    ax.bar(tick_points_x, tick_points_y, color='k')


def draw_similarity(ax, encoder, X_gnomes, ref_points, colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True):
    """
    Draw count similarity of reference values to existing encodings

    :param ax:
    :param encoder:
    :param X_gnomes: encoded points over the space
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

    # reference points for comparison
    ref_gnomes = encoder.encode(ref_points)

    # count similarity scores
    #scores = gnome_similarity(X_gnomes, ref_gnomes)
    scores2 = count_similarity(X_gnomes, ref_gnomes)

    # for plotting purposes
    X_point_lower = lower_bound - 0.5
    X_point_upper = upper_bound + 0.5
    X_gnome_lower = encoder.encode(X_point_lower).reshape(1, -1)
    X_gnome_upper = encoder.encode(X_point_upper).reshape(1, -1)
    # X_points_extended = np.concatenate(
    #    ([X_point_lower], encoder.region_centers, [X_point_upper]))
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


def draw_features(ax, encoder, colors, markersize=4, draw_regions=False, draw_h_grid=True):
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

    # plot legend for property data
    legend = ax.legend(handles1, labels1, title="Features", ncol=3, fontsize=8, title_fontsize=9)

def add_rect(ax, box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k',
                  facecolor='none', alpha=1.0, clip_on=False, label=None):

    # add rectangle at corner position and rotate by angle
    rect = patches.Rectangle((box_x, box_y), box_width, box_height, angle=angle, linewidth=linewidth,
                             edgecolor=edgecolor,
                             facecolor=facecolor, clip_on=clip_on, alpha=alpha, label=label)
    return rect

def add_text_rect(ax, box_x, box_y, box_width, box_height, angle=0, linewidth=1.5, edgecolor='k', fontsize=8,
                  facecolor='none', text_str=None, aligned_text=False, alpha=1.0, text_v_offset=-0.01, clip_on=False,
                  label=None):

    # data space coordinates to find new point after rotated
    fixed_point_rotation = Affine2D().rotate_deg_around(box_x, box_y, angle)

    # add rectangle at corner position and rotate by angle
    rect = patches.Rectangle((box_x, box_y), box_width, box_height, angle=angle, linewidth=linewidth,
                             edgecolor=edgecolor,
                             facecolor=facecolor, clip_on=clip_on, alpha=alpha, label=label)
    ax.add_patch(rect)

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
            fontsize=fontsize, va='center', ha='center', clip_on=clip_on, alpha=alpha)


    #return rect


