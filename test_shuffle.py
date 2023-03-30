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
        self.w = 8
        self.trackers = []
        self.bins = []
        self.rng = np.random.default_rng(0)

        self.__init_array()

    def __update_array(self):
        """updater member function called by inline-defined 'updater_func(mob)' in '__add_updater(self)' """

        for bin in self.bins:
            cell = bin["cell"]
            label = bin["label"]

            # value trackers for bit value of element
            val = label.tracker.get_value()

            # change cell background color
            cell_rgb = [(1.0 - val) for _ in range(3)]
            cell_color = rgb_to_color(cell_rgb)

            # change text value and color by "becoming" one of two different saved text mobjects
            text_rgb = [val for _ in range(3)]
            text_color = rgb_to_color(text_rgb)

            # update colors based on value
            label.set_color(text_color)
            cell.set_fill(color=cell_color, opacity=1)

    def __add_updater(self) -> None:
        """Attaches the value tracker updater function to array animation"""

        def updater_func(mob: Mobject) -> None:
            self.__update_array()

        self.__updater_func = updater_func
        self.add_updater(self.__updater_func)

    def __init_array(self) -> None:
        """ gnome code animation of mobjects """

        # array of values from 0 to 1 for each textbox
        self.trackers = [ValueTracker(0).set(index=k) for k in range(self.num_bins)]

        # cell and text grouped to textbox
        for k in range(0, self.num_bins):

            # cell of a binary array
            cell = Square(side_length=1.0, stroke_color=BLACK, stroke_opacity=1, fill_color=WHITE, fill_opacity=1)#.set(z_index=2)

            # cell index label
            label = Integer(number=k, font_size=DEFAULT_FONT_SIZE).set_color(BLACK).scale(1.5)

            # book-keeping attributes to control each cell's state
            label = label.set(index=k, tracker=self.trackers[k])

            # create VGroup to associate this label and cell
            #vgroup = VGroup(cell, label)
            vgroup = VDict(dict(cell=cell, label=label))

            # add to book-keeping list of bins
            self.bins.append(vgroup)
            self.add(vgroup)

        # add updater function to mobjects
        self.__add_updater()


    def set_value(self, new_code):
        anims = AnimationGroup(*[self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)])
        return anims

    def permutate(self):

        # permutate indices
        permutated_indices = list(range(self.num_bins))
        np.random.shuffle(permutated_indices)
        permutated_bins = [self.bins[i] for i in permutated_indices]

        ## move bins to their new index positions, but preserve index labels
        for i in range(self.num_bins):
            bin = permutated_bins[i]
            bin.generate_target()
            bin.target.move_to(self.bins[i].get_center())

        self.bins = permutated_bins
        self.submobjects = permutated_bins

        anims = AnimationGroup(*[MoveToTarget(bin) for bin in self.bins])
        return anims


class GnomeShuffle(Scene):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):

        self.rng = np.random.default_rng(0)

        # frame configuration
        self.camera.background_color = GREY_C

        # initialize gnome code array animation mobject and add to scene
        code = GnomeCode()
        self.add(code)

        # group bins into array, arranged from left to right, and center it to screen
        num_cols = 6
        code.arrange_in_grid(cols=num_cols, buff=0.1).center()

        self.wait(0.5)

        for j in range(2):

            # generate new code with w random activated bits
            sparse_elements = [0, ] * (code.num_bins - code.w) + [1, ] * code.w
            new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)

            # set encoding
            self.play(code.set_value(new_code), run_time=0.5)
            self.wait(0.5)

            # permutate the array
            self.play(code.permutate(), run_time=1)
            self.wait(0.5)

            # rearrange grid layout
            self.play(code.animate.arrange_in_grid(cols=num_cols - 1 - j, buff=0.1).center(), run_time=1)
            self.wait(0.5)

