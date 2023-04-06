import numpy as np
from gnomecode import *


# TODO:
"""
## TODO list
# 1) + add base class boundary-handling options (exception, clamp, modulo, silent)
# 2) + able to plot fundamental regions of periodic cells
# 3) + plot fundamental bin and congruent bins (with lower alpha)
# 4) + create better grid distribution options, multi-scale, etc
# 5) center fund. region for each bin
# 6) illustrative plots for each step of discussion (Properties of Discrete Encodings of Binary Population)
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
    experiment = "PeriodicCellEncoder"

    # Initalize Encoder
    multi_encoder = MultiEncoder()

    for i in range(10, 11):
        # Change Encoder
        multi_encoder.add_encoder(PeriodicCellEncoder(n=i, oob_method="modulo", seed=i))

        # Plot Feature
        plot_interval_multi_encoder(multi_encoder, desc_str=experiment)
        save_fig(file_dir, multi_encoder, "Features", experiment)

        # Plot Similarity Matrix by Code
        plot_code_heatmap(multi_encoder, desc_str=experiment)
        save_fig(file_dir, multi_encoder, "Similarity_Matrix_by_Region_Code", experiment)

        # Plot Similarity Matrix by Real Space
        plot_realspace_heatmap(multi_encoder, desc_str=experiment)
        save_fig(file_dir, multi_encoder, "Similarity_Matrix_Projected_to_Real_Space", experiment)


if __name__ == "__main__":
    run_experiment()
