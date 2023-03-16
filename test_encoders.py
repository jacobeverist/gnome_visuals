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


def plot_interval_multi_encoder(encoder, desc_str="Encoder", lower_bound=0.0, upper_bound=1.0, file_dir="./out"):
    n_bits = encoder.n
    markersize = 4

    # file_name = file_dir + "%02u_%02u_" % (w, n_bits) + encoder.__class__.__name__ + ".png"
    file_name = file_dir + "%02u_" % (n_bits) + desc_str + ".png"

    # reference points for comparison
    ref_points = np.array([[0.21], [0.69]])
    ref_gnomes = encoder.encode(ref_points)

    # sampled points over the space
    X_points = np.array(encoder.region_centers).reshape(-1, 1)

    # encodings
    X_gnomes2 = encoder.encode(X_points)

    # count similarity scores
    scores2 = count_similarity(X_gnomes2, ref_gnomes)

    # boundaries and crossings
    boundaries = encoder.region_boundaries
    deltas = encoder.region_deltas

    # for plotting purposes
    X_point_lower = lower_bound - 0.5
    X_point_upper = upper_bound + 0.5
    X_gnome_lower = encoder.encode(X_point_lower).reshape(1, -1)
    X_gnome_upper = encoder.encode(X_point_upper).reshape(1, -1)
    X_points_extended = np.concatenate(
        ([X_point_lower], encoder.region_centers, [X_point_upper]))
    X_gnomes_extended = np.concatenate(
        (X_gnome_lower, X_gnomes2, X_gnome_upper), axis=0)
    boundaries_extended = np.concatenate(
        ([lower_bound - 1.0], encoder.region_boundaries, [upper_bound + 1.0]))

    scores_extended = count_similarity(X_gnomes_extended, ref_gnomes)

    print("X_points_extended:", X_points_extended.shape)
    print(X_points_extended)
    print("X_gnomes_extended:", X_gnomes_extended.shape)
    print(X_gnomes_extended)
    print("boundaries_extended:", boundaries_extended.shape)
    print(boundaries_extended)
    print("scores_extended:", scores_extended.shape)
    print(scores_extended)

    # Draw Plots in Each SubAxes
    # subplot_kw, gridspec_kw
    fig = plt.figure(num=1, figsize=(10, 8), dpi=300, constrained_layout=True)
    fig, axes = plt.subplots(4, 1, num=1, gridspec_kw={'height_ratios': [1, 1, 1, 1]})  # , sharex=True)

    ax0 = axes[0]
    ax2 = axes[1]
    ax4 = axes[2]
    ax5 = axes[3]
    colors = sns.color_palette("Set1", n_colors=len(ref_points))

    # Encoding Bins Subplot
    ax0.set_title("%s, n=%d" % (desc_str, n_bits))
    ax0.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        bottom=False,
        left=False,
        right=True,
        labelleft=False,
        labelright=True, labelsize='small')
    ax0.yaxis.set_major_locator(ticker.IndexLocator(5, 0))
    #ax0.set_ylim(-0.5, n_bits + 0.5)
    ax0.set_ylim(-0.1, n_bits + 0.1)
    ax0.set_ylabel("Encoding Bins\non Interval")

    # draw_encoder_bins(ax0, encoder, fontsize=6)
    draw_multi_encoder_bins(ax0, encoder, fontsize=6, xmin=lower_bound - 0.1, xmax=upper_bound + 0.1, clip_on=False)

    # Features Subplot (Boundaries, Weight, Crossings)
    ax2.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        bottom=False,
        left=False,
        right=True,
        labelleft=False,
        labelright=True)

    # Data for Features
    bin_weights = encoder.region_weights
    max_bin_weight = max(bin_weights)
    bin_weights_y = np.append(bin_weights, [bin_weights[-1], ])

    # scale y-axis properties
    ax2.set_ylim(-0.1, max_bin_weight + 2)
    #ax2.yaxis.set_major_locator(ticker.IndexLocator(5, 0))
    ax2.yaxis.set_major_locator(ticker.IndexLocator(2, 0))
    ax2.set_ylabel("Features of\nEncodings")

    # share ax0 and ax2 x-axis
    ax2.get_shared_x_axes().join(ax2, ax0)

    # set central ordinal value on y-axis for swarmplot
    bottom, top = ax2.get_ylim()
    swarm_ordinal = (top - bottom) / 2.0 + bottom

    # points repeated for each delta count
    repeat_boundaries = []
    for k in range(len(deltas)):
        count = deltas[k]
        for j in range(count):
            repeat_boundaries.append(boundaries[k])

    # ordinal number that we want swarm points to be plotted on the y-axis
    y_vals = [swarm_ordinal for k in range(len(repeat_boundaries))]

    # FIXME: hacked seaborn by adding a second category with ordinal number out of plot range.
    #  Enables swarm points beyond unit category range
    #  This point is plotted, but not seen since '-100' is far out of axes y-range
    repeat_boundaries.append(0.0)
    y_vals.append(-100)

    # do swarm plot
    sns.swarmplot(x=repeat_boundaries, y=y_vals, orient='h', color=colors[0], ax=ax2, size=4, native_scale=True,
                  legend=False, label="Crossings")

    # remove extra category
    repeat_boundaries.pop(-1)
    y_vals.pop(-1)

    # draw grid lines representing boundaries between regions
    #ax2.axvline(x=boundaries[0], alpha=0.2, linewidth=0.5, color='k', zorder=-1,
    #            label="Boundary")
    #for k in range(1, len(boundaries)):
    #    ax2.axvline(x=boundaries[k], alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    for k in range(0, max_bin_weight + 3):
        ax2.hlines(y=k, xmin=lower_bound-0.1, xmax=upper_bound+0.1, alpha=0.2, linewidth=0.5, color='k', zorder=-1)


    # draw gnome weights
    ax2.step(boundaries, bin_weights_y, where='post', color=colors[1], alpha=0.6, zorder=1, label="Weight")
    ax2.fill_between(boundaries, -1, bin_weights_y, step='post', color=colors[1], alpha=0.3, zorder=1)

    # legend labels and handles
    handles1, labels1 = ax2.get_legend_handles_labels()

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
    legend = ax2.legend(handles1, labels1, title="Features", ncol=3, fontsize=8, title_fontsize=9)

    ## Similarity Subplot

    # data to plot
    max_score = np.max(scores2)

    ax4.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        bottom=False,
        left=False,
        right=True,
        labelleft=False,
        labelright=True)

    # scale y-axis to maximum of weight
    ax4.set_ylim(-0.1, max_score + 2)
    #ax4.yaxis.set_major_locator(ticker.IndexLocator(5, 1))
    ax4.yaxis.set_major_locator(ticker.IndexLocator(2, 1))
    ax4.set_ylabel("Similarity of\nExample Values")

    # share ax0 and ax4 x-axis
    ax4.get_shared_x_axes().join(ax4, ax0)

    # plot similarity scores for each reference value
    for k in range(len(ref_points)):
        # print(X_points_extended)
        # print(X_gnomes_extended)
        # print(boundaries_extended)
        # print(scores_extended)

        # boundaries_x = boundaries
        # scores_y = np.append(scores2[:, k], [scores2[-1, k], ])

        boundaries_x = boundaries_extended
        scores_y = np.append(scores_extended[:, k], [scores_extended[-1, k], ])

        ax4.step(boundaries_x, scores_y, where='post', color=colors[k], label=float(ref_points[k]))
        ax4.fill_between(boundaries_x, -1, scores_y, step='post', color=colors[k], alpha=0.3, zorder=1)

    # draw vertical line indicating reference value on x-axis
    for k in range(len(ref_points)):
        ax4.axvline(x=ref_points[k], ymax=3.2, alpha=1.0, linewidth=1.5, color=colors[k], linestyle='--', clip_on=False)

    # draw boundaries between each region
    #for k in range(len(boundaries)):
    #    ax4.axvline(x=boundaries[k], alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    for k in range(max_score + 3):
        ax4.hlines(y=k, xmin=lower_bound-0.1, xmax=upper_bound+0.1, alpha=0.2, linewidth=0.5, color='k', zorder=-1)

    # show legend for each example value
    handles, labels = ax4.get_legend_handles_labels()
    handles.reverse()
    labels.reverse()
    legend = ax4.legend(handles, labels, title="Similarity of", ncol=2, fontsize=8, title_fontsize=8)

    ## Encoding Bits Subplot
    ax5.tick_params(
        axis='both',
        which='both',
        labelbottom=True,
        bottom=True,
        left=False,
        right=True,
        labelleft=False,
        labelright=True, labelsize='small')

    # scale y-axis to number of bits
    ax5.yaxis.set_major_locator(ticker.IndexLocator(5, 0))
    ax5.set_ylim(-0.5, n_bits + 0.5)
    ax5.set_ylabel("Bit Encoding vs.\nReal Value")

    # share ax0 and ax5 x-axis
    ax5.get_shared_x_axes().join(ax5, ax0)

    # draw encoding bits along x-axis values
    # draw_bits_by_data(ax5, encoder, xmin=lower_bound-0.1, xmax=upper_bound+0.1, sampling=False, permute_bits=True, clip_on=False)
    draw_bits_by_data(ax5, encoder, xmin=lower_bound - 0.1, xmax=upper_bound + 0.1, draw_region_bits=True,
                      draw_uniform_samples=False, permute_bits=False, clip_on=False)

    # set xlim lower and upper bounds for all subplots
    # ax5.set_xlim(lower_bound, upper_bound)
    ax5.set_xlim(lower_bound - 0.1, upper_bound + 0.1)

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

    # print(multi_encoder.upper_bound)
    # print(multi_encoder.lower_bound)
    # print(multi_encoder.L)

    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(FixedWeightEncoder(n=20, w=3))
    plot_interval_multi_encoder(multi_encoder, "FixedWeightEncoder", file_dir=file_dir)
    plt.clf()

    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(TaperingWeightEncoder(n=20, w=3))
    plot_interval_multi_encoder(multi_encoder, "TaperingWeightEncoder", file_dir=file_dir)
    plt.clf()

    multi_encoder = MultiEncoder()
    multi_encoder.add_encoder(PlaceCellEncoder(n=20))
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
