# plotting
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy.ma as ma

# sns.set_theme(style="white", color_codes=True)

try:
    from encoders.encoders import *
    from encoders.visuals import *
    from encoders.helpers import *
except:
    from encoder_analysis.encoders.encoders import *
    from encoder_analysis.encoders.visuals import *
    from encoder_analysis.encoders.helpers import *


def plot_heatmap(encoder, desc_str="Encoder", file_dir="./out", triangle=False, fontsize=8, annot=True):
    n_bits = encoder.n
    n_regions = len(encoder.region_centers)

    file_name = file_dir + "%03u_%04u_" % (n_bits, n_regions) + desc_str + ".png"


    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)
    X_gnomes1 = encoder.region_codes
    X_gnomes2 = encoder.encode(X_points)

    diagonal_scores = count_similarity(X_gnomes1, X_gnomes2)
    max_count = np.max(diagonal_scores)
    mean_count = np.mean(diagonal_scores)

    sns.set_style("white")
    sns.set_style("ticks")
    # sns.set_theme(style="white")

    # Generate a mask for the upper triangle
    if triangle:
        shape_mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    else:
        shape_mask = np.zeros_like(diagonal_scores, dtype=bool)
    mask = shape_mask

    # omit zero text data
    scores_text = diagonal_scores.astype('|S10')
    annot_data = np.where(diagonal_scores > 0, scores_text, '')

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    ax.set_title(desc_str)
    # ax.tick_params(axis='both', which='major', labelsize=10)
    ax.tick_params(axis='both', labelsize=fontsize)

    # Generate a custom diverging colormap
    #cmap = sns.diverging_palette(230, 20, as_cmap=True)
    #cmap = sns.color_palette("rocket_r", as_cmap=True)
    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)

    #print(f"{np.array2string(means, formatter={'float': lambda x: f'{x:.2f}'})}")

    num_points = X_points.shape[0]
    #print("num_points:", num_points)

    if num_points < 80:
        linewidths = 2. / num_points
        fontsize = 32. * 8. / num_points

    else:
        linewidths = 0
        fontsize = 0
        annot_data = False

    #print("line_widths:", linewidths)
    #print("fontsize:", fontsize)

    # Draw the heatmap with the mask and correct aspect ratio
    #sns.heatmap(diagonal_scores, mask=mask, cmap=cmap, vmax=max_count, center=mean_count,
    #            square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=annot, annot_kws={"fontsize": fontsize})
    #sns.heatmap(diagonal_scores, mask=mask, cmap=cmap, vmax=max_count, center=mean_count,
    sns.heatmap(diagonal_scores, mask=mask, cmap=cmap, vmax=max_count, fmt="s",
                square=True, linewidths=linewidths, cbar_kws={"shrink": .5}, annot=annot_data, annot_kws={"fontsize": fontsize})
                #square=True, cbar_kws={"shrink": .5}, annot=annot)
                #square = True, linewidths = .5, cbar_kws = {"shrink": .5}, annot = annot)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


