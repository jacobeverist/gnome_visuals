# plotting
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

#sns.set_theme(style="white", color_codes=True)

try:
    from encoders.encoders import *
    from encoders.visuals import *
    from encoders.helpers import *
except:
    from encoder_analysis.encoders.encoders import *
    from encoder_analysis.encoders.visuals import *
    from encoder_analysis.encoders.helpers import *


def plot_heatmap(encoder, desc_str="Encoder", file_dir="./out", triangle=False, fontsize=8, annot=True):
    w = encoder.w
    n_bits = encoder.n

    file_name = file_dir + "%02u_" % (n_bits) + "heatmap_by_region" + ".png"

    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)
    X_gnomes1 = encoder.region_codes
    X_gnomes2 = encoder.encode(X_points)

    diagonal_scores = count_similarity(X_gnomes1, X_gnomes2)
    max_count = np.max(diagonal_scores)
    mean_count = np.mean(diagonal_scores)

    sns.set_style("white")
    sns.set_style("ticks")
    #sns.set_theme(style="white")

    # Generate a mask for the upper triangle
    if triangle:
        mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    else:
        mask = np.zeros_like(diagonal_scores, dtype=bool)

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    ax.set_title(desc_str)
    #ax.tick_params(axis='both', which='major', labelsize=10)
    ax.tick_params(axis='both', labelsize=fontsize)

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(diagonal_scores, mask=mask, cmap=cmap, vmax=max_count, center=mean_count,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=annot, annot_kws={"fontsize": fontsize})

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


def plot_pmesh_heatmap(encoder, desc_str="Encoder", file_dir="./out", triangle=False, fontsize=8, annot=True):
    w = encoder.w
    n_bits = encoder.n

    file_name = file_dir + "%02u_" % (n_bits) + "heatmap_by_value" + ".png"

    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)
    X_gnomes1 = encoder.region_codes
    X_gnomes2 = encoder.encode(X_points)

    x_vals = encoder.region_boundaries
    y_vals = encoder.region_boundaries

    x_centers = encoder.region_centers
    y_centers = encoder.region_centers

    diagonal_scores = count_similarity(X_gnomes1, X_gnomes2)
    max_count = np.max(diagonal_scores)
    mean_count = np.mean(diagonal_scores)

    sns.set_style("white")
    sns.set_style("ticks")
    #sns.set_theme(style="white")

    # Generate a mask for the upper triangle
    #mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    if triangle:
        mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    else:
        mask = np.zeros_like(diagonal_scores, dtype=bool)

    import numpy.ma as ma
    masked_scores = ma.array(diagonal_scores, mask=mask)

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    #ax.tick_params(axis='both', labelsize=fontsize)

    ax.set_title(desc_str)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Recenter a divergent colormap
    if True:
        vmax = max_count
        vmin = 0
        center = mean_count
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

    c = ax.pcolormesh(x_vals, y_vals, masked_scores, vmax=max_count, vmin=0, edgecolor='1.0', linewidth=0.3, cmap=cmap)
    cb = f.colorbar(c, ax=ax, shrink=0.5)  # , spacing="uniform", drawedges=True)
    cb.outline.set_linewidth(0)

    # add text box to center of each rectangle indicating count similarity
    if annot:

        # code to change the color of the text depending on cell color
        # lum = relative_luminance(color)
        # text_color = ".15" if lum > .408 else "w"

        for i in range(len(x_centers)):
            x = x_centers[i]

            for j in range(len(y_centers)):
                y = y_centers[j]
                score = masked_scores[j, i]
                if score is not np.ma.masked:
                    ax.text(x, y, str(score), horizontalalignment='center', verticalalignment='center',
                            fontsize=fontsize)

    """
    # code to change the color of the text depending on cell color
    
    def _annotate_heatmap(self, ax, mesh):
        "Add textual labels with the value in each cell."
        mesh.update_scalarmappable()
        height, width = self.annot_data.shape
        xpos, ypos = np.meshgrid(np.arange(width) + .5, np.arange(height) + .5)
        for x, y, m, color, val in zip(xpos.flat, ypos.flat,
                                       mesh.get_array(), mesh.get_facecolors(),
                                       self.annot_data.flat):
            if m is not np.ma.masked:
                lum = relative_luminance(color)
                text_color = ".15" if lum > .408 else "w"
                annotation = ("{:" + self.fmt + "}").format(val)
                text_kwargs = dict(color=text_color, ha="center", va="center")
                text_kwargs.update(self.annot_kws)
                ax.text(x, y, annotation, **text_kwargs)
    """

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


