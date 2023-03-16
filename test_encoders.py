# plotting
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="white", color_codes=True)

try:
    from encoders.encoders import *
    from encoders.visuals import *
    from encoders.helpers import *
except:
    from encoder_analysis.encoders.encoders import *
    from encoder_analysis.encoders.visuals import *
    from encoder_analysis.encoders.helpers import *


def plot_heatmap(encoder, desc_str="Encoder", lower_bound=0.0, upper_bound=1.0, file_dir="./out"):
    w = encoder.w
    n_bits = encoder.n

    file_name = file_dir + "%02u_%02u_" % (w, n_bits) + "heatmap_" + encoder.__class__.__name__ + ".png"

    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)
    X_gnomes1 = encoder.region_codes
    X_gnomes2 = encoder.encode(X_points)

    diagonal_scores = count_similarity(X_gnomes1, X_gnomes2)
    max_count = np.max(diagonal_scores)
    mean_count = np.mean(diagonal_scores)

    sns.set_theme(style="white")

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    ax.set_title(desc_str)

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(diagonal_scores, mask=mask, cmap=cmap, vmax=max_count, center=mean_count,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


def plot_pmesh_heatmap(encoder, desc_str="Encoder", lower_bound=0.0, upper_bound=1.0, file_dir="./out"):
    w = encoder.w
    n_bits = encoder.n

    file_name = file_dir + "%02u_%02u_" % (w, n_bits) + "pmesh_heatmap_" + encoder.__class__.__name__ + ".png"

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

    sns.set_theme(style="white")

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(diagonal_scores, dtype=bool), k=1)

    import numpy.ma as ma
    masked_scores = ma.array(diagonal_scores, mask=mask)

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

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

    # c = ax.pcolormesh(x_vals, y_vals, diagonal_scores, vmax=max_count, vmin=0, edgecolor='1.0', linewidth=0.3, cmap=cmap)
    c = ax.pcolormesh(x_vals, y_vals, masked_scores, vmax=max_count, vmin=0, edgecolor='1.0', linewidth=0.3, cmap=cmap)
    cb = f.colorbar(c, ax=ax, shrink=0.5)  # , spacing="uniform", drawedges=True)
    cb.outline.set_linewidth(0)

    print("x_vals:", len(x_vals), x_vals)
    print("y_vals:", len(y_vals), y_vals)
    print("masked_scores:", masked_scores.shape)

    fontsize = 8

    print("x_centers:", len(x_centers), x_centers)
    print("y_centers:", len(y_centers), y_centers)

    for i in range(len(x_centers)):
        x = x_centers[i]

        for j in range(len(y_centers)):
            y = y_centers[j]
            score = masked_scores[j, i]

            # if score != "--":
            if score is not np.ma.masked:
                # add text box to center of rectangle
                ax.text(x, y, str(score), horizontalalignment='center', verticalalignment='center',
                        fontsize=fontsize)  # , color='1.0')
                # , clip_on=clip_on, alpha=alpha, transfom=ax.transAxes)

    """
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

    # Draw the heatmap with the mask and correct aspect ratio
    # sns.heatmap(diagonal_scores, mask=mask, cmap=cmap, vmax=max_count, center=mean_count,
    #            square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True)

    if not file_name is None:
        plt.savefig(file_name, bbox_inches='tight')


def plot_interval_encoder(encoder, desc_str="Encoder", lower_bound=0.0, upper_bound=1.0, file_dir="./out"):
    w = encoder.w
    n_bits = encoder.n

    file_name = file_dir + "%02u_%02u_" % (w, n_bits) + encoder.__class__.__name__ + ".png"

    # reference points for comparison
    ref_points = np.array([[0.21], [0.69]])
    ref_gnomes = encoder.encode(ref_points)

    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)

    # encodings
    X_gnomes = encoder.encode(X_points)

    # similarity scores
    scores = gnome_similarity(X_gnomes, ref_gnomes)

    # boundaries and crossings
    boundaries = encoder.region_boundaries
    deltas = encoder.region_deltas

    # Draw Plots in Each SubAxes
    # subplot_kw, gridspec_kw
    fig = plt.figure(num=1, figsize=(10, 8), dpi=200, constrained_layout=True)
    fig, axes = plt.subplots(6, 1, num=1, gridspec_kw={'height_ratios': [1, 0.5, 0.5, 0.5, 0.5, 1]})  # , sharex=True)
    ax0 = axes[0]
    ax1 = axes[1]
    ax2 = axes[2]
    ax3 = axes[3]
    ax4 = axes[4]
    ax5 = axes[5]
    colors = sns.color_palette("Set1", n_colors=len(ref_points))

    # Encoding Plot
    # ax0.set_title("%s, n=%d, w=%d" % (desc_str,n_bits,w))
    # ax0.tick_params(
    #    axis='both',
    #    which='both',
    #    bottom=False,
    #    left=False,
    #    right=True,
    #    labelbottom=False,
    #    labelleft=False,
    #    labelright = True, labelsize = 'small')
    # ax0.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    # ax0.set_ylim(0, n_bits)
    # ax0.set_ylabel("Encoded Bits")
    # draw_encoding(ax0, X_gnomes)

    ax0.set_title("%s, n=%d, w=%d" % (desc_str, n_bits, w))
    ax0.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        right=True,
        labelbottom=False,
        labelleft=False,
        labelright=True, labelsize='small')
    ax0.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    ax0.set_ylim(-0.5, n_bits + 0.5)
    ax0.set_ylabel("Bins")

    draw_encoder_bins(ax0, encoder)

    # Granulation Plot
    # ax1.set_xlim(lower_bound, upper_bound)
    ax1.set_ylim(0.0, 1.0)
    ax1.set_axis_on()
    ax1.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        right=False,
        labelbottom=False,
        labelleft=False)
    ax1.set_ylabel("Decomposition")
    ax1.get_shared_x_axes().join(ax1, ax0)
    ax1.vlines([0.0, 1.0], ymin=-100, ymax=100, color='k', alpha=0.2)

    draw_decomposition(ax1, boundaries)

    max_change_count = max(encoder.region_weights)

    ax2.tick_params(
        axis='both',
        which='both',
        bottom=True,
        left=False,
        right=True,
        labelbottom=False,
        labelleft=False,
        labelright=True)

    ax2.set_ylim(bottom=0, top=max_change_count + 0.5)
    ax2.set_ylabel("Delta Count")
    ax2.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    # ax3.set_ylim(bottom=0, top=max_change_count)

    # share ax1 and ax2 x-axis
    ax2.get_shared_x_axes().join(ax2, ax1)

    # fix x-axis to interval bounds
    ax2.set_xlim(lower_bound, upper_bound)

    # draw_delta_count(ax2, boundaries, deltas)
    # ax2.plot(boundaries, deltas, color='k')
    # ax2.scatter(boundaries, deltas, color='k')
    ax2.bar(boundaries, deltas, width=0.005, linewidth=0, color='k')

    for k in range(len(boundaries)):
        ax2.axvline(x=boundaries[k], ymin=-1, ymax=max_change_count + 1, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    bin_weights = encoder.region_weights
    max_bin_weight = max(bin_weights)

    ax3.tick_params(
        axis='both',
        which='both',
        bottom=True,
        left=False,
        right=True,
        labelbottom=False,
        labelleft=False,
        labelright=True)

    ax3.set_ylim(bottom=0, top=max_bin_weight + 0.5)
    ax3.set_ylabel("Weight")
    ax3.yaxis.set_major_locator(ticker.IndexLocator(1, 0))

    # share ax1 and ax3 x-axis
    ax3.get_shared_x_axes().join(ax3, ax2)

    # fix x-axis to interval bounds
    ax3.set_xlim(lower_bound, upper_bound)

    # draw_delta_count(ax3, boundaries, deltas)

    bin_weights_y = np.append(bin_weights, [bin_weights[-1], ])

    # plt.step(x_data, y_data, where='pre', label='vert_first')

    # ax3.step(boundaries, bin_weights_y, where='pre', color='k')
    ax3.step(boundaries, bin_weights_y, where='post', color='k')
    # ax3.plot(boundaries, bin_weights_y, color='k')
    # ax3.scatter(boundaries, deltas, color='k')

    for k in range(len(boundaries)):
        ax3.axvline(x=boundaries[k], ymin=-1, ymax=max_bin_weight + 1, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    # Similarity Plot
    ax4.tick_params(
        axis='both',
        which='both',
        bottom=True,
        left=False,
        right=True,
        labelbottom=True,
        labelleft=False,
        labelright=True)
    ax4.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    ax4.set_ylabel("Similarity")
    for k in range(len(ref_points)):
        # ax4.plot(X_points, scores[:, k], color=colors[k], label=float(ref_points[k]))
        # ax4.step(X_points, scores[:, k], where='mid', marker='o', markersize=4, color=colors[k], label=float(ref_points[k]))
        ax4.step(X_points, scores[:, k], where='mid', color=colors[k], label=float(ref_points[k]))

    # share ax1 and ax2 x-axis
    ax4.get_shared_x_axes().join(ax4, ax3)

    # fix x-axis to interval bounds
    ax4.set_xlim(lower_bound, upper_bound)
    ax4.xaxis.set_major_locator(ticker.LinearLocator(5))

    for k in range(len(ref_points)):
        ax4.axvline(x=ref_points[k], ymin=-0.1, ymax=2.1, alpha=0.4, linewidth=1.5, color=colors[k], linestyle='--',
                    clip_on=True)
        # clip_on = False)

    for k in range(len(boundaries)):
        ax4.axvline(x=boundaries[k], ymin=-0.1, ymax=2.1, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    handles, labels = ax4.get_legend_handles_labels()
    handles.reverse()
    labels.reverse()
    # legend = fig.legend(handles, labels, title="Reference Value", bbox_to_anchor=(0.98, 1),
    #                    bbox_transform=ax4.transAxes)

    # Granulation Plot
    # ax1.set_xlim(lower_bound, upper_bound)

    ax5.tick_params(
        axis='both',
        which='both',
        bottom=False,
        left=False,
        right=True,
        labelbottom=False,
        labelleft=False,
        labelright=True, labelsize='small')
    ax5.yaxis.set_major_locator(ticker.IndexLocator(1, 0))
    ax5.set_ylim(-0.5, n_bits + 0.5)
    ax5.set_ylabel("Bits")
    ax5.get_shared_x_axes().join(ax5, ax4)

    draw_bits_by_data(ax5, encoder)
    # draw_encoder_bins(ax5, encoder)

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
    plot_interval_multi_encoder(multi_encoder, "FixedWeightEncoder", file_dir=file_dir)
    plt.clf()

    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(TaperingWeightEncoder(n=20, w=3))
    plot_interval_multi_encoder(multi_encoder, "TaperingWeightEncoder", file_dir=file_dir)
    plt.clf()
    """

    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(PlaceCellEncoder(n=40))
    plot_interval_multi_encoder(multi_encoder, "PlaceEncoder", file_dir=file_dir)
    plt.clf()

    # plot_heatmap(multi_encoder, "MultiEncoder Self-Similarity", file_dir=file_dir)
    # plt.clf()

    # plot_pmesh_heatmap(multi_encoder, "MultiEncoder Self-Similarity", file_dir=file_dir)
    # plt.clf()

    # plot_interval_encoder(taper_encoder, "Tapering Weight Encoder", file_dir=file_dir)
    # plt.clf()
    # plot_interval_encoder(fixed_encoder, "Fixed Weight Encoder", file_dir=file_dir)
    # plt.clf()
