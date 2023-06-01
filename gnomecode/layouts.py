# plotting

import re
import textwrap
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from line_profiler_pycharm import profile
from matplotlib import ticker

from .axesplots import *

__all__ = ['plot_diff_heatmap', 'plot_code_heatmap', 'plot_realspace_heatmap', 'plot_interval_multi_encoder',
           'save_fig', 'plot_compact_multi_encoder', 'plot_periodic_cell_multi_encoder']


@profile
def save_fig(path, encoder, plot_name, do_close=True, w_param=None):
    # if w_param:
    #     file_path = path + "%03u_%04u_" % (
    #             encoder.n, w_param) + plot_name + "_" + experiment_name + ".png"
    # else:
    #     file_path = path + "%03u_%04u_" % (
    #             encoder.n, len(encoder.region_centers)) + plot_name + "_" + experiment_name + ".png"

    if w_param:
        file_path = path + "%03u_%04u_" % (
                encoder.n, w_param) + plot_name + ".png"
    else:
        file_path = path + "%03u_%04u_" % (
                encoder.n, len(encoder.region_centers)) + plot_name + ".png"

    # print(plt.gcf().get_size_inches())

    plt.savefig(file_path, bbox_inches='tight')
    # plt.savefig(file_path)

    # print(plt.gcf().get_size_inches())

    if do_close:
        plt.close()
        sns.reset_defaults()

    return file_path


@profile
def plot_diff_heatmap(encoder, desc_str="Encoder", triangle=False, annot=True, draw_manual_grid=True,
                      draw_minor_tick_grid=False):
    y_spacing = 0.05
    inset_fraction = 0.25

    # Start with a square Figure and add a couple extra inches to top
    fig = plt.figure(figsize=(9, 12), constrained_layout=True)

    ax_heatmap = fig.add_gridspec(top=0.75, right=0.75).subplots()
    ax_heatmap.set(aspect=1)

    plot_up = True
    if plot_up:
        ax_features = ax_heatmap.inset_axes([0, 1.0 + y_spacing, 1, inset_fraction], sharex=ax_heatmap)  # plot on top
    else:
        ax_features = ax_heatmap.inset_axes([0, -inset_fraction - y_spacing, 1, inset_fraction],
                                            sharex=ax_heatmap)  # plot on bottom

    # title of figure
    fig.suptitle(desc_str)

    # print("X_gnomes:", encoder.region_codes.shape)

    draw_code_difference(ax_heatmap, encoder, triangle=triangle, annot=annot)

    # redraw tick locations because seaborn heatmap shifts them by 0.5
    ax_heatmap.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax_heatmap.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax_heatmap.xaxis.set_major_formatter(lambda x, pos: str(int(x)))
    ax_heatmap.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax_heatmap.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax_heatmap.yaxis.set_major_formatter(lambda x, pos: str(int(x)))

    # restore bounding box lines
    ax_heatmap.spines['top'].set_visible(True)
    ax_heatmap.spines['right'].set_visible(True)
    ax_heatmap.spines['bottom'].set_visible(True)
    ax_heatmap.spines['left'].set_visible(True)

    draw_barcode(ax_features, encoder.region_codes)

    # redraw tick locations because seaborn heatmap shifts them by 0.5
    ax_features.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    ax_features.xaxis.set_minor_locator(ticker.IndexLocator(1, 0))

    grid_linewidth = 0.3
    grid_alpha = 0.2

    if draw_manual_grid:
        num_points = encoder.region_codes.shape[0]
        xmin, xmax = ax_features.get_xbound()
        ymin, ymax = ax_features.get_ybound()
        for k in range(num_points):
            ax_features.axvline(x=k, ymin=ymin, ymax=ymax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                                zorder=1)

        num_bits = encoder.region_codes.shape[1]
        for k in range(num_bits):
            ax_features.axhline(y=k, xmin=xmin, xmax=xmax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                                zorder=1)

        xmin, xmax = ax_heatmap.get_xbound()
        ymin, ymax = ax_heatmap.get_ybound()
        for k in range(num_points):
            ax_heatmap.axvline(x=k, ymin=ymin, ymax=ymax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                               zorder=1)
            ax_heatmap.axhline(y=k, xmin=xmin, xmax=xmax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                               zorder=1)

    elif draw_minor_tick_grid:
        ax_features.grid(visible=True, which='minor', axis='x', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                         zorder=1)
        ax_heatmap.grid(visible=True, which='minor', axis='both', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                        zorder=1)


