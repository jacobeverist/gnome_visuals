from manim import *
import numpy as np

# printing boolean arrays neatly
np.set_printoptions(
    precision=3, suppress=True, threshold=1000000, linewidth=400,
    formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


class SquareShuffle(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.num_bins = 32
        #self.w = 3
        self.w = 10

    def construct(self):


        self.camera.background_color = GREY_C

        # array of values from 0 to 1 for each textbox
        trackers = [ValueTracker(0) for _ in range(self.num_bins)]
        for i in range(self.num_bins):
            trackers[i].set(index=i)
            self.add(trackers[i])

        # updater function for textbox
        def update_textbox(textbox, dt):
            """

            :param textbox: VGroup of "square" and "number"
            :param dt: float time increment
            :param val: float [0,1]
            :return:
            """


            number = textbox[0]
            square = textbox[1]

            # value trackers for bit value of element
            tracker_index = number.index
            tracker = trackers[tracker_index]
            val = tracker.get_value()

            # change square background color
            square_rgb = [(1.0 - val) for _ in range(3)]
            square_color = rgb_to_color(square_rgb)

            # change text value and color by "becoming" one of two different saved text mobjects
            text_rgb = [val for _ in range(3)]
            text_color = rgb_to_color(text_rgb)

            # update colors
            number.set_color(text_color)
            square.set_fill(color=square_color, opacity=1).set_stroke(color=BLACK, opacity=1)

            return textbox

        # square and text grouped to textbox
        bins = []
        for k in range(0, self.num_bins):
            square = Square(side_length=1.0, stroke_color=BLACK, fill_color=WHITE, fill_opacity=1)
            num = Integer(number=k, color=BLACK, font_size=DEFAULT_FONT_SIZE, fill_opacity=1).set(index=k, z_index=1).scale(1.5)

            # create VGroup to associate this number and square
            vgroup = VGroup(num, square)

            # add updater
            vgroup.add_updater(update_textbox)

            # add to book-keeping list of bins
            bins.append(vgroup)


        # group bins into array, arranged from left to right, and center it to screen
        array_group = VGroup(*bins)
        array_group.arrange_in_grid(cols=8, buff=0.1).center()

        # add to scene
        self.add(array_group)

        rng = np.random.default_rng(0)

        new_code = rng.choice([0, ] * (self.num_bins - self.w) + [1, ] * self.w, self.num_bins, replace=False,
                              shuffle=True)
        self.play(*[trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)], run_time=0.5)
        print("set:", new_code)


        # iterate through different values
        for j in range(10):
            #new_code = rng.choice([0, ] * (self.num_bins - self.w) + [1, ] * self.w, self.num_bins, replace=False, shuffle=True)
            #self.play(*[trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)], run_time=0.5)
            #print("set:", new_code)

            # shuffle indices
            shuffled_indices = list(range(self.num_bins))
            np.random.shuffle(shuffled_indices)
            shuffled_bins = [bins[i] for i in shuffled_indices]

            # move bins to their new index positions, but preserve index numbers
            for i in range(self.num_bins):
                bin = bins[i]
                bin.generate_target()
                bin.target.move_to(shuffled_bins[i].get_center())
            self.play(*[MoveToTarget(bin) for bin in bins], run_time=0.5)