def plot_interval_multi_encoder(encoder, desc_str="Encoder", file_dir="./out", x_pad=0.1):
    n_bits = encoder.n
    markersize = 4
    fontsize = 6

    # plot range for this multi encoder
    xmin = encoder.lower_bound - x_pad
    xmax = encoder.upper_bound + x_pad

    # filename
    file_name = file_dir + "%02u_" % (n_bits) + desc_str + ".png"

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

    ## Encoding Bins Subplot
    ax0.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        bottom=False,
        left=False,
        right=True,
        labelleft=False,
        labelright=True, labelsize='small')

    # draw encoder bins
    draw_multi_encoder_bins(ax0, encoder, fontsize=fontsize, xmin=xmin, xmax=xmax,
                            clip_on=False, draw_regions=False, draw_region_by_encoder=False)

    # Features Subplot (Boundaries, Weight, Crossings)
    ax1.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        bottom=False,
        left=False,
        right=True,
        labelleft=False,
        labelright=True)

    # share ax0 and ax1 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw weight, crossings, and boundary features
    draw_features(ax1, encoder, colors, markersize)

    ## Similarity Subplot
    ax2.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        bottom=False,
        left=False,
        right=True,
        labelleft=False,
        labelright=True)

    # share ax0 and ax2 x-axis
    ax2.get_shared_x_axes().join(ax2, ax0)

    # draw similarity plot
    draw_similarity(ax2, encoder, X_gnomes, ref_points, colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True)

    ## Encoding Bits Subplot
    ax3.tick_params(
        axis='both',
        which='both',
        labelbottom=True,
        bottom=True,
        left=False,
        right=True,
        labelleft=False,
        labelright=True, labelsize='small')

    # share ax0 and ax3 x-axis
    ax3.get_shared_x_axes().join(ax3, ax0)

    # draw encoding bits along x-axis values
    #draw_bits_by_data(ax3, encoder, xmin=xmin, xmax=xmax, x_pad=0.0, draw_region_bits=False,
    #                 draw_uniform_samples=True, permute_bits=False, clip_on=False, draw_boundaries=False)
    draw_bits_by_data(ax3, encoder, xmin=xmin, xmax=xmax, x_pad=0.0, draw_region_bits=True,
                      draw_uniform_samples=False, permute_bits=False, clip_on=False, draw_boundaries=False)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


if __name__ == "__main__":
    file_dir = "out/"

    # multi_encoder.add_encoder(FixedWeightEncoder(n=5, w=1))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=7, w=1))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=11, w=1))

    # multi_encoder.add_encoder(FixedWeightEncoder(n=4, w=1))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=16, w=1))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=7, w=3, lower_bound=0.5, L=0.5))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=9, w=3, lower_bound=0.3, L=0.7))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=11, w=3))

    # multi_encoder.add_encoder(FixedWeightEncoder(n=7, w=3, L=0.5, clamped_input=True))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=7, w=3, L=0.5, clamped_input=True))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=7, w=3, L=0.5, clamped_input=True))
    # multi_encoder.add_encoder(FixedWeightEncoder(n=9, w=3, L=0.7, clamped_input=True))

    # test scalar and clamped input encoding
    # result = multi_encoder.encode(-1)
    # print(-1, result)

    # X = np.array([[0.21], [0.69], [0.91]])
    # composite_codes = multi_encoder.encode(X)
    # print(composite_codes)
    # print(composite_codes.shape)

    """
    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(FixedWeightEncoder(n=20, w=3))
    plot_interval_multi_encoder(multi_encoder, desc_str="FixedWeightEncoder", file_dir=file_dir)
    plt.clf()

    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(TaperingWeightEncoder(n=20, w=3))
    plot_interval_multi_encoder(multi_encoder, desc_str="TaperingWeightEncoder", file_dir=file_dir)
    plt.clf()
    """

    #foo = PeriodicCellEncoder(n=1)

    multi_encoder = MultiEncoder()
    #multi_encoder.add_encoder(PlaceCellEncoder(n=10))
    #multi_encoder.add_encoder(PlaceCellEncoder(n=10))
    #multi_encoder.add_encoder(FixedWeightEncoder(n=15, w=3))
    #multi_encoder.add_encoder(FixedWeightEncoder(n=10, w=3))
    #multi_encoder.add_encoder(RandomizedPlaceCellEncoder(n=10))

    multi_encoder.add_encoder(PeriodicCellEncoder(n=10, oob_method="modulo"))
    multi_encoder.add_encoder(PeriodicCellEncoder(n=10, oob_method="modulo"))

    plot_interval_multi_encoder(multi_encoder, desc_str="PeriodicCellEncoder", file_dir=file_dir)
    plt.clf()

    #place_encoder = RandomizedPlaceCellEncoder(n=10)
    #plot_interval_multi_encoder(place_encoder, desc_str="RandomizedPlaceCellEncoder", file_dir=file_dir)
    #plt.clf()

    # TODO:
    # 1) + add base class boundary-handling options (exception, clamp, modulo, silent)
    # 2) + able to plot fundamental regions of periodic cells
    # 3) + plot fundamental bin and congruent bins (with lower alpha)
    # 4) create better grid distribution options, multi-scale, etc



    #plot_heatmap(multi_encoder, desc_str="Similarity_by_Region", file_dir=file_dir, fontsize=6)
    #plt.clf()

    #plot_pmesh_heatmap(multi_encoder, desc_str="Similarity_by_Value", file_dir=file_dir, annot=False)
    #plt.clf()

    #taper_encoder = TaperingWeightEncoder(n=10, w=3)
    #plot_interval_multi_encoder(taper_encoder, "Tapering Weight Encoder", file_dir=file_dir)
    #plt.clf()
    # plot_interval_encoder(fixed_encoder, "Fixed Weight Encoder", file_dir=file_dir)
    # plt.clf()