@profile
def plot_code_heatmap(encoder, desc_str="Encoder", triangle=False, annot=True, draw_manual_grid=True,
                      draw_minor_tick_grid=False):
    y_spacing = 0.05
    inset_fraction = 0.25

    # Start with a square Figure and add a couple extra inches to top
    fig = plt.figure(figsize=(9, 12), constrained_layout=True)

    ax_heatmap = fig.add_gridspec(top=0.75, right=0.75).subplots()
    ax_heatmap.set(aspect=1)

    plot_up = True
    if plot_up:
        ax_features = ax_heatmap.inset_axes([0, 1.0 + y_spacing, 1, inset_fraction], sharex=ax_heatmap)  # plot on top
    else:
        ax_features = ax_heatmap.inset_axes([0, -inset_fraction - y_spacing, 1, inset_fraction],
                                            sharex=ax_heatmap)  # plot on bottom

    # title of figure
    fig.suptitle(desc_str)

    draw_code_self_similarity(ax_heatmap, encoder, triangle=triangle, annot=annot)

    # redraw tick locations because seaborn heatmap shifts them by 0.5
    ax_heatmap.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax_heatmap.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax_heatmap.xaxis.set_major_formatter(lambda x, pos: str(int(x)))
    ax_heatmap.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax_heatmap.yaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax_heatmap.yaxis.set_major_formatter(lambda x, pos: str(int(x)))

    # restore bounding box lines
    ax_heatmap.spines['top'].set_visible(True)
    ax_heatmap.spines['right'].set_visible(True)
    ax_heatmap.spines['bottom'].set_visible(True)
    ax_heatmap.spines['left'].set_visible(True)

    draw_barcode(ax_features, encoder.region_codes)

    # redraw tick locations because seaborn heatmap shifts them by 0.5
    ax_features.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    ax_features.xaxis.set_minor_locator(ticker.IndexLocator(1, 0))

    grid_linewidth = 0.3
    grid_alpha = 0.2

    if draw_manual_grid:
        num_points = encoder.region_codes.shape[0]
        xmin, xmax = ax_features.get_xbound()
        ymin, ymax = ax_features.get_ybound()
        for k in range(num_points):
            ax_features.axvline(x=k, ymin=ymin, ymax=ymax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                                zorder=1)

        num_bits = encoder.region_codes.shape[1]
        for k in range(num_bits):
            ax_features.axhline(y=k, xmin=xmin, xmax=xmax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                                zorder=1)

        xmin, xmax = ax_heatmap.get_xbound()
        ymin, ymax = ax_heatmap.get_ybound()
        for k in range(num_points):
            ax_heatmap.axvline(x=k, ymin=ymin, ymax=ymax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                               zorder=1)
            ax_heatmap.axhline(y=k, xmin=xmin, xmax=xmax, alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                               zorder=1)

    elif draw_minor_tick_grid:
        ax_features.grid(visible=True, which='minor', axis='x', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                         zorder=1)
        ax_heatmap.grid(visible=True, which='minor', axis='both', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                        zorder=1)


