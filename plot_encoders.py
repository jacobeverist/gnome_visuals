import random

from PIL import Image

from gnomecode.encoders import *

# from encoders import *
from gnomevisual import *

from icecream import ic
import numpy as np

# from stitch_images import stitch_images

# TODO:
"""
## TODO list
# 1) + add base class boundary-handling options (exception, clamp, modulo, silent)
# 2) + able to plot fundamental regions of periodic cells
# 3) + plot fundamental bin and congruent bins (with lower alpha)
# 4) + create better grid distribution options, multi-scale, etc
# 5) - center fund. region for each bin
# 6) - illustrative plots for each step of discussion (Properties of Discrete Encodings of Binary Population)
# 7) + try to use the seaborn facet features to align heatmap x-axis with a graph plot x-axis
# 8) + replace original self-similarity plots with plot_heatmap2 and plot_pmesh_heatmap2,
#      figure out style issues (add seaborn layout)
# 9) + remove plot_heatmap and plot_pmesh_heatmap code
# 10)+ plot_encoders.py should be figure-level and axes-level styling code, and axesplots.py should be axes-level plotting


## Current implemented encoders in gnomevisual.encoders
# "MultiEncoder",
# "PeriodicCellEncoder",
# "RandomizedPlaceCellEncoder",
# "FixedWeightEncoder", "TaperingWeightEncoder"


## FOREACH encoder type and config
# test numpy array input (n,)
# test list of floats input
# test different interval upper and lower bounds
# test different weight 'w'
# test different interval length 'L'
# test oob_method 'silent'
# test oob_method 'modulo'
# test oob_method 'clamp'
# test oob_method 'exception'

## test numpy array input (n,1)
# X = np.array([[0.21], [0.69], [0.91]])
# result = multi_encoder.encode(X)
# print(X, result)kkkk

## test scalar input
# result = multi_encoder.encode(-1)
# print(-1, result)

# experiment = "RandomizedPlaceCellEncoder"
# RandomizedPlaceCellEncoder(n=1, seed=i)

# experiment = "Fixed_Weight_MultiEncoder"
# FixedWeightEncoder(n=5+i, w=1)

# experiment = "Tapering_Weight_MultiEncoder"
# TaperingWeightEncoder(n=6+i, w=3)

"""


def quad_merge(im1, im2, im3, im4):
    """

    Args:
        im1:
        im2:
        im3:
        im4:

    Returns:

    """
    w1 = max(im1.size[0], im3.size[0])
    w2 = max(im2.size[0], im4.size[0])
    w = w1 + w2

    h1 = max(im1.size[1], im2.size[1])
    h2 = max(im3.size[1], im4.size[1])
    h = h1 + h2

    # w = max(im1.size[0], im3.size[0]) + max(im2.size[0], im4.size[0])
    # h = max(im1.size[1], im2.size[1]) + max(im3.size[1], im4.size[1])

    # h = im1.size[1] + im3.size[1]
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (w1, 0))
    im.paste(im3, (0, h1))
    im.paste(im4, (w1, h1))

    return im


