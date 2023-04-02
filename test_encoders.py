# plotting

from matplotlib import ticker
from matplotlib import axis


import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import numpy.ma as ma

from gnomecodes import *


# sns.set_theme(style="white", color_codes=True)

# TODO:
# 1) + add base class boundary-handling options (exception, clamp, modulo, silent)
# 2) + able to plot fundamental regions of periodic cells
# 3) + plot fundamental bin and congruent bins (with lower alpha)
# 4) + create better grid distribution options, multi-scale, etc
# 5) center fund. region for each bin
# 6) illustrative plots for each step of discussion (Properties of Discrete Encodings of Binary Population)
# 7) + try to use the seaborn facet features to align heatmap x-axis with a graph plot x-axis
# 8) + replace original self-similarity plots with plot_heatmap2 and plot_pmesh_heatmap2, figure out style issues (add seaborn layout)
# 9) + remove plot_heatmap and plot_pmesh_heatmap code
# 10)+ test_encoders.py should be figure-level and axes-level styling code, and visuals.py should be axes-level plotting

def plot_heatmap(encoder, desc_str="Encoder", file_dir="./out", triangle=False, fontsize=8, annot=True):
    n_bits = encoder.n
    n_regions = len(encoder.region_centers)

    file_name = file_dir + "%03u_%04u_" % (n_bits, n_regions) + desc_str + ".png"

    sns.set_style("white")
    sns.set_style("ticks")

    # Set up the matplotlib figure
    # fig, ax = plt.subplots(1, 1, figsize=(10, 8), dpi=300, constrained_layout=True)
    # f, ax = plt.subplots(figsize=(11, 9))

    f, ax = plt.subplots(figsize=(11, 9))

    # same tick configuration for each axes
    # ax.tick_params({'axis': 'both', 'which': 'both', 'labelsize': fontsize})
    # ax.tick_params({'axis': 'both', 'labelsize': fontsize})
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.set_title(desc_str)

    draw_code_self_similarity(ax, encoder, triangle=triangle, annot=annot)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')

    sns.reset_defaults()


