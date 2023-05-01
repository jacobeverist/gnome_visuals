import numpy as np
from gnomecode import *
from line_profiler_pycharm import profile


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


## Current implemented encoders in gnomecode.encoders
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


def run_experiment():
    # Constants
    file_dir = "out/"
    #experiment = "PeriodicCellEncoder"
    experiment = "PeriodicScalarEncoder"
    #experiment = "FixedWeightEncoder"
    #experiment = "TaperingWeightEncoder"
    #experiment = "PlaceCellEncoder"

    # Initalize Encoder
    multi_encoder = MultiEncoder(upper_bound=2.0, lower_bound=-1.0)
    #multi_encoder = PeriodicScalarEncoder(n=8, period=0.5, xmin=0, xmax=2)

    #for i in [2, 3, 5, 7]:
    #    multi_encoder.add_encoder(PeriodicScalarEncoder(n=i, period=0.5, xmin=0, xmax=2))
        #multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=1))
    #for i in [5, 7, 11, 13]:
    #    multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=2))

    #multi_encoder.add_encoder(PeriodicScalarEncoder(n=3, w=1, period=0.5, xmin=0, xmax=2))
    #multi_encoder.add_encoder(PeriodicScalarEncoder(n=5, w=2, period=0.5, xmin=0, xmax=2))
    #multi_encoder.add_encoder(PeriodicScalarEncoder(n=7, w=3, period=0.5, xmin=0, xmax=2))
    #multi_encoder.add_encoder(FixedWeightEncoder(n=5, w=2, lower_bound=0, upper_bound=1))
    #multi_encoder.add_encoder(FixedWeightEncoder(n=8, w=3, upper_bound=1))

    #multi_encoder.add_encoder(PeriodicScalarEncoder(n=1000, w=3, period=0.5, xmin=0, xmax=1))
    #for i in range(0, 100):
    #    multi_encoder.add_encoder(PeriodicScalarEncoder(n=8, w=3, period=0.5, xmin=0, xmax=1))

    #for i in range(7, 9):
    #    multi_encoder.add_encoder(PeriodicScalarEncoder(n=i, w=3, period=0.5, xmin=0, xmax=1))
    #multi_encoder.add_encoder(FixedWeightEncoder(n=8, w=3, upper_bound=1))

    #for i in [7, 11, 13, 17]:
    #    multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=3, upper_bound=1))

    #for i in range(4):
    #    multi_encoder.add_encoder(PeriodicScalarEncoder(n=2**i, period=0.5, xmin=0, xmax=1))

    #for i in [7, 11, 13, 19]:
    #    multi_encoder.add_encoder(TaperingWeightEncoder(n=i, w=3))

    w_param = 1
    # multi_encoder.add_encoder(FixedWeightEncoder(n=16, w=w_param))
    #multi_encoder.add_encoder(FixedWeightEncoder(n=8, w=w_param))

    #for i in [4, 8, 12, 16]:
    #    multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=w_param))

    #for i in [5, 7, 11, 13]:
    #    multi_encoder.add_encoder(FixedWeightEncoder(n=i, w=w_param))
    #multi_encoder.add_encoder(RandomizedPlaceCellEncoder(n=100, seed=0))

    #multi_encoder.add_encoder(PeriodicCellEncoder(n=100, seed=0))
    #multi_encoder.add_encoder(PeriodicCellEncoder(n=20, seed=0))
    multi_encoder.add_encoder(PeriodicCellEncoder(n=10, seed=0, lower_bound=-1, upper_bound=2))
    multi_encoder.add_encoder(PeriodicScalarEncoder(n=10, period=0.5, xmin=-1, xmax=2))

    for i in range(10, 11):
        # Change Encoder
        #multi_encoder.add_encoder(PeriodicCellEncoder(n=i, oob_method="modulo", seed=i))
        #multi_encoder.add_encoder(RandomizedPlaceCellEncoder(n=1, seed=i))
        #multi_encoder.add_encoder(FixedWeightEncoder(n=5+i, w=1))
        #multi_encoder.add_encoder(TaperingWeightEncoder(n=6+i, w=3))
        #multi_encoder.add_encoder(PeriodicScalarEncoder())
        #multi_encoder.add_encoder(PeriodicScalarEncoder(n=8, period=0.5, xmin=0, xmax=2))

        #print(multi_encoder.__dict__)
        #for bin in multi_encoder.bins:
        #    print(bin)
        #print(multi_encoder.straddles)

        # Plot Feature
        plot_interval_multi_encoder(multi_encoder, desc_str=experiment, w_param=w_param, x_pad=1.0)
        save_fig(file_dir, multi_encoder, "Features", experiment, w_param=w_param)

        # Plot Similarity Matrix by Code
        #plot_code_heatmap(multi_encoder, desc_str=experiment, annot=False)
        #save_fig(file_dir, multi_encoder, "Similarity_Matrix_by_Region_Code", experiment)

        # Plot Similarity Matrix by Real Space
        plot_realspace_heatmap(multi_encoder, desc_str=experiment, w_param=w_param)
        save_fig(file_dir, multi_encoder, "Similarity_Matrix_Projected_to_Real_Space", experiment, w_param=w_param)

        # Plot Difference Matrix by Code
        #plot_diff_heatmap(multi_encoder, desc_str=experiment, annot=False)
        #save_fig(file_dir, multi_encoder, "Difference_Matrix_by_Region_Code", experiment)

if __name__ == "__main__":
    run_experiment()
