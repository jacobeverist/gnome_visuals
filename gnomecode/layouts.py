# plotting

from line_profiler_pycharm import profile
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import ticker, axis

from .axesplots import *

__all__ = ['plot_diff_heatmap', 'plot_code_heatmap', 'plot_realspace_heatmap', 'plot_interval_multi_encoder', 'save_fig']


@profile
def save_fig(path, encoder, plot_name, experiment_name, do_close=True):
    file_path = path + "%03u_%04u_" % (
            encoder.n, len(encoder.region_centers)) + plot_name + "_" + experiment_name + ".png"

    plt.savefig(file_path, bbox_inches='tight')

    if do_close:
        plt.close()
        sns.reset_defaults()


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

    print("X_gnomes:", encoder.region_codes.shape)

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
                           draw_minor_tick_grid=False):
    y_spacing = 0.05
    inset_fraction = 0.25

    # plot range for this multi encoder
    xmin = encoder.lower_bound
    xmax = encoder.upper_bound

    ax_colorbar = None

    do_sns_jointgrid = False
    do_inset_axes = True
    do_gridspec_axes = False
    do_subgridspec_axes = False
    do_gridspec_inset_axes = False

    if do_sns_jointgrid:
        ratio = 4

        # setup Seaborn JointGrid
        g = sns.JointGrid(ratio=ratio, xlim=(0, 1), ylim=(0, 1))

        fig = g.fig
        ax_heatmap = g.ax_joint
        ax_features = g.ax_marg_x
        ax_colorbar = g.ax_marg_y

        # Unshare y-axis of colorbar

        # Now remove axes from the grouper for xaxis
        ax_colorbar.get_shared_y_axes().remove(ax_colorbar)

        # Create and assign new ticker
        yticker = mpl.axis.Ticker()
        ax_colorbar.yaxis.major = yticker

        # The new ticker needs new locator and formatters
        yloc = mpl.ticker.AutoLocator()
        yfmt = mpl.ticker.ScalarFormatter()
        ax_colorbar.yaxis.set_major_locator(yloc)
        ax_colorbar.yaxis.set_major_formatter(yfmt)

        fig.set_tight_layout(True)

    elif do_inset_axes:

        # Start with a square Figure and add a couple extra inches to top
        fig = plt.figure(figsize=(9, 12), constrained_layout=True)

        ax_heatmap = fig.add_gridspec(top=0.75, right=0.75).subplots()
        ax_heatmap.set(aspect=1)

        plot_up = True
        if plot_up:
            ax_features = ax_heatmap.inset_axes([0, 1.0 + y_spacing, 1, inset_fraction],
                                                sharex=ax_heatmap)  # plot on top
        else:
            ax_features = ax_heatmap.inset_axes([0, -inset_fraction - y_spacing, 1, inset_fraction],
                                                sharex=ax_heatmap)  # plot on bottom

        # ax_colorbar = ax_heatmap.inset_axes([1.05, 0.25, 0.05, 0.5])
        ax_colorbar = ax_heatmap.inset_axes([1.03, 0.23, 0.023, 0.54])

    elif do_gridspec_axes:

        # Start with a square Figure.
        fig = plt.figure(figsize=(9, 9))

        # Add a gridspec with two rows and two columns and a ratio of 1 to 4 between
        # the size of the marginal axes and the main axes in both directions.
        # Also adjust the subplot parameters for a square plot.
        # gs = fig.add_gridspec(2, 2, width_ratios=(8, 1), height_ratios=(4, 1))
        # , left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.05)

        gs = fig.add_gridspec(6, 6)

        ax_heatmap = fig.add_subplot(gs[1:, :-1])
        ax_features = fig.add_subplot(gs[0, :-1], sharex=ax_heatmap)
        ax_colorbar = fig.add_subplot(gs[1:, -1])

    elif do_subgridspec_axes:

        fig = plt.figure(figsize=(9, 11))  # , constrained_layout=True) #, tight_layout=True)

        gs0 = fig.add_gridspec(1, 2, width_ratios=(4, 1), hspace=0, wspace=0)
        gs00 = gs0[0].subgridspec(2, 1, height_ratios=(4, 1), hspace=0, wspace=0)  # , wspace=0.05, hspace=0.05)
        gs01 = gs0[1].subgridspec(2, 3, height_ratios=(4, 1), width_ratios=(1, 1, 1), hspace=0.03, wspace=0.03)

        ax_heatmap = fig.add_subplot(gs00[0, 0])
        ax_features = fig.add_subplot(gs00[1, 0], sharex=ax_heatmap)
        ax_colorbar = fig.add_subplot(gs01[0, 1])

        ax_heatmap.set(aspect=1)

        for a in range(2):
            for b in range(3):
                if not (a == 0 and b == 1):
                    ax_temp = fig.add_subplot(gs01[a, b])

                    ax_temp.spines['top'].set_visible(False)
                    ax_temp.spines['right'].set_visible(False)
                    ax_temp.spines['bottom'].set_visible(False)
                    ax_temp.spines['left'].set_visible(False)

                    # same tick configuration for each axes
                    tick_args = {'axis': 'both', 'which': 'both',
                                 'labelsize': 'small',
                                 'labelbottom': False, 'bottom': False,
                                 'left': False, 'labelleft': False,
                                 'right': False, 'labelright': False}

                    # # Encoding Bins Subplot
                    ax_temp.tick_params(**tick_args)

                    ax_temp.set(visible=False)

    elif do_gridspec_inset_axes:

        fig = plt.figure(figsize=(9, 11), constrained_layout=True)  # , tight_layout=True)

        gs0 = fig.add_gridspec(2, 1, height_ratios=(4, 1))

        ax_heatmap = fig.add_subplot(gs0[0, 0])
        ax_features = fig.add_subplot(gs0[1, 0], sharex=ax_heatmap)
        ax_colorbar = ax_heatmap.inset_axes([1.05, 0.25, 0.05, 0.5])

        ax_heatmap.set(aspect=1)

    # do_subplots_axes
    else:
        fig, axes = plt.subplots(2, 1, figsize=(9, 11), gridspec_kw={'height_ratios': [4, 1], 'width_ratios': [1, ]})
        ax_heatmap = axes[0]
        ax_features = axes[1]

    ax_heatmap.invert_yaxis()
    fig.suptitle(desc_str)

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
    ax_features.set_xlim(xmin, xmax)

    # draw weight, crossings, and boundary features
    # markersize = 4
    # colors = sns.color_palette("Set1")  # , n_colors=oints))

    # draw_features(ax_features, encoder, colors, markersize, draw_regions=True, draw_legend=False)
    draw_bits_by_data(ax_features, encoder, draw_boundaries=False, draw_region_bits=True, draw_bit_grid=True, x_pad=0,
                      y_margin=0, y_pad=0)

    # draw minor tick locations for the region boundaries
    boundaries = encoder.region_boundaries
    ax_features.xaxis.set_minor_locator(ticker.FixedLocator(boundaries))
    ax_heatmap.yaxis.set_minor_locator(ticker.FixedLocator(boundaries))

    # ax_features.set_ylabel("Bit Encoding vs.\nReal Value")

    grid_linewidth = 0.3
    grid_alpha = 0.2

    if draw_manual_grid:
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
        ax_features.grid(visible=True, which='minor', axis='x', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                         zorder=1)
        ax_heatmap.grid(visible=True, which='minor', axis='both', alpha=grid_alpha, linewidth=grid_linewidth, color='k',
                        zorder=1)


