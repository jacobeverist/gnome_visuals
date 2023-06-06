from colour import Color
from manim import *

# appending a path
sys.path.append("../../")


class EncoderCollapse(Scene):
    pass

    def construct(self):
        stroke_width = 4
        stroke_color = WHITE

        rect = Rectangle(color=Color(hex=LIGHT_BROWN),
                         stroke_width=stroke_width,
                         stroke_color=stroke_color,
                         fill_opacity=0.8)

        self.add(rect)

        fade_anim = ApplyMethod(rect.set_opacity, 0.0)

        self.play(fade_anim)
