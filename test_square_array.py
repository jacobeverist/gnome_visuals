from manim import *
import numpy as np

# printing boolean arrays neatly
np.set_printoptions(
    precision=3, suppress=True, threshold=1000000, linewidth=400,
    formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


class SquareScene(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # cached text mobjects for values 0 or 1
        self.text_0 = Text(text="0", color=BLACK, weight=BOLD)
        self.text_1 = Text(text="1", color=WHITE, weight=BOLD)

        self.square_0 = Square(side_length=1.0, stroke_color=WHITE, fill_opacity=1)
        self.square_1 = Square(side_length=1.0, stroke_color=BLACK, fill_opacity=1)

    def construct(self):

        num_bins = 5
        w = 3

        self.camera.background_color = GREY_C

        # array of values from 0 to 1 for each textbox
        trackers = [ValueTracker(0) for j in range(num_bins)]
        for i in range(num_bins):
            trackers[i].set(index=i)
            self.add(trackers[i])

        # updater function for textbox
        def update_textbox(textbox, dt):
            """

            :param textbox: VDict of "square" and "val_text"
            :param dt: float time increment
            :param val: float [0,1]
            :return:
            """

            tracker_index = int(textbox["val_text"].index)
            tracker = trackers[tracker_index]
            val = tracker.get_value()

            # change square background color
            square_rgb = [(1.0 - val) for _ in range(3)]
            square_color = rgb_to_color(square_rgb)

            # change text value and color by "becoming" one of two different saved text mobjects
            text_rgb = [val for _ in range(3)]
            text_color = rgb_to_color(text_rgb)

            textbox["square"].set_fill(color=square_color, opacity=1).set_stroke(color=BLACK, opacity=1)
            textbox["val_text"].set_fill(color=text_color, opacity=1)

            if val >= 0.5:
                textbox["val_text"].become(self.text_1, match_center=True)
            else:
                textbox["val_text"].become(self.text_0, match_center=True)

            # single-line equivalent of above
            # textbox["val_text"].become(self.text_1)\
            #    .set_fill(color=rgb_to_color([val for _ in range(3)]), opacity=1)\
            #    if val >= 0.5 else \
            #    textbox["val_text"].become(self.text_0)\
            #    .set_fill(color=rgb_to_color([val for _ in range(3)]), opacity=1)

            return textbox

        # square and text grouped to textbox
        bins = [VDict() for _ in range(num_bins)]
        for k in range(0, num_bins):
            square = Square(side_length=1.0, stroke_color=BLACK, fill_color=WHITE, fill_opacity=1)
            val_text = Text(text=str(k), color=BLACK, weight=BOLD).set(index=k).move_to(square.get_center()).scale(1.5)
            bins[k].add({"square": square, "val_text": val_text})

        # group bins into array, arranged from left to right, and center it to screen
        array_group = VGroup(*bins).arrange(RIGHT, buff=0.1).move_to([0.,0.,0.])

        # add updater, anonymous part gets proper valuetracker data
        for k in range(0, num_bins):
            bins[k].add_updater(update_textbox)

        # add to scene
        self.add(array_group)

        # iterate through different values
        for j in range(10):
            rng = np.random.default_rng(j)
            new_code = rng.choice([0, ] * (num_bins - w) + [1, ] * w, num_bins, replace=False, shuffle=True)

            # new_code = np.array([int((j+k) % 2) for k in range(num_bins)], dtype=int)
            print("set:", new_code)

            # self.play(*[trackers[k].animate.set_value(new_code[k]) for k in range(num_bins)], run_time=0.5)
            # self.play(*[trackers[k].animate.set_value(new_code[k]) for k in range(num_bins)], run_time=0.5)
            self.play(*[trackers[k].animate.set_value(new_code[k]) for k in range(num_bins)], run_time=0.5)

            #self.play(array_group.animate.shuffle(recursive=True), run_time=2)
            #self.play(array_group.animate.shuffle(recursive=True), run_time=2)

