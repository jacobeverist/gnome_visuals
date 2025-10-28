"""Manim animation components for Gnome Codes."""

from .gnome import (
    Synapse,
    NaiveNeuron,
    NeuronWithOperations,
    NeuronWithWindow,
    Cell,
    GnomeCode,
)

from .arrange_bins import (
    ClippedBin,
)

__all__ = [
    "Synapse",
    "NaiveNeuron",
    "NeuronWithOperations",
    "NeuronWithWindow",
    "Cell",
    "GnomeCode",
    "ClippedBin",
]