@profile
def plot_realspace_heatmap(encoder, desc_str="Encoder", triangle=False, annot=True, draw_manual_grid=True,
                           draw_minor_tick_grid=False, w_param=None, do_inset_axes=False):
    n_bits = encoder.n

    y_spacing = 0.03
    inset_fraction = 0.25

    # plot range for this multi encoder
    try:
        # if xmin/xmax doesn't exist, use input bounds
        xmin = encoder.xmin
        xmax = encoder.xmax
    except AttributeError:
        xmin = encoder.lower_bound
        xmax = encoder.upper_bound

    if do_inset_axes:

        fig = plt.figure(figsize=(10, 7), dpi=300, constrained_layout=True)

        ax_heatmap = fig.add_gridspec(top=0.75, right=0.75).subplots()
        ax_heatmap.set(aspect=1)

        plot_up = True
        if plot_up:
            ax_features = ax_heatmap.inset_axes([0, 1.0 + y_spacing, 1, inset_fraction],
                                                sharex=ax_heatmap)  # plot on top
        else:
            ax_features = ax_heatmap.inset_axes([0, -inset_fraction - y_spacing, 1, inset_fraction],
                                                sharex=ax_heatmap)  # plot on bottom

        ax_colorbar = ax_heatmap.inset_axes([1.03, 0.23, 0.023, 0.54])

    else:

        # #figure.figsize:     6.4, 4.8  # figure size in inches
        # #figure.dpi:         100       # figure dots per inch

        # Start with a square Figure and add a couple extra inches to top
        #  figsize=(10, 8), dpi=300,
        # fig = plt.figure(figsize=(9, 12), dpi=300, constrained_layout=True)
        # fig = plt.figure(figsize=(10, 15), dpi=300, constrained_layout=True)
        # fig = plt.figure(figsize=(10, 15), dpi=300)
        # fig = plt.figure(figsize=(10, 7), dpi=300, constrained_layout=True)

        fig, ax_heatmap = plt.subplots(1, 1, num=1, figsize=(10, 7), dpi=300, constrained_layout=True)
        ax_heatmap.set(aspect=1)

        ax_colorbar = ax_heatmap.inset_axes([1.03, 0.23, 0.023, 0.54])

        # no inset axes
        ax_features = None

    ax_heatmap.invert_yaxis()

    # set title of whole figure
    if w_param:
        fig.suptitle("%s, n=%d, w=%d" % (desc_str, n_bits, w_param))
    else:
        fig.suptitle("%s, n=%d" % (desc_str, n_bits))

    # hide the spines
    # for side in ["top", "right", "bottom", "left"]:
    #    ax_heatmap.spines[side].set_visible(False)

    draw_projected_self_similarity(ax_heatmap, encoder, triangle=triangle, annot=annot, cbar=True, cbar_ax=ax_colorbar)

    # same tick configuration for each axes
    # tick_args = {'axis': 'both', 'which': 'both', 'labelsize': 'small', 'labelbottom': False, 'bottom': False,
    #             'left': False, 'labelleft': False, 'right': True, 'labelright': True}

    # Features Subplot (Boundaries, Weight, Crossings)
    # ax_features.tick_params(**tick_args)

    # share ax_heatmap and ax_features x-axis
    # ax_features.get_shared_x_axes().join(ax_features, ax_heatmap)

    if do_inset_axes:
        ax_features.set_xlim(xmin, xmax)
    else:
        ax_heatmap.set_xlim(xmin, xmax)

    # draw weight, crossings, and boundary features
    # markersize = 4
    # colors = sns.color_palette("Set1")  # , n_colors=oints))

    # draw minor tick locations for the region boundaries
    boundaries = encoder.region_boundaries

    if do_inset_axes:
        # draw_features(ax_features, encoder, colors, markersize, draw_regions=True, draw_legend=False)
        draw_bits_by_data(ax_features, encoder, draw_boundaries=False, draw_region_bits=True, draw_bit_grid=True,
                          x_pad=0,
                          y_margin=0, y_pad=0)

        ax_features.xaxis.set_minor_locator(ticker.FixedLocator(boundaries))
        ax_features.tick_params(which='major', labelbottom=False, bottom=False)

    ax_heatmap.yaxis.set_minor_locator(ticker.FixedLocator(boundaries))
    ax_heatmap.xaxis.set_minor_locator(ticker.FixedLocator(boundaries))

    # ax_features.xticks

    # ax_features.set_ylabel("Bit Encoding vs.\nReal Value")

    grid_linewidth = 0.3
    grid_alpha = 0.2

    if draw_manual_grid:
        if do_inset_axes:
            ymin, ymax = ax_features.get_ybound()
            for k in range(len(boundaries)):
                ax_features.axvline(x=boundaries[k], ymin=ymin, ymax=ymax, alpha=grid_alpha, linewidth=grid_linewidth,
                                    color='k', zorder=-1)

        xmin, xmax = ax_heatmap.get_xbound()
        ymin, ymax = ax_heatmap.get_ybound()
        for k in range(len(boundaries)):
            ax_heatmap.axvline(x=boundaries[k], ymin=ymin, ymax=ymax, alpha=grid_alpha, linewidth=grid_linewidth,
                               color='k', zorder=1)
            ax_heatmap.axhline(y=boundaries[k], xmin=xmin, xmax=xmax, alpha=grid_alpha, linewidth=grid_linewidth,
                               color='k', zorder=1)

    elif draw_minor_tick_grid:

        if do_inset_axes:
            ax_features.grid(visible=True, which='minor', axis='x', alpha=grid_alpha, linewidth=grid_linewidth,
                             color='k',
                             zorder=1)

        ax_heatmap.grid(visible=True, which='minor', axis='both', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                        zorder=1)

    # print(fig.get_size_inches())


