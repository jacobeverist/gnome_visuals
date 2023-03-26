from manim import *
import numpy as np


class SquareScene(Scene):

    def construct(self):

        # value from 0 to 1 for textbox
        square_tracker = ValueTracker(0)
        self.add(square_tracker)

        # square and text grouped to textbox
        textbox_1 = VDict()
        square_1 = Square(side_length=1.0, stroke_color=WHITE, fill_opacity=1)
        val_text = Text(text="X", color=BLACK, weight=BOLD).move_to(square_1.get_center())
        textbox_1.add({"square": square_1, "val_text": val_text})

        # saved text mobjects for values 0 or 1
        text_0 = Text(text="0", color=BLACK, weight=BOLD)
        text_1 = Text(text="1", color=WHITE, weight=BOLD)

        # updater function for textbox
        def update_textbox(textbox, dt):
            val = square_tracker.get_value()
            square_rgb = [(1.0 - val) for _ in range(3)]
            text_rgb = [val for _ in range(3)]
            square_color = rgb_to_color(square_rgb)
            text_color = rgb_to_color(text_rgb)
            textbox["square"].set_fill(color=square_color, opacity=1)

            # change text value by "becoming" one of two different saved text mobjects
            bin_val = 1 if val >= 0.5 else 0
            if bin_val == 1:
                textbox["val_text"].become(text_1)
            else:
                textbox["val_text"].become(text_0)
            textbox["val_text"].set_fill(color=text_color, opacity=1)

            return textbox

        # add updater
        textbox_1.add_updater(update_textbox)

        # add to scene
        self.add(textbox_1)

        # iterate through different values
        for _ in range(10):
            old_val = int(square_tracker.get_value())
            new_val = 0 if old_val else 1
            self.play(square_tracker.animate.set_value(new_val), run_time=0.25)
