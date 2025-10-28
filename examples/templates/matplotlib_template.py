"""
Template for creating matplotlib visualizations with gnomevisual.

Usage:
    python gallery/templates/matplotlib_template.py
"""
import matplotlib.pyplot as plt
import numpy as np

from gnomecode.encoders import PeriodicScalarEncoder
from gnomevisual.matplotlib import (
    draw_multi_encoder_bins,
    draw_similarity_heatmap,
    save_fig,
)


def main():
    """Create example matplotlib visualizations."""
    # Create an encoder
    encoder = PeriodicScalarEncoder(n=32, w=8, period=1.0, xmin=0.0, xmax=1.0)

    # Create a figure with subplots
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Draw encoder bins
    draw_multi_encoder_bins(axes[0], encoder)
    axes[0].set_title("Encoder Bins Visualization")

    # Draw similarity heatmap
    draw_similarity_heatmap(axes[1], encoder, num_samples=50)
    axes[1].set_title("Similarity Heatmap")

    plt.tight_layout()

    # Save or show
    # save_fig("outputs/figures/", encoder, "example_plot")
    plt.show()


if __name__ == "__main__":
    main()