def plot_pmesh_heatmap(encoder, desc_str="Encoder", file_dir="./out", triangle=False, annot=True):
    n_bits = encoder.n
    n_regions = len(encoder.region_centers)

    # plot range for this multi encoder
    xmin = encoder.lower_bound
    xmax = encoder.upper_bound

    # file_name = file_dir + "%02u_" % (n_bits) + "heatmap_by_value" + ".png"
    file_name = file_dir + "%03u_%04u_" % (n_bits, n_regions) + desc_str + ".png"

    # sns.set_style("white")
    # sns.set_style("ticks")

    ax_heatmap = None
    ax_features = None
    ax_colorbar = None

    do_sns_jointgrid = False
    do_inset_axes = True
    do_gridspec_axes = False
    do_subgridspec_axes = False
    do_gridspec_inset_axes = False


    if do_sns_jointgrid:
        ratio = 5

        # Set up the subplot grid
        #f = plt.figure(figsize=(9, 9))
        #gs = plt.GridSpec(ratio + 1, ratio + 1)

        #ax_joint = f.add_subplot(gs[1:, :-1])
        #ax_marg_x = f.add_subplot(gs[0, :-1], sharex=ax_joint)
        #ax_marg_y = f.add_subplot(gs[1:, -1], sharey=ax_joint)

        g = sns.JointGrid(ratio=4, xlim=(0, 1), ylim=(0, 1))

        fig = g._figure
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
        fig = plt.figure(figsize=(9,11), constrained_layout=True)

        ax_heatmap = fig.add_gridspec(top=0.75, right=0.75).subplots()
        ax_heatmap.set(aspect=1)

        plot_up = True
        if plot_up:
            ax_features = ax_heatmap.inset_axes([0, 1.05, 1, 0.25], sharex=ax_heatmap)  # plot on top
        else:
            ax_features = ax_heatmap.inset_axes([0, -0.30, 1, 0.25], sharex=ax_heatmap)  # plot on bottom

        ax_colorbar = ax_heatmap.inset_axes([1.05, 0.25, 0.05, 0.5])

    elif do_gridspec_axes:

        # Start with a square Figure.
        fig = plt.figure(figsize=(9, 9))

        # Add a gridspec with two rows and two columns and a ratio of 1 to 4 between
        # the size of the marginal axes and the main axes in both directions.
        # Also adjust the subplot parameters for a square plot.
        gs = fig.add_gridspec(2, 2, width_ratios=(8, 1), height_ratios=(4, 1))
        # , left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.05)

        gs = fig.add_gridspec(6, 6)

        ax_heatmap = fig.add_subplot(gs[1:, :-1])
        ax_features = fig.add_subplot(gs[0, :-1], sharex=ax_heatmap)
        ax_colorbar = fig.add_subplot(gs[1:, -1])


        # Create the Axes.
        #ax_heatmap = fig.add_subplot(gs[0, 0])
        #ax_features = fig.add_subplot(gs[1, 0], sharex=ax_heatmap)
        #ax_colorbar = fig.add_subplot(gs[:, 1])
        #ax_heatmap.set(aspect=1)

        # def make_axes_gridspec(parent, *, fraction=0.15, shrink=1.0, aspect=20, **kw):

    elif do_subgridspec_axes:

        fig = plt.figure(figsize=(9,11)) #, constrained_layout=True) #, tight_layout=True)

        # 2, 2,  width_ratios=(4, 1), height_ratios=(1, 4),
        #gs0 = fig.add_gridspec(2, 2, width_ratios=(4, 1), height_ratios=(4, 1))
        # left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.05)

        #gs0 = fig.add_gridspec(1, 2, width_ratios=(4, 1), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.01)
        gs0 = fig.add_gridspec(1, 2, width_ratios=(4, 1), hspace=0, wspace=0)
        gs00 = gs0[0].subgridspec(2, 1, height_ratios=(4, 1), hspace=0, wspace=0 ) #, wspace=0.05, hspace=0.05)
        gs01 = gs0[1].subgridspec(2, 3, height_ratios=(4, 1), width_ratios=(1, 1, 1), hspace=0.03, wspace=0.03)

        # gs01 = gs0[1].subgridspec(1, 1)

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

                    ## Encoding Bins Subplot
                    ax_temp.tick_params(**tick_args)

                    ax_temp.set(visible=False)


    elif do_gridspec_inset_axes:

        fig = plt.figure(figsize=(9,11), constrained_layout=True) #, tight_layout=True)

        # 2, 2,  width_ratios=(4, 1), height_ratios=(1, 4),
        #gs0 = fig.add_gridspec(2, 2, width_ratios=(4, 1), height_ratios=(4, 1))
        # left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.05)

        #gs0 = fig.add_gridspec(1, 2, width_ratios=(4, 1), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05, hspace=0.01)
        #gs0 = fig.add_gridspec(2, 1, height_ratios=(4, 1), top=0.75, right=0.75) #, hspace=0, wspace=0)
        gs0 = fig.add_gridspec(2, 1, height_ratios=(4, 1)) #, top=0.75, right=0.75) #, hspace=0, wspace=0)

        ax_heatmap = fig.add_subplot(gs0[0, 0])
        ax_features = fig.add_subplot(gs0[1, 0], sharex=ax_heatmap)

        #ax_heatmap = fig.add_gridspec(top=0.75, right=0.75).subplots()
        #ax_heatmap.set(aspect=1)

        #plot_top = False
        #if plot_top:
        #    ax_features = ax_heatmap.inset_axes([0, 1.05, 1, 0.25], sharex=ax_heatmap)  # plot on top
        #else:
        #    ax_features = ax_heatmap.inset_axes([0, -0.30, 1, 0.25], sharex=ax_heatmap)  # plot on bottom

        ax_colorbar = ax_heatmap.inset_axes([1.05, 0.25, 0.05, 0.5])

        ax_heatmap.set(aspect=1)




    # do_subplots_axes
    else:
        fig, axes = plt.subplots(2, 1, figsize=(9, 11), gridspec_kw={'height_ratios': [4, 1], 'width_ratios': [1, ]})
        ax_heatmap = axes[0]
        ax_features = axes[1]

    ax0 = ax_heatmap
    ax1 = ax_features


    fig.suptitle(desc_str)
    #ax0.set_title(desc_str)
    ax0.invert_yaxis()
    ax0.spines['top'].set_visible(False)
    ax0.spines['right'].set_visible(False)
    ax0.spines['bottom'].set_visible(False)
    ax0.spines['left'].set_visible(False)
    #ax0.set_aspect("equal")

    draw_projected_self_similarity(ax0, encoder, triangle=triangle, annot=annot, cbar=True, cbar_ax=ax_colorbar)

    # same tick configuration for each axes
    tick_args = {'axis': 'both', 'which': 'both', 'labelsize': 'small', 'labelbottom': True, 'bottom': True,
                 'left': False, 'labelleft': False, 'right': True, 'labelright': True}

    # Features Subplot (Boundaries, Weight, Crossings)
    ax1.tick_params(**tick_args)

    # share ax0 and ax1 x-axis
    # ax1.get_shared_x_axes().join(ax1, ax0)
    ax1.set_xlim(xmin, xmax)

    # draw weight, crossings, and boundary features
    markersize = 4
    colors = sns.color_palette("Set1")  # , n_colors=oints))
    draw_features(ax1, encoder, colors, markersize, draw_regions=True, draw_legend=False)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')

    sns.reset_defaults()


