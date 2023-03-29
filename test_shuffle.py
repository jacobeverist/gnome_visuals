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
        #self.w = 3
        self.w = 10
        self.trackers = []
        self.bins = VGroup()

        # array of values from 0 to 1 for each textbox
        self.trackers = [ValueTracker(0) for _ in range(self.num_bins)]
        for i in range(self.num_bins):
            self.trackers[i].set(index=i)
            self.add(self.trackers[i])

        self.rng = np.random.default_rng(0)

    def set_code(self):


        new_code = self.rng.choice([0, ] * (self.num_bins - self.w) + [1, ] * self.w, self.num_bins, replace=False,
                              shuffle=True)
        self.play(*[self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)], run_time=0.5)
        print("set:", new_code)

    def permutate(self):

        # shuffle indices
        shuffled_indices = list(range(self.num_bins))
        np.random.shuffle(shuffled_indices)

        shuffled_bins = [self.bins[i] for i in shuffled_indices]

        # move bins to their new index positions, but preserve index numbers
        for i in range(self.num_bins):
            bin = self.bins[i]
            bin.generate_target()
            bin.target.move_to(shuffled_bins[i].get_center())
        self.play(*[MoveToTarget(bin) for bin in self.bins], run_time=0.5)


    # updater function for textbox
    def __update_array(self):
        """

        :param varray: VGroup of textboxes
        :param dt: float time increment
        :return:
        """

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
        """Attaches the value tracker updater function with the pointer."""

        def updater_func(mob: Mobject) -> None:
            self.__update_array()

        self.__updater_func = updater_func
        self.add_updater(self.__updater_func)



class SquareShuffle(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.num_bins = 32
        #self.w = 3
        self.w = 10
        self.trackers = []
        self.bins = VGroup()

        self.rng = np.random.default_rng(0)

    def __update_array(self):
        """

        :param varray: VGroup of textboxes
        :param dt: float time increment
        :return:
        """

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
        """Attaches the value tracker updater function with the pointer."""

        def updater_func(mob: Mobject) -> None:
            self.__update_array()

        self.__updater_func = updater_func
        self.bins.add_updater(self.__updater_func)

    def __init_array(self) -> None:
        """ gnome code animation mobjects """

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
            self.bins.add(vgroup)

        self.__add_updater()


    def set_code(self):

        new_code = self.rng.choice([0, ] * (self.num_bins - self.w) + [1, ] * self.w, self.num_bins,
                                   replace=False, shuffle=True)

        #self.play(*[self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)], run_time=0.5)
        new_anims = [self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)]

        return new_anims

    def permutate(self):

        # shuffle indices
        shuffled_indices = list(range(self.num_bins))
        np.random.shuffle(shuffled_indices)

        shuffled_bins = [self.bins[i] for i in shuffled_indices]

        # move bins to their new index positions, but preserve index numbers
        for i in range(self.num_bins):
            bin = self.bins[i]
            bin.generate_target()
            bin.target.move_to(shuffled_bins[i].get_center())
        #self.play(*[MoveToTarget(bin) for bin in self.bins], run_time=0.5)
        new_anims = [MoveToTarget(bin) for bin in self.bins]

        return new_anims

    def construct(self):

        # frame configuration
        self.camera.background_color = GREY_C

        # build array animation mobjects
        self.__init_array()

        # add value trackers to scene
        self.add(*self.trackers)

        # add gnome code array to scene
        self.add(self.bins)

        # group bins into array, arranged from left to right, and center it to screen
        num_cols = 8
        self.bins.arrange_in_grid(cols=num_cols, buff=0.1).center()


        for j in range(2):

            # shuffle the array
            self.play(*self.permutate(), run_time=0.5)

            # set encoding
            self.play(*self.set_code(), run_time=0.5)

            # rearrange grid layout
            self.play(self.bins.animate.arrange_in_grid(cols=num_cols-1-j, buff=0.1).center(), run_time=0.5)
            #.to_edge(LEFT).to_edge(UP)

            self.wait(1)


