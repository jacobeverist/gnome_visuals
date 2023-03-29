from manim import *
import numpy as np


# printing boolean arrays neatly
np.set_printoptions(
    precision=3, suppress=True, threshold=1000000, linewidth=400,
    formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})

class GnomeCode(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.num_bins = 32
        self.w = 10
        self.trackers = []
        self.bins = []
        self.rng = np.random.default_rng(0)

        self.__init_array()

    def __update_array(self):
        """updater member function called by inline-defined 'updater_func(mob)' in '__add_updater(self)' """

        for bin in self.bins:
            number = bin[0]
            square = bin[1]

            # value trackers for bit value of element
            val = number.tracker.get_value()

            # change square background color
            square_rgb = [(1.0 - val) for _ in range(3)]
            square_color = rgb_to_color(square_rgb)

            # change text value and color by "becoming" one of two different saved text mobjects
            text_rgb = [val for _ in range(3)]
            text_color = rgb_to_color(text_rgb)

            # update colors
            number.set_color(text_color)
            square.set_fill(color=square_color, opacity=1).set_stroke(color=BLACK, opacity=1)

    def __add_updater(self) -> None:
        """Attaches the value tracker updater function to array animation"""

        def updater_func(mob: Mobject) -> None:
            self.__update_array()

        self.__updater_func = updater_func
        self.add_updater(self.__updater_func)

    def __init_array(self) -> None:
        """ gnome code animation of mobjects """

        # array of values from 0 to 1 for each textbox
        self.trackers = [ValueTracker(0).set(index=_) for _ in range(self.num_bins)]

        # square and text grouped to textbox
        for k in range(0, self.num_bins):
            square = Square(side_length=1.0, stroke_color=BLACK, fill_color=WHITE, fill_opacity=1)
            num = Integer(number=k, color=BLACK, font_size=DEFAULT_FONT_SIZE, fill_opacity=1)\
                .set(index=k, z_index=1, tracker=self.trackers[k]).scale(1.5)

            # create VGroup to associate this number and square
            vgroup = VGroup(num, square)

            # add to book-keeping list of bins
            self.bins.append(vgroup)
            self.add(vgroup)

        # add updater function to mobjects
        self.__add_updater()

    def set_code(self):
        # activate w random bits
        new_code = self.rng.choice([0, ] * (self.num_bins - self.w) + [1, ] * self.w, self.num_bins, replace=False, shuffle=True)
        return [self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)]

    def permutate(self):

        # permutate indices
        permutated_indices = list(range(self.num_bins))
        np.random.shuffle(permutated_indices)
        permutated_bins = [self.bins[i] for i in permutated_indices]

        # move bins to their new index positions, but preserve index numbers
        for i in range(self.num_bins):
            bin = self.bins[i]
            bin.generate_target()
            bin.target.move_to(permutated_bins[i].get_center())

        return [MoveToTarget(bin) for bin in self.bins]


class GnomeShuffle(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):

        # frame configuration
        self.camera.background_color = GREY_C

        # initialize gnome code array animation mobject and add to scene
        code = GnomeCode()
        self.add(code)

        # group bins into array, arranged from left to right, and center it to screen
        num_cols = 8
        code.arrange_in_grid(cols=num_cols, buff=0.1).center()

        for j in range(2):

            # permutate the array
            self.play(*code.permutate(), run_time=0.5)

            # set encoding
            self.play(*code.set_code(), run_time=0.5)

            # rearrange grid layout
            self.play(code.animate.arrange_in_grid(cols=num_cols-1-j, buff=0.1).center(), run_time=0.5)

            self.wait(1)

