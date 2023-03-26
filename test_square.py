from manim import *
import numpy as np


class SquareScene(Scene):

    def construct(self):

        # saved text mobjects for values 0 or 1
        text_0 = Text(text="0", color=BLACK, weight=BOLD)
        text_1 = Text(text="1", color=WHITE, weight=BOLD)

        # updater function for textbox
        def update_textbox(textbox, dt, val):

            # float value from 0 to 1
            #val = square_tracker.get_value()

            # change square background color
            square_rgb = [(1.0 - val) for _ in range(3)]
            square_color = rgb_to_color(square_rgb)
            textbox["square"].set_fill(color=square_color, opacity=1)

            # change text value and color by "becoming" one of two different saved text mobjects
            text_rgb = [val for _ in range(3)]
            text_color = rgb_to_color(text_rgb)
            if val >= 0.5:
                textbox["val_text"].become(text_1, match_center=True).set_fill(color=text_color, opacity=1)
            else:
                textbox["val_text"].become(text_0, match_center=True).set_fill(color=text_color, opacity=1)

            # single-line equivalent of above
            #textbox["val_text"].become(text_1)\
            #    .set_fill(color=rgb_to_color([val for _ in range(3)]), opacity=1)\
            #    if val >= 0.5 else \
            #    textbox["val_text"].become(text_0)\
            #    .set_fill(color=rgb_to_color([val for _ in range(3)]), opacity=1)

            return textbox

        # value from 0 to 1 for textbox
        square_tracker = ValueTracker(0)
        self.add(square_tracker)

        square_tracker2 = ValueTracker(1)
        self.add(square_tracker2)

        # square and text grouped to textbox
        textbox_1 = VDict()
        square_1 = Square(side_length=1.0, stroke_color=WHITE, fill_opacity=1)
        val_text_1 = Text(text="X", color=BLACK, weight=BOLD).move_to(square_1.get_center())
        textbox_1.add({"square": square_1, "val_text": val_text_1})

        textbox_2 = VDict()
        square_2 = Square(side_length=1.0, stroke_color=WHITE, fill_opacity=1)
        val_text_2 = Text(text="X", color=BLACK, weight=BOLD).move_to(square_2.get_center())
        textbox_2.add({"square": square_2, "val_text": val_text_2})
        textbox_2.next_to(textbox_1, RIGHT)


        # add updater, anonymous part gets proper valuetracker data
        textbox_1.add_updater(lambda x, dt: update_textbox(x, dt, square_tracker.get_value()))
        textbox_2.add_updater(lambda x, dt: update_textbox(x, dt, square_tracker2.get_value()))
        #textbox_1.add_updater(update_textbox)

        # add to scene
        self.add(textbox_1)
        self.add(textbox_2)

        # iterate through different values
        for _ in range(10):
            old_val = int(square_tracker.get_value())
            new_val = 0 if old_val else 1
            self.play(square_tracker.animate.set_value(new_val), square_tracker2.animate.set_value(old_val), run_time=1)