@profile
def plot_interval_multi_encoder(encoder, desc_str="Encoder", x_pad=0.1, draw_folded_bins=False, w_param=None):
    n_bits = encoder.n
    n_grids = 1

    try:
        sub_encoders = encoder.encoders
        n_grids = len(sub_encoders)
    except:
        pass

    markersize = 4
    fontsize = 8

    # TODO: plot distribution of periods, bin sizes, offsets, duty cycles, of a multi-encoder

    # print(encoder.xmin, encoder.xmax, encoder.lower_bound, encoder.upper_bound)
    # for enc in encoder.encoders:
    #     try:
    #         print(enc.xmin, enc.xmax, enc.lower_bound, enc.upper_bound)
    #     except:
    #         print(enc.lower_bound, enc.upper_bound)

    # plot range for this multi encoder
    try:
        # if xmin/xmax doesn't exist, use input bounds
        xmin = encoder.xmin - x_pad
        xmax = encoder.xmax + x_pad
    except AttributeError:
        xmin = encoder.lower_bound - x_pad
        xmax = encoder.upper_bound + x_pad

    # print(xmin, xmax)
    # reference points for comparison
    ref_points = np.array([[0.21], [0.75]])

    n_points = len(ref_points)

    # color palette
    # colors = sns.color_palette("Set1", n_colors=len(ref_points))
    # colors = sns.color_palette("muted", n_colors=(n_grids+n_points))
    # colors = sns.color_palette("Set1", n_colors=(n_grids+n_points+2))
    # colors = sns.color_palette("cet_glasbey_hv", n_colors=(n_grids+n_points+2))
    # colors = sns.color_palette("cet_glasbey_hv", as_cmap=True).colors
    # colors = sns.color_palette("cet_glasbey_category10", as_cmap=True).colors
    colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors

    encoder_colors = colors[0:n_grids]
    # similarity_colors = colors[n_grids:n_grids+n_points]
    # feature_colors = colors[n_grids+n_points:n_grids+n_points+2]

    similarity_colors = colors[-2 - n_points:-2]
    feature_colors = colors[-2:]

    # seaborn style
    sns.set_theme(style="white")

    # # Draw Plots in Each SubAxes

    # subplot_kw, gridspec_kw, **fig_kw
    # fig, axes = plt.subplots(4, 1, num=1, figsize=(10, 8), dpi=300, constrained_layout=True,
    #                         gridspec_kw={'height_ratios': [1, 1, 1, 1]})  # , sharex=True)
    # fig, axes = plt.subplots(3, 1, num=1, figsize=(10, 8), dpi=300, constrained_layout=True,
    #                         gridspec_kw={'height_ratios': [1, 1, 1]})
    fig, axes = plt.subplots(3, 1, num=1, figsize=(10, 7), dpi=300, gridspec_kw={'height_ratios': [1, 1, 1]},
                             constrained_layout=True)
    ax0 = axes[0]
    ax1 = axes[1]
    ax2 = axes[2]
    # ax3 = axes[3]

    # set title of whole figure
    if w_param:
        fig.suptitle("%s, n=%d, w=%d" % (desc_str, n_bits, w_param))
    else:
        fig.suptitle("%s, n=%d" % (desc_str, n_bits))

    # same tick configuration for each axes
    tick_args = {'axis': 'both', 'which': 'both',
                 'labelsize': 'small',
                 'labelbottom': False, 'bottom': False,
                 'left': False, 'labelleft': False,
                 'right': True, 'labelright': True}

    # # Encoding Bins Subplot
    ax0.tick_params(**tick_args)

    # draw encoder bins
    draw_multi_encoder_bins(ax0, encoder, encoder_colors, fontsize=fontsize, xmin=xmin, xmax=xmax, draw_h_grid=True,
                            bin_linewidth=0.5,
                            clip_on=False, draw_regions=False, draw_region_by_encoder=False, draw_h_border=False,
                            draw_folded_bins=draw_folded_bins, label_bins=True)

    # # Similarity Subplot
    ax1.tick_params(**tick_args)

    # share ax0 and ax2 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw similarity plot
    draw_similarity(ax1, encoder, ref_points, feature_colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True)

    # Features Subplot (Boundaries, Weight, Crossings)
    ax2.tick_params(**tick_args)

    # share ax0 and ax1 x-axis
    ax2.get_shared_x_axes().join(ax2, ax0)

    # draw weight, crossings, and boundary features
    draw_features(ax2, encoder, similarity_colors, markersize, draw_regions=True)

    # draw_barcode(ax1, encoder.region_codes)

    # # Encoding Bits Subplot
    tick_args['labelbottom'] = True
    tick_args['bottom'] = True
    ax2.tick_params(**tick_args)
    ax2.set_xlim(xmin, xmax)

    ax2.axvline(x=encoder.lower_bound, ymax=3.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax2.axvline(x=encoder.upper_bound, ymax=3.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    ax2.set_xlabel("Value to Encode")
    ax2.set_ylabel("Binary Encoding")

    # ax3.tick_params(**tick_args)

    # share ax0 and ax3 x-axis
    # ax3.get_shared_x_axes().join(ax3, ax0)
    # ax3.set_xlim(xmin, xmax)

    # draw_similarity_heatmap(ax3, encoder, ref_points[0], colors, draw_regions=False, draw_v_values=False,
    #                         clip_on=False, xmin=xmin, xmax=xmax)

    # draw encoding bits along x-axis values
    # FIXME: still some encoding bin errors
    # draw_bits_by_data(ax3, encoder, x_pad=0.0, draw_region_bits=True,
    #                  draw_uniform_samples=False, permute_bits=False, clip_on=False, draw_boundaries=False)

    # draw input interval boundary lines across axes with vertical lines
    # ax3.axvline(x=encoder.lower_bound, ymax=4.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    # ax3.axvline(x=encoder.upper_bound, ymax=4.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    # ax3.set_xlabel("Value to Encode")
    # ax3.set_ylabel("Binary Encoding")


@profile
def plot_compact_multi_encoder(encoder, desc_str="Encoder", x_pad=0.1, draw_folded_bins=False, w_param=None):
    n_bits = encoder.n
    try:
        sub_encoders = encoder.encoders
        n_grids = len(sub_encoders)
    except:
        n_grids = 1

    markersize = 4
    fontsize = 8

    # TODO: plot distribution of periods, bin sizes, offsets, duty cycles, of a multi-encoder

    # print(encoder.xmin, encoder.xmax, encoder.lower_bound, encoder.upper_bound)
    # for enc in encoder.encoders:
    #     try:
    #         print(enc.xmin, enc.xmax, enc.lower_bound, enc.upper_bound)
    #     except:
    #         print(enc.lower_bound, enc.upper_bound)

    # plot range for this multi encoder
    try:
        # if xmin/xmax doesn't exist, use input bounds
        xmin = encoder.xmin - x_pad
        xmax = encoder.xmax + x_pad
    except AttributeError:
        xmin = encoder.lower_bound - x_pad
        xmax = encoder.upper_bound + x_pad

    # print(xmin, xmax)
    # reference points for comparison
    #ref_points = np.array([[0.21], [0.75]])
    ref_points = np.array([[2.1], [7.5]])

    n_points = len(ref_points)

    # color palette
    # colors = sns.color_palette("Set1", n_colors=len(ref_points))
    # colors = sns.color_palette("muted", n_colors=(n_grids+n_points))
    # colors = sns.color_palette("Set1", n_colors=(n_grids+n_points+2))
    # colors = sns.color_palette("cet_glasbey_hv", n_colors=(n_grids+n_points+2))
    # colors = sns.color_palette("cet_glasbey_hv", as_cmap=True).colors
    # colors = sns.color_palette("cet_glasbey_category10", as_cmap=True).colors
    colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors

    # grid_names = string.ascii_uppercase[:n_grids]
    # keys = list(range(n_grids))
    # keys.sort()
    # grid_colors = [colors[j] for j in range(n_grids)]

    encoder_colors = colors[0:n_grids]
    # similarity_colors = colors[n_grids:n_grids+n_points]
    # feature_colors = colors[n_grids+n_points:n_grids+n_points+2]

    similarity_colors = colors[-2 - n_points:-2]
    feature_colors = colors[-2:]

    # seaborn style
    sns.set_theme(style="white")

    # # Draw Plots in Each SubAxes

    # subplot_kw, gridspec_kw, **fig_kw
    # fig, axes = plt.subplots(4, 1, num=1, figsize=(10, 8), dpi=300, constrained_layout=True,
    #                         gridspec_kw={'height_ratios': [1, 1, 1, 1]})  # , sharex=True)
    # fig, axes = plt.subplots(3, 1, num=1, figsize=(10, 8), dpi=300, constrained_layout=True,
    #                         gridspec_kw={'height_ratios': [1, 1, 1]})
    fig, axes = plt.subplots(2, 1, num=1, figsize=(10, 7), dpi=300, gridspec_kw={'height_ratios': [1, 1]},
                             constrained_layout=True)
    ax0 = axes[0]
    ax1 = axes[1]
    # ax2 = axes[2]
    # ax3 = axes[3]

    # set title of whole figure
    if w_param:
        fig.suptitle("%s, n=%d, w=%d" % (desc_str, n_bits, w_param))
    else:
        fig.suptitle("%s, n=%d" % (desc_str, n_bits))

    # same tick configuration for each axes
    tick_args0 = {'axis': 'both', 'which': 'both',
                  'labelsize': 'small',
                  'labelbottom': False, 'bottom': False,
                  'left': False, 'labelleft': False,
                  'right': False, 'labelright': True}

    tick_args1 = {'axis': 'both', 'which': 'both',
                  'labelsize': 'small',
                  'labelbottom': True, 'bottom': True,
                  'left': False, 'labelleft': False,
                  'right': True, 'labelright': True}

    # # Encoding Bins Subplot
    ax0.tick_params(**tick_args0)

    # draw encoder bins
    draw_multi_encoder_bins(ax0, encoder, encoder_colors, fontsize=fontsize, xmin=xmin, xmax=xmax, draw_h_grid=True,
                            bin_linewidth=0.5, clip_on=False, draw_regions=False, draw_region_by_encoder=False,
                            draw_h_border=False, draw_folded_bins=draw_folded_bins, label_bins=False, label_grids=False)

    # # Similarity Subplot
    ax1.tick_params(**tick_args1)

    # share ax0 and ax2 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw weight, crossings, and boundary features
    # draw_features(ax1, encoder, similarity_colors, markersize, draw_regions=True, fill_weight=False, draw_legend=False)
    # draw_features(ax1, encoder, similarity_colors, markersize, draw_regions=False, fill_weight=False, draw_legend=False)

    #     ax.set_ylim(-0.1, max_bin_weight + 2)

    # draw similarity plot
    draw_similarity(ax1, encoder, ref_points, feature_colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True, draw_legend=False)

    # DRAW LEGEND WHILE REMOVING DUPLICATE LABELS

    handles2, labels2 = ax1.get_legend_handles_labels()

    # duplicate handle indices
    tally = defaultdict(list)
    for i, item in enumerate(labels2):
        tally[item].append(i)
    dup_items = ((key, locs) for key, locs in tally.items() if len(locs) > 1)

    indices_to_delete = []
    for dup in sorted(dup_items):
        # dup_value = dup[0]
        num_dups = len(dup[1]) - 1

        for i in range(num_dups):
            indices_to_delete.append(dup[1][i])

    for index in sorted(indices_to_delete, reverse=True):
        del handles2[index]
        del labels2[index]

    legend = ax1.legend(handles2, labels2, title=None, ncol=len(labels2), fontsize=8, title_fontsize=9)

    # draw_barcode(ax1, encoder.region_codes)

    # tick_args['labelbottom'] = True
    # tick_args['bottom'] = True
    # ax1.tick_params(**tick_args)
    ax1.set_xlim(xmin, xmax)

    ax0.axvline(x=encoder.lower_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax0.axvline(x=encoder.upper_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    ax1.axvline(x=encoder.lower_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax1.axvline(x=encoder.upper_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    # making the top and bottom spine invisible:
    ax0.spines['top'].set_color('none')
    ax0.spines['bottom'].set_color('none')
    ax0.spines['left'].set_color('none')
    ax0.spines['right'].set_color('none')

    # moving bottom spine up to y=0 position:
    # ax.xaxis.set_ticks_position('bottom')
    # ax.spines['bottom'].set_position(('data', 0))

    # moving left spine to the right to position x == 0:
    # ax.yaxis.set_ticks_position('left')
    # ax.spines['left'].set_position(('data', 0))

    # ax1.axvline(x=encoder.lower_bound, ymax=2.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    # ax1.axvline(x=encoder.upper_bound, ymax=2.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    # ax3.tick_params(**tick_args)

    # share ax0 and ax3 x-axis
    # ax3.get_shared_x_axes().join(ax3, ax0)
    # ax3.set_xlim(xmin, xmax)

    # draw_similarity_heatmap(ax3, encoder, ref_points[0], colors, draw_regions=False, draw_v_values=False,
    #                         clip_on=False, xmin=xmin, xmax=xmax)

    # draw encoding bits along x-axis values
    # FIXME: still some encoding bin errors
    # draw_bits_by_data(ax3, encoder, x_pad=0.0, draw_region_bits=True,
    #                  draw_uniform_samples=False, permute_bits=False, clip_on=False, draw_boundaries=False)

    # draw input interval boundary lines across axes with vertical lines
    # ax3.axvline(x=encoder.lower_bound, ymax=4.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    # ax3.axvline(x=encoder.upper_bound, ymax=4.1, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    # ax3.set_xlabel("Value to Encode")
    # ax3.set_ylabel("Binary Encoding")


@profile
def plot_periodic_cell_multi_encoder(encoder, desc_str="Encoder", x_pad=0.1, draw_folded_bins=False, w_param=None):
    n_bits = encoder.n
    try:
        sub_encoders = encoder.encoders
        n_grids = len(sub_encoders)
    except:
        n_grids = 1

    markersize = 4
    fontsize = 8

    # TODO: plot distribution of periods, bin sizes, offsets, duty cycles, of a multi-encoder

    # plot range for this multi encoder
    try:
        # if xmin/xmax doesn't exist, use input bounds
        xmin = encoder.xmin - x_pad
        xmax = encoder.xmax + x_pad
    except AttributeError:
        xmin = encoder.lower_bound - x_pad
        xmax = encoder.upper_bound + x_pad

    # reference points for comparison
    ref_points = np.array([[0.21], [0.75]])

    n_points = len(ref_points)

    # color palette
    colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors

    encoder_colors = colors[0:n_grids]

    similarity_colors = colors[-2 - n_points:-2]
    feature_colors = colors[-2:]

    # seaborn style
    sns.set_theme(style="white")

    # # Draw Plots in Each SubAxes

    fig, axes = plt.subplots(2, 1, num=1, figsize=(10, 7), dpi=300, gridspec_kw={'height_ratios': [1, 1]},
                             constrained_layout=True)
    ax0 = axes[0]
    ax1 = axes[1]

    # set title of whole figure
    if w_param:
        fig.suptitle("%s, n=%d, w=%d" % (desc_str, n_bits, w_param))
    else:
        fig.suptitle("%s, n=%d" % (desc_str, n_bits))

    # same tick configuration for each axes
    tick_args0 = {'axis': 'both', 'which': 'both',
                  'labelsize': 'small',
                  'labelbottom': False, 'bottom': False,
                  'left': False, 'labelleft': False,
                  'right': False, 'labelright': True}

    tick_args1 = {'axis': 'both', 'which': 'both',
                  'labelsize': 'small',
                  'labelbottom': True, 'bottom': True,
                  'left': False, 'labelleft': False,
                  'right': True, 'labelright': True}

    # # Encoding Bins Subplot
    ax0.tick_params(**tick_args0)

    # multiple single-cell periodic cell encoders
    # period, binsize, offset
    grid_labels = [
            textwrap.fill(
                    "period=%0.1f binsize=%0.2f offset=%0.2f" % (
                            encoder.encoders[j].periods[0], encoder.encoders[j].bin_sizes[0], encoder.encoders[j].origins[0]),
                    22)
            for j in range(n_grids)]

    # draw encoder bins
    draw_multi_encoder_bins(ax0, encoder, encoder_colors, fontsize=fontsize, xmin=xmin, xmax=xmax, draw_h_grid=False,
                            bin_linewidth=0.5, clip_on=False, draw_regions=False, draw_region_by_encoder=False,
                            draw_h_border=False, draw_folded_bins=draw_folded_bins, label_bins=True,
                            grid_labels=grid_labels, grid_label_size=6)

    # # Similarity Subplot
    ax1.tick_params(**tick_args1)

    # share ax0 and ax2 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw weight, crossings, and boundary features
    draw_features(ax1, encoder, similarity_colors, markersize, draw_regions=False, fill_weight=False, draw_legend=False)


    # draw similarity plot
    draw_similarity(ax1, encoder, ref_points, feature_colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True, draw_legend=False)

    # DRAW LEGEND WHILE REMOVING DUPLICATE LABELS

    handles2, labels2 = ax1.get_legend_handles_labels()

    # duplicate handle indices
    tally = defaultdict(list)
    for i, item in enumerate(labels2):
        tally[item].append(i)
    dup_items = ((key, locs) for key, locs in tally.items() if len(locs) > 1)

    indices_to_delete = []
    for dup in sorted(dup_items):
        # dup_value = dup[0]
        num_dups = len(dup[1]) - 1

        for i in range(num_dups):
            indices_to_delete.append(dup[1][i])

    for index in sorted(indices_to_delete, reverse=True):
        del handles2[index]
        del labels2[index]

    legend = ax1.legend(handles2, labels2, title=None, ncol=len(labels2), fontsize=8, title_fontsize=9)

    ax1.set_xlim(xmin, xmax)

    ax0.axvline(x=encoder.lower_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax0.axvline(x=encoder.upper_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    ax1.axvline(x=encoder.lower_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax1.axvline(x=encoder.upper_bound, ymax=1.0, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    # making the top and bottom spine invisible:
    ax0.spines['top'].set_color('none')
    ax0.spines['bottom'].set_color('none')
    ax0.spines['left'].set_color('none')
    ax0.spines['right'].set_color('none')