def plot_interval_multi_encoder(encoder, desc_str="Encoder", file_dir="./out", x_pad=0.1):
    n_bits = encoder.n
    markersize = 4
    fontsize = 6

    # TODO: plot distribution of periods, bin sizes, offsets, duty cycles, of a multi-encoder

    # plot range for this multi encoder
    xmin = encoder.lower_bound - x_pad
    xmax = encoder.upper_bound + x_pad

    # filename
    file_name = file_dir + "%03u_samples_" % (n_bits) + desc_str + ".png"

    # reference points for comparison
    ref_points = np.array([[0.21], [0.69]])

    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)

    # encodings
    X_gnomes = encoder.encode(X_points)

    # color palette
    colors = sns.color_palette("Set1", n_colors=len(ref_points))

    # seaborn style
    sns.set_theme(style="white")

    ## Draw Plots in Each SubAxes

    # subplot_kw, gridspec_kw, **fig_kw
    fig, axes = plt.subplots(4, 1, num=1, figsize=(10, 8), dpi=300, constrained_layout=True,
                             gridspec_kw={'height_ratios': [1, 1, 1, 1]})  # , sharex=True)
    ax0 = axes[0]
    ax1 = axes[1]
    ax2 = axes[2]
    ax3 = axes[3]

    # set title of whole figure
    ax0.set_title("%s, n=%d" % (desc_str, n_bits))

    # same tick configuration for each axes
    tick_args = {'axis': 'both', 'which': 'both',
                 'labelsize': 'small',
                 'labelbottom': False, 'bottom': False,
                 'left': False, 'labelleft': False,
                 'right': True, 'labelright': True}

    ## Encoding Bins Subplot
    ax0.tick_params(**tick_args)

    # draw encoder bins
    draw_multi_encoder_bins(ax0, encoder, fontsize=fontsize, xmin=xmin, xmax=xmax, draw_h_grid=False, bin_linewidth=0,
                            clip_on=True, draw_regions=False, draw_region_by_encoder=False, draw_h_border=False)

    # Features Subplot (Boundaries, Weight, Crossings)
    ax1.tick_params(**tick_args)

    # share ax0 and ax1 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw weight, crossings, and boundary features
    draw_features(ax1, encoder, colors, markersize, draw_regions=True)

    ## Similarity Subplot
    ax2.tick_params(**tick_args)

    # share ax0 and ax2 x-axis
    ax2.get_shared_x_axes().join(ax2, ax0)

    # draw similarity plot
    draw_similarity(ax2, encoder, X_gnomes, ref_points, colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True)

    # draw_similarity_heatmap(ax2, encoder, X_gnomes, ref_points[0], colors, draw_regions=True, draw_v_values=True,
    #                        clip_on=False, xmin=xmin, xmax=xmax)

    ## Encoding Bits Subplot
    tick_args['labelbottom'] = True
    tick_args['bottom'] = True
    ax3.tick_params(**tick_args)

    # share ax0 and ax3 x-axis
    ax3.get_shared_x_axes().join(ax3, ax0)

    ax3.set_xlim(xmin, xmax)

    draw_similarity_heatmap(ax3, encoder, X_gnomes, ref_points[0], colors, draw_regions=False, draw_v_values=False,
                            clip_on=False, xmin=xmin, xmax=xmax)

    # draw encoding bits along x-axis values
    # FIXME: still some encoding bin errors
    # draw_bits_by_data(ax3, encoder, xmin=xmin, xmax=xmax, x_pad=0.0, draw_region_bits=False,
    #                  draw_uniform_samples=True, permute_bits=False, clip_on=True, draw_boundaries=False)

    # draw input interval boundary lines across axes with vertical lines
    ax3.axvline(x=encoder.lower_bound, ymax=4.3, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)
    ax3.axvline(x=encoder.upper_bound, ymax=4.3, alpha=0.3, linewidth=1.5, color='k', linestyle='--', clip_on=False)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


