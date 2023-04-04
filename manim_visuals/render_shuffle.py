from manim import *
import numpy as np
from copy import deepcopy

# printing boolean arrays neatly
np.set_printoptions(
    precision=3, suppress=True, threshold=1000000, linewidth=400,
    formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


class Count(Animation):
    def __init__(self, number: DecimalNumber, start: float, end: float, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(number, **kwargs)
        # Set start and end
        self.start = start
        self.end = end

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        value = self.start + (alpha * (self.end - self.start))
        self.mobject.set_value(value)


class GnomeCode(VGroup):
    def __init__(self, shape="square", n=32, w=8, **kwargs):
        super().__init__(**kwargs)

        if shape in ["square", "circle"]:
            self.shape = shape
        else:
            raise Exception("shape must be 'square' or 'circle'")

        self.num_bins = n
        self.w = w
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
            cell.set_fill(color=cell_color, opacity=1)
            label.set_color(text_color)  # .move_to(cell.get_center())

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

            # size = self.rng.uniform(0.8, 1.2)
            size = 1

            # cell of a binary array
            # if k % 2 == 0:
            if self.shape == "square":
                cell = Square(side_length=1, stroke_color=BLACK, stroke_opacity=1, fill_color=WHITE,
                              fill_opacity=1).scale(size)
            elif self.shape == "circle":
                cell = Dot(radius=0.5, stroke_color=BLACK, stroke_opacity=1, stroke_width=DEFAULT_STROKE_WIDTH,
                           fill_color=WHITE, fill_opacity=1).scale(size)
            else:
                cell = None

            # cell index label
            label = Integer(number=k, font_size=DEFAULT_FONT_SIZE).set_color(BLACK).scale(1.5)

            # book-keeping attributes to control each cell's state
            label = label.set(index=k, tracker=self.trackers[k])

            # create VGroup to associate this label and cell
            vgroup = VDict(dict(cell=cell, label=label))

            # add to book-keeping list of bins
            self.bins.append(vgroup)
            self.add(vgroup)

        # add updater function to mobjects
        self.__add_updater()

    def set_value(self, new_code):
        return AnimationGroup(*[self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)])

    def permutate(self):

        # permutate indices
        permutated_indices = list(range(self.num_bins))
        np.random.shuffle(permutated_indices)
        permutated_bins = [self.bins[i].copy() for i in permutated_indices]

        # matching submobjects transformation
        """
        self.generate_target()
        for i in range(self.num_bins):
            self.target.bins[i] = permutated_bins[i]
            self.target.submobjects[i] = permutated_bins[i]
        transform_anim = TransformMatchingShapes(self, self.target, path_arc=PI/2)

        for i in range(self.num_bins):
            target_mobject = self.target.bins[i]
            target_family = target_mobject.family_members_with_points()
            target_sm = transform_anim.get_shape_map(target_mobject)

            target_bin = self.target.bins[i]['cell']
            target_bin.save_state()
            target_bin.center()
            target_bin.set_height(1)
            target_result = hash(np.round(target_bin.points, 3).tobytes())
            #target_result = deepcopy(target_bin.points)
            target_bin.restore()

            source_mobject = self.bins[i]
            source_family = source_mobject.family_members_with_points()
            source_sm = transform_anim.get_shape_map(source_mobject)

            source_bin = self.bins[i]['cell']
            source_bin.save_state()
            source_bin.center()
            source_bin.set_height(1)
            source_result = hash(np.round(source_bin.points, 3).tobytes())
            #source_result = deepcopy(source_bin.points)
            source_bin.restore()


            print(i, source_sm, permutated_indices[i], target_sm)
            #print(i, source_family, permutated_indices[i], target_family)

            #print(i, source_result == target_result, source_result, target_result)
            #print(i, source_result, target_result)
            #print(i, source_bin, target_bin)

        # return TransformMatchingShapes(self, self.target, path_arc=PI/2)
        """

        ## move bins to their new index positions, but preserve index labels
        for i in range(self.num_bins):
            bin = permutated_bins[i]
            bin.generate_target()
            bin.target.move_to(self.bins[i].get_center())

        self.bins = permutated_bins
        self.submobjects = permutated_bins

        return AnimationGroup(*[MoveToTarget(bin) for bin in self.submobjects])


class GnomeShuffle(Scene):

    #def __init__(self, **kwargs):
    #    super().__init__(**kwargs)

    def construct(self):

        #print(self.renderer)
        #return

        self.rng = np.random.default_rng(0)

        # frame configuration
        self.camera.background_color = GREY_C

        # Create Decimal Number and add it to scene
        number = DecimalNumber().set_color(BLACK).to_corner()
        # Add an updater to keep the DecimalNumber centered as its value changes
        number.add_updater(lambda number: number.to_corner())

        # initialize gnome code array animation mobject and add to scene
        code = GnomeCode()
        self.add(code)


        # group bins into array, arranged from left to right, and center it to screen
        num_cols = 6
        code.arrange_in_grid(cols=num_cols, buff=0.1).center()

        #code2 = GnomeCode()
        #code2.arrange_in_grid(cols=num_cols+2, buff=0.1).center()

        self.wait(0.5)

        #self.play(TransformMatchingShapes(code, code2, path_arc=PI/2))

        # self.play(Count(number, 0, 100), run_time=4, rate_func=linear)

        for j in range(2):
            # generate new code with w random activated bits
            sparse_elements = [0, ] * (code.num_bins - code.w) + [1, ] * code.w
            new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)

            print("set code:", new_code)

            # set encoding
            self.play(code.set_value(new_code), run_time=0.4)
            self.wait(0.5)

            # permutate the array
            self.play(code.permutate(), run_time=1)
            self.wait(0.5)

            # rearrange grid layout
            self.play(code.animate.arrange_in_grid(cols=num_cols - 1 - j, buff=0.1).center(), run_time=1)
            self.wait(0.5)