def plot_pmesh_heatmap(encoder, desc_str="Encoder", file_dir="./out", triangle=False, fontsize=8, annot=True):
    n_bits = encoder.n

    n_regions = len(encoder.region_centers)

    #file_name = file_dir + "%02u_" % (n_bits) + "heatmap_by_value" + ".png"
    file_name = file_dir + "%03u_%04u_" % (n_bits, n_regions) + desc_str + ".png"

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
    #max_count = 15
    #max_count = 6
    mean_count = np.mean(diagonal_scores)

    sns.set_style("white")
    sns.set_style("ticks")
    # sns.set_theme(style="white")

    # Generate a mask for the upper triangle
    # mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    if triangle:
        mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    else:
        mask = np.zeros_like(diagonal_scores, dtype=bool)

    #mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)
    masked_scores = ma.array(diagonal_scores, mask=mask)
    #print(masked_scores.mask)
    #print(masked_scores.data)

    #shape_mask = np.zeros_like(diagonal_scores, dtype=bool)

    # omit zero text data
    #gt0_mask = np.where(diagonal_scores > 0, False, True).astype(dtype=bool)
    #mask = gt0_mask
    #scores_text = diagonal_scores.astype('|S10')
    #annot_data = np.where(diagonal_scores > 0, scores_text, '')

    #masked_scores = ma.array(diagonal_scores, mask=mask)

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # ax.tick_params(axis='both', labelsize=fontsize)

    ax.set_title(desc_str)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Generate a custom diverging colormap
    #cmap = sns.diverging_palette(230, 20, s=75, l=50, as_cmap=True)
    #cmap = sns.diverging_palette(230, 20, s=100, as_cmap=True)
    #cmap = sns.color_palette("rocket_r", as_cmap=True)
    #cmap = sns.color_palette("Reds", as_cmap=True)


    #print(type(cmap), cmap.__dict__)

    #print(max_count, cmap.N, cmap(0), cmap(128), cmap(256))

    cmap = sns.light_palette((0.826214657892039, 0.28182798426159617, 0.0, 1.0), as_cmap=True)

    #cmap = sns.light_palette("red", as_cmap=True)

    # Recenter a divergent colormap
    if False:
        vmax = max_count
        vmin = 0
        #center = mean_count
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

    num_points = X_points.shape[0]
    #print("num_points:", num_points)

    if num_points < 80:
        linewidth = 2. / num_points
    else:
        linewidth = 0

    #print("line_width:", linewidth)


    c = ax.pcolormesh(x_vals, y_vals, masked_scores, vmax=max_count, vmin=0, edgecolor='1.0', linewidth=linewidth, cmap=cmap)
    cb = f.colorbar(c, ax=ax, shrink=0.5)  # , spacing="uniform", drawedges=True)
    cb.outline.set_linewidth(0)

    # add text box to center of each rectangle indicating count similarity
    if annot:

        # code to change the color of the text depending on cell color
        # lum = relative_luminance(color)
        # text_color = ".15" if lum > .408 else "w"
        text_color = ".15"
        #text_color = "w"

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
    tick_args = { 'axis': 'both', 'which': 'both',
        'labelsize': 'small',
        'labelbottom': False, 'bottom': False,
        'left': False, 'labelleft': False,
        'right': True, 'labelright': True}

    ## Encoding Bins Subplot
    ax0.tick_params(**tick_args)

    # draw encoder bins
    draw_multi_encoder_bins(ax0, encoder, fontsize=fontsize, xmin=xmin, xmax=xmax,
                            clip_on=True, draw_regions=False, draw_region_by_encoder=False)

    # Features Subplot (Boundaries, Weight, Crossings)
    ax1.tick_params(**tick_args)

    # share ax0 and ax1 x-axis
    ax1.get_shared_x_axes().join(ax1, ax0)

    # draw weight, crossings, and boundary features
    draw_features(ax1, encoder, colors, markersize)

    ## Similarity Subplot
    ax2.tick_params(**tick_args)

    # share ax0 and ax2 x-axis
    ax2.get_shared_x_axes().join(ax2, ax0)

    # draw similarity plot
    draw_similarity(ax2, encoder, X_gnomes, ref_points, colors, draw_regions=False,
                    draw_h_grid=True, draw_v_values=True)

    ## Encoding Bits Subplot
    tick_args['labelbottom'] = True
    tick_args['bottom'] = True
    ax3.tick_params(**tick_args)

    # share ax0 and ax3 x-axis
    ax3.get_shared_x_axes().join(ax3, ax0)

    # draw encoding bits along x-axis values
    # draw_bits_by_data(ax3, encoder, xmin=xmin, xmax=xmax, x_pad=0.0, draw_region_bits=False,
    #                 draw_uniform_samples=True, permute_bits=False, clip_on=False, draw_boundaries=False)
    draw_bits_by_data(ax3, encoder, xmin=xmin, xmax=xmax, x_pad=0.0, draw_region_bits=False,
                      draw_uniform_samples=True, permute_bits=False, clip_on=True, draw_boundaries=False)


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
    for i in range(1, 41):

        #desc_str = "RandomizedPlaceCellEncoder"
        #multi_encoder.add_encoder(RandomizedPlaceCellEncoder(n=1, seed=i))

        #desc_str = "Fixed_Weight_MultiEncoder"
        #multi_encoder.add_encoder(FixedWeightEncoder(n=6+i, w=3))

        #desc_str = "Tapering_Weight_MultiEncoder"
        #multi_encoder.add_encoder(TaperingWeightEncoder(n=6+i, w=3))

        desc_str = "PeriodicCellEncoder"
        multi_encoder.add_encoder(PeriodicCellEncoder(n=1, oob_method="modulo", seed=i))

        #plot_interval_multi_encoder(multi_encoder, desc_str=desc_str, file_dir=file_dir)
        #plt.clf()

        # self-similarity matrix by region code
        plot_heatmap(multi_encoder, desc_str=desc_str+"Similarity_Matrix_by_Region_Code", file_dir=file_dir, fontsize=6)
        plt.close()
        #plt.clf()

        # self-similarity matrix projected to real space
        plot_pmesh_heatmap(multi_encoder, desc_str=desc_str+"Similarity_Matrix_Projected_to_Real_Space", file_dir=file_dir, annot=True)
        plt.close()

    # TODO:
    # 1) + add base class boundary-handling options (exception, clamp, modulo, silent)
    # 2) + able to plot fundamental regions of periodic cells
    # 3) + plot fundamental bin and congruent bins (with lower alpha)
    # 4) create better grid distribution options, multi-scale, etc
    # 5) center fund. region for each bin
    # 6) illustrative plots for each step of discussion (Properties of Discrete Encodings of Binary Population)

