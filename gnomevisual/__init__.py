"""
Gnome Visual - Visualization toolkit for Gnome Codes.

This package provides visualization tools for Gnome Code encoders across
multiple technologies: Matplotlib, Manim, and Plotly/Dash.
"""

# Import core utilities
import gnomevisual.utils as utils
from .utils import *

# Import technology-specific modules
import gnomevisual.matplotlib as matplotlib
import gnomevisual.manim as manim
import gnomevisual.plotly as plotly

# For backwards compatibility, also import matplotlib components at top level
from .matplotlib import *

__version__ = "0.1.0"

__all__ = [
    # Submodules
    "utils",
    "matplotlib",
    "manim",
    "plotly",
    # Utils
    *utils.__all__,
    # Matplotlib components (backwards compatibility)
    *matplotlib.__all__,
]