@profile
def plot_interval_multi_encoder(encoder, desc_str="Encoder", x_pad=0.1):
    n_bits = encoder.n
    markersize = 4
    fontsize = 6

    # TODO: plot distribution of periods, bin sizes, offsets, duty cycles, of a multi-encoder

    # plot range for this multi encoder
    xmin = encoder.lower_bound - x_pad
    xmax = encoder.upper_bound + x_pad

    # reference points for comparison
    ref_points = np.array([[0.21], [0.69]])

    # color palette
    colors = sns.color_palette("Set1", n_colors=len(ref_points))

    # seaborn style
    sns.set_theme(style="white")

    # # Draw Plots in Each SubAxes

    # subplot_kw, gridspec_kw, **fig_kw
    fig, axes = plt.subplots(4, 1, num=1, figsize=(10, 8), dpi=300, constrained_layout=True,
                             gridspec_kw={'height_ratios': [1, 1, 1, 1]})  # , sharex=True)
    ax0 = axes[0]
    ax1 = axes[1]
    ax2 = axes[2]
    ax3 = axes[3]

    # set title of whole figure
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
    draw_multi_encoder_bins(ax0, encoder, fontsize=fontsize, xmin=xmin, xmax=xmax, draw_h_grid=True, bin_linewidth=0.5,
                            clip_on=False, draw_regions=False, draw_region_by_encoder=False, draw_h_border=False,
                            draw_folded_bins=True, label_bins=True)

    # Features Subplot (Boundaries, Weight, Crossings)
    # ax1.tick_params(**tick_args)

    # share ax0 and ax1 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw weight, crossings, and boundary features
    draw_features(ax1, encoder, colors, markersize, draw_regions=True)

    # draw_barcode(ax1, encoder.region_codes)

    # # Similarity Subplot
    ax2.tick_params(**tick_args)

    # share ax0 and ax2 x-axis
    ax2.get_shared_x_axes().join(ax2, ax0)

    # draw similarity plot
    draw_similarity(ax2, encoder, ref_points, colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True)

    # # Encoding Bits Subplot
    tick_args['labelbottom'] = True
    tick_args['bottom'] = True
    ax3.tick_params(**tick_args)

    # share ax0 and ax3 x-axis
    ax3.get_shared_x_axes().join(ax3, ax0)

    ax3.set_xlim(xmin, xmax)

    # draw_similarity_heatmap(ax3, encoder, ref_points[0], colors, draw_regions=False, draw_v_values=False,
    #                         clip_on=False, xmin=xmin, xmax=xmax)

    # draw encoding bits along x-axis values
    # FIXME: still some encoding bin errors
    draw_bits_by_data(ax3, encoder, xmin=xmin, xmax=xmax, x_pad=0.0, draw_region_bits=True,
                      draw_uniform_samples=False, permute_bits=False, clip_on=False, draw_boundaries=False)

    # draw input interval boundary lines across axes with vertical lines
    ax3.axvline(x=encoder.lower_bound, ymax=4.3, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax3.axvline(x=encoder.upper_bound, ymax=4.3, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