if __name__ == "__main__":
    file_dir = "out/"

    # test numpy array input (n,1)
    # X = np.array([[0.21], [0.69], [0.91]])
    # result = multi_encoder.encode(X)
    # print(X, result)

    # test scalar input
    # result = multi_encoder.encode(-1)
    # print(-1, result)

    # FOREACH encoder type and config
    # test numpy array input (n,)
    # test list of floats input
    # test different interval upper and lower bounds
    # test different weight 'w'
    # test different interval length 'L'
    # test oob_method 'silent'
    # test oob_method 'modulo'
    # test oob_method 'clamp'
    # test oob_method 'exception'

    multi_encoder = MultiEncoder()
    for i in range(10, 11):
        #for i in range(40, 41):
        # for i in range(200, 201):
        # desc_str = "RandomizedPlaceCellEncoder"
        # multi_encoder.add_encoder(RandomizedPlaceCellEncoder(n=1, seed=i))

        desc_str = "Fixed_Weight_MultiEncoder"
        multi_encoder.add_encoder(FixedWeightEncoder(n=3, w=1))
        multi_encoder.add_encoder(FixedWeightEncoder(n=5, w=1))
        multi_encoder.add_encoder(FixedWeightEncoder(n=7, w=1))

        # desc_str = "Tapering_Weight_MultiEncoder"
        # multi_encoder.add_encoder(TaperingWeightEncoder(n=6+i, w=3))

        #desc_str = "PeriodicCellEncoder"
        #multi_encoder.add_encoder(PeriodicCellEncoder(n=i, oob_method="modulo", seed=i))

        # plot_interval_multi_encoder(multi_encoder, desc_str=desc_str, file_dir=file_dir)
        # plt.close()

        # self-similarity matrix by region code
        # plot_heatmap(multi_encoder, desc_str=desc_str + "_Similarity_Matrix_by_Region_Code", file_dir=file_dir,
        #             fontsize=6)
        # plt.close()

        # self-similarity matrix projected to real space
        plot_pmesh_heatmap(multi_encoder, desc_str=desc_str + "_Similarity_Matrix_Projected_to_Real_Space",
                           file_dir=file_dir)
        plt.close()
