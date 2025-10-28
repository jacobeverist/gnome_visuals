"""
Template for creating Manim animations with gnomevisual.

Usage:
    manim gallery/templates/manim_template.py MyScene
"""
from manim import *
import numpy as np

from gnomevisual.manim import GnomeCode, Synapse, Cell
from gnomecode.encoders import PeriodicScalarEncoder


class MyScene(Scene):
    """Example scene demonstrating basic Gnome Code visualization."""

    def construct(self):
        # Create an encoder
        encoder = PeriodicScalarEncoder(n=32, w=8, period=1.0)

        # Create a visual GnomeCode object
        gnome = GnomeCode(n=32, w=8, shape="square")

        # Add to scene
        self.play(Create(gnome))
        self.wait(1)

        # Example: Encode a value and show it
        # value = 0.5
        # encoding = encoder.encode(value)
        # ... animate the encoding ...

        self.wait(2)
