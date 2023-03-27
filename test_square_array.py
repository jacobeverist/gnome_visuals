from manim import *
import numpy as np


class SquareScene(Scene):

    def construct(self):

        num_bins = 5

        # cached text mobjects for values 0 or 1
        text_0 = Text(text="0", color=BLACK, weight=BOLD)
        text_1 = Text(text="1", color=WHITE, weight=BOLD)

        # array of values from 0 to 1 for each textbox
        trackers = [ValueTracker(0) for j in range(num_bins)]
        for tracker in trackers:
            self.add(tracker)

        # updater function for textbox
        #def update_textbox(textbox, dt, tracker_index):
        def update_textbox(textbox, dt):
            """

            :param textbox: VDict of "square" and "val_text"
            :param dt: float time increment
            :param val: float [0,1]
            :return:
            """

            tracker_index = int(textbox["val_text"].text)
            tracker = trackers[tracker_index]
            val = tracker.get_value()

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
            # textbox["val_text"].become(text_1)\
            #    .set_fill(color=rgb_to_color([val for _ in range(3)]), opacity=1)\
            #    if val >= 0.5 else \
            #    textbox["val_text"].become(text_0)\
            #    .set_fill(color=rgb_to_color([val for _ in range(3)]), opacity=1)

            return textbox

        # square and text grouped to textbox
        bins = [VDict() for _ in range(num_bins)]
        for k in range(0, num_bins):
            square = Square(side_length=1.0, stroke_color=WHITE, fill_opacity=1)
            val_text = Text(text=str(k), color=BLACK, weight=BOLD).move_to(square.get_center())
            bins[k].add({"square": square, "val_text": val_text})

        for k in range(1, num_bins):
            bins[k].next_to(bins[k-1], RIGHT)

        # add updater, anonymous part gets proper valuetracker data
        for k in range(0, num_bins):
            bins[k].add_updater(update_textbox)

        # add to scene
        for k in range(0, num_bins):
            self.add(bins[k])

        # iterate through different values
        for j in range(10):
            self.play(*[trackers[k].animate.set_value((j+k) % 2) for k in range(num_bins)], run_time=0.25)
            print("vals:", [trackers[k].get_value() for k in range(num_bins)])