def stitch_images(filenames, output_str, input_dir="", output_dir="out/"):
    """

    Args:
        filenames:
        output_str:
        input_dir:
        output_dir:

    Returns:

    """
    for i in range(int(len(filenames) / 4)):
        im1 = Image.open(input_dir + filenames[i * 4 + 0])
        im2 = Image.open(input_dir + filenames[i * 4 + 1])
        im3 = Image.open(input_dir + filenames[i * 4 + 2])
        im4 = Image.open(input_dir + filenames[i * 4 + 3])

        result_img = quad_merge(im1, im2, im3, im4)

        # shrink it to 1/4
        (width, height) = (result_img.width // 4, result_img.height // 4)
        im_final = result_img.resize((width, height))
        print("saving", output_dir + output_str % (i + 1))
        im_final.save(output_dir + output_str % (i + 1))


def plot_compact_and_heatmap(multi_encoder, file_dir, experiment, w_param,
                             draw_folded_bins=True,
                             annot=False,
                             compact_suffix="Features",
                             heatmap_suffix="Similarity_Matrix_Projected_to_Real_Space"
                             ):
    ref_points=[-0.5,]
    # ref_points=[0.499,]
    # ref_points=[0.5,]
    # ref_points=[0.21]
    # ref_points = [0.21, 0.45]
    # ref_points=[0.21, 0.45, 0.75, 0.9]
    # ref_points=[]
    plot_compact_multi_encoder(multi_encoder, desc_str=experiment, draw_folded_bins=draw_folded_bins, w_param=w_param,
                               ref_points=ref_points)
    feature_file = save_fig(file_dir, multi_encoder, experiment + "_" + compact_suffix, w_param=w_param)

    plot_realspace_heatmap(multi_encoder, desc_str=experiment, w_param=w_param, annot=annot)
    heatmap_file = save_fig(file_dir, multi_encoder, experiment + "_" + heatmap_suffix, w_param=w_param)

    return feature_file, heatmap_file


def run_experiment1():
    """

    Returns:

    """
    # Constants
    file_dir = "out/"
    test_place = PlaceCellEncoder()
    test_place.add_cell(0.1, 0.2)
    test_place.add_cell(0.15, 0.25)
    test_place.add_cell(0.05, 0.3)

    multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
    multi_encoder.add_encoder(test_place)
    print(multi_encoder.bins)
    print(multi_encoder.region_boundaries)
    print(multi_encoder.region_centers)
    print(multi_encoder.region_weights)
    print(multi_encoder.region_codes)

    # offsets = [random.uniform(-0.2, 0.2)]

    feature_filenames = []
    heatmap_filenames = []

    for w_param in [1, 2, 3]:

        # 2^n, equal bin size
        experiment = "2n_equal_binsize_zerocenter_PeriodicScalarEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [4, 8, 12, 16]:
            period = n / 16.0
            offset = -w_param * period / (2 * n)

            multi_encoder.add_encoder(
                    PeriodicScalarEncoder(n=n, w=w_param, period=n / 16.0, lower_bound=offset,
                                          upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, w_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

        # 2^n, equal period
        experiment = "2n_equal_period_zerocenter_PeriodicScalarEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [4, 8, 12, 16]:
            period = 1.0
            offset = -w_param * period / (2 * n)
            multi_encoder.add_encoder(
                    PeriodicScalarEncoder(n=n, w=w_param, period=1.0, lower_bound=offset, upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, w_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

        # prime, equal binsize
        experiment = "prime_equal_binsize_zerocenter_PeriodicScalarEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [5, 7, 11, 13]:
            period = n / 13.0
            offset = -w_param * period / (2 * n)
            multi_encoder.add_encoder(
                    PeriodicScalarEncoder(n=n, w=w_param, period=n / 13.0, lower_bound=offset,
                                          upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, w_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

        # prime, equal period
        experiment = "prime_equal_period_zerocenter_PeriodicScalarEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [5, 7, 11, 13]:
            period = 1.0
            offset = -w_param * period / (2 * n)
            multi_encoder.add_encoder(
                    PeriodicScalarEncoder(n=n, w=w_param, period=1.0, lower_bound=offset, upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, w_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

    feature_str = "Features_Compact_zero_PeriodicScalar_w%d.png"
    heatmap_str = "Heatmap_zero_PeriodicScalar_w%d.png"

    print(feature_filenames)
    print(heatmap_filenames)

    stitch_images(heatmap_filenames, heatmap_str)
    stitch_images(feature_filenames, feature_str)


def run_experiment2():
    """

    Returns:

    """
    # Constants
    file_dir = "out/"

    feature_filenames = []
    heatmap_filenames = []

    # for l_param in [0.01, 0.02, 0.03]:
    # for test_num in [1, 2, 3]:
    for test_num in [3]:

        l_param = test_num * 0.05

        # 2^n, equal bin size
        experiment = "2n_equal_binsize_zerocenter_PeriodicCellEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        # period = 1.0
        offset = -l_param  # * period / (2 * n)
        # origin = 0.5*offset
        # origin = 2.0*offset
        origin = 0.5 - l_param / 2.0
        ic(offset, origin)

        # encoder = PeriodicCellEncoder(n=10, period=1.0)
        # encoder = PeriodicCellEncoder(n=10, period=1.0, l_frac=0.1)
        # encoder = PeriodicCellEncoder(n=10, period=1.0, l=0.1)

        periodic_encoder = PeriodicCellEncoder(n=8, l=l_param, period=1.0, do_rand=True)
        multi_encoder.add_encoder(periodic_encoder)

        periodic_encoder = PeriodicCellEncoder(n=8, l_frac=0.5, do_rand=True)
        multi_encoder.add_encoder(periodic_encoder)

        periodic_encoder = PeriodicCellEncoder(n=8, l_frac=0.5)  # , do_rand=True)
        multi_encoder.add_encoder(periodic_encoder)

        assemble_encoder = MultiPeriodicEncoder(xmin=-1.0, xmax=2.0)
        rng = assemble_encoder.rng
        origins = rng.uniform(0.0, 1.0, 8)
        periods = rng.uniform(0.1, 0.5, 8)

        for k in range(4):
            bin_length = rng.uniform(0.05, periods[k] / 2.0, 1)[0]
            periodic_encoder = PeriodicCellEncoder(l=bin_length, origin=origins[k], period=periods[k])
            ic(bin_length)
            ic(periodic_encoder)
            assemble_encoder.add_encoder(periodic_encoder)
        periodic_encoder = PeriodicCellEncoder(n=4)
        assemble_encoder.add_encoder(periodic_encoder)

        multi_encoder.add_encoder(assemble_encoder)

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, test_num,
                                                              draw_folded_bins=False)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

    """
        # 2^n, equal period
        experiment = "2n_equal_period_zerocenter_PeriodicCellEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [4, 8, 12, 16]:
            period = 1.0
            offset = -l_param * period / (2 * n)
            multi_encoder.add_encoder(
                    PeriodicCellEncoder(n=n, l=l_param, period=1.0, lower_bound=offset, upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, l_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

        # prime, equal binsize
        experiment = "prime_equal_binsize_zerocenter_PeriodicCellEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [5, 7, 11, 13]:
            period = n / 13.0
            offset = -l_param * period / (2 * n)
            multi_encoder.add_encoder(
                    PeriodicCellEncoder(n=n, l=l_param, period=n / 13.0, lower_bound=offset,
                                          upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, l_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)

        # prime, equal period
        experiment = "prime_equal_period_zerocenter_PeriodicCellEncoder"
        multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
        for n in [5, 7, 11, 13]:
            period = 1.0
            offset = -l_param * period / (2 * n)
            multi_encoder.add_encoder(
                    PeriodicCellEncoder(n=n, l=l_param, period=1.0, lower_bound=offset, upper_bound=1.0 + offset))

        feature_file, heatmap_file = plot_compact_and_heatmap(multi_encoder, file_dir, experiment, l_param)
        feature_filenames.append(feature_file)
        heatmap_filenames.append(heatmap_file)
    """

    feature_str = "Features_Compact_zero_PeriodicCell_w%d.png"
    heatmap_str = "Heatmap_zero_PeriodicCell_w%d.png"

    print(feature_filenames)
    print(heatmap_filenames)

    stitch_images(heatmap_filenames, heatmap_str)
    stitch_images(feature_filenames, feature_str)


def plot_layouts():
    # Constants
    file_dir = "out/"
    w_param = 3
    experiment = "layouts_2n_equal_period_zerocenter_PeriodicScalarEncoder"
    multi_encoder = MultiEncoder(xmin=-1.0, xmax=2.0)
    period = 1.0
    n = 8
    offset = -w_param * period / (2 * n)
    multi_encoder.add_encoder(
            PeriodicScalarEncoder(n=n, w=w_param, period=1.0, lower_bound=offset, upper_bound=1.0 + offset))

    # PLOT EXAMPLES
    # Plot Feature
    plot_interval_multi_encoder(multi_encoder, desc_str=experiment, draw_folded_bins=True, w_param=w_param)
    save_fig(file_dir, multi_encoder, experiment + "_" + "Features", w_param=w_param)

    # Plot Compact
    plot_compact_multi_encoder(multi_encoder, desc_str=experiment, draw_folded_bins=True, w_param=w_param,
                               # ref_points=[0.21, 0.75])
                               )

    save_fig(file_dir, multi_encoder, experiment + "_" + "Features", w_param=w_param)

    # Plot Similarity Matrix by Code
    plot_code_heatmap(multi_encoder, desc_str=experiment, annot=False)
    save_fig(file_dir, multi_encoder, experiment + "_" + "Similarity_Matrix_by_Region_Code", w_param=w_param)

    # Plot Similarity Matrix by Real Space
    plot_realspace_heatmap(multi_encoder, desc_str=experiment, w_param=w_param, annot=False)
    save_fig(file_dir, multi_encoder, experiment + "_" + "Similarity_Matrix_Projected_to_Real_Space", w_param=w_param)

    # Plot Difference Matrix by Code
    plot_diff_heatmap(multi_encoder, desc_str=experiment, annot=False)
    save_fig(file_dir, multi_encoder, experiment + "_" + "Difference_Matrix_by_Region_Code", w_param=w_param)


if __name__ == "__main__":
    # run_experiment1()
    run_experiment2()
    # plot_layouts()

    # import numpy as np
    #
    # ref_points = np.array([[0.21], [0.75]])
    #
    # print(ref_points.shape)
