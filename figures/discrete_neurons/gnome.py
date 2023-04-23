# Colors
import colorcet as cc
import matplotlib as mpl  # mpl.colormaps.get_cmap
# import seaborn as sns
from manim import *
from manim.utils.color import Colors

testcc = cc.gray
cmap = mpl.colormaps.get_cmap


class Neuron(Circle):
    CONFIG = {
            "neuron_radius": 0.5,
            "neuron_stroke_color": WHITE,
            "neuron_stroke_width": 3,
            "neuron_fill_color": BLUE,
    }

    def __init__(self, **kwargs):

        # update local CONFIG
        for k, v in {k: v for k, v in kwargs.items() if k in self.CONFIG}.items():
            self.CONFIG[k] = kwargs.pop(k)

        # set CONFIG key-value pairs as member variables of this class instance
        for attr, value in self.CONFIG.items():
            setattr(self, attr, value)

        # send remaining kwargs to superclass
        Circle.__init__(
                self,
                radius=self.neuron_radius,
                stroke_color=self.neuron_stroke_color,
                stroke_width=self.neuron_stroke_width,
                fill_color=self.neuron_fill_color,
                fill_opacity=1,
                **kwargs,
        )


class Cell(Square):
    CONFIG = {
            "cell_side_length": 0.5,
            "cell_stroke_color": BLACK,
            "cell_stroke_opacity": 1,
            "cell_fill_color": WHITE,
            "cell_fill_opacity": 1,
    }

    def __init__(self, **kwargs):

        # update local CONFIG
        for k, v in {k: v for k, v in kwargs.items() if k in self.CONFIG}.items():
            self.CONFIG[k] = kwargs.pop(k)

        # set CONFIG key-value pairs as member variables of this class instance
        for attr, value in self.CONFIG.items():
            setattr(self, attr, value)

        Square.__init__(
                self,
                # **self.CONFIG,
                side_length=self.cell_side_length,
                stroke_color=self.cell_stroke_color,
                stroke_opacity=self.cell_stroke_opacity,
                fill_color=self.cell_fill_color,
                fill_opacity=self.cell_fill_opacity,
                **kwargs,
        )


class GnomeCode(VGroup):
    CONFIG = {
            "cell_side_length": 0.5,
            "cell_stroke_color": BLACK,
            "cell_stroke_opacity": 1,
            "cell_stroke_width": DEFAULT_STROKE_WIDTH,
            "cell_fill_color": WHITE,
            "cell_fill_opacity": 1,
            "cell_text_buff": 0.1
    }

    def __init__(self, shape="square", n=32, **kwargs):

        # update local CONFIG
        for k, v in {k: v for k, v in kwargs.items() if k in self.CONFIG}.items():
            self.CONFIG[k] = kwargs.pop(k)

        # set CONFIG key-value pairs as member variables of this class instance
        for attr, value in self.CONFIG.items():
            setattr(self, attr, value)

        super().__init__(**kwargs)

        if shape in ["square", "dot"]:
            self.shape = shape
        else:
            raise Exception("shape must be 'square' or 'dot'")

        self.num_bins = n
        self.trackers = []
        self.bins = []
        self.rng = np.random.default_rng(0)

        self.show_index = False
        self.show_value = True

        # mpl
        # "cet_CET_L1" (black-white)
        # "cet_CET_CBTD1" (color-blind green/purple)
        # "cet_CET_CBD1" (color-blind)
        # "cet_CET_D4"
        # "cet_CET_D2"
        # "cet_fire"
        # "cet_CET_I1"
        # "cet_CET_CBTL2"
        # "cet_CET_CBTL2_r"

        # seaborn
        # "rocket_r"

        self.colormap = "cet_CET_L1"
        self.cmap = mpl.colormaps.get_cmap(self.colormap)

        self.__init_array()

    def __update_array(self):
        """updater member function called by inline-defined 'updater_func(mob)' in '__add_updater(self)' """

        for b in self.bins:
            cell = b["cell"]
            label = b["label"]

            # value trackers for bit value of element
            val = label.tracker.get_value()

            # change cell background color
            # cell_rgb = [(1.0 - val) for _ in range(3)]
            # cell_color = rgb_to_color(cell_rgb)
            cell_color = mpl.colors.rgb2hex(self.cmap(1.0 - val))

            # change text value and color by "becoming" one of two different saved text mobjects
            # text_rgb = [val for _ in range(3)]
            # text_color = rgb_to_color(text_rgb)
            text_color = mpl.colors.rgb2hex(self.cmap(val))

            # update colors based on value
            cell.set_fill(color=cell_color, opacity=1)
            label.set_color(text_color)  # .move_to(cell.get_center())

            # update text
            if self.show_value:
                label.set_opacity(1)
                label.set_value(label.tracker.get_value())
            elif self.show_index and not self.show_value:
                label.set_opacity(1)
                label.set_value(label.index)
            else:
                label.set_opacity(0)

            self.fit_text()

    def __add_updater(self) -> None:
        """Attaches the value tracker updater function to array animation"""

        def updater_func(mob: Mobject) -> None:
            self.__update_array()

        self.__updater_func = updater_func
        self.add_updater(self.__updater_func)

    def __init_array(self) -> None:
        """ gnome code animation of mobjects """

        cell_color = mpl.colors.rgb2hex(self.cmap(1))
        text_color = mpl.colors.rgb2hex(self.cmap(0))

        # array of values from 0 to 1 for each textbox
        self.trackers = [ValueTracker(0).set(index=k) for k in range(self.num_bins)]

        # cell and text grouped to textbox
        for k in range(0, self.num_bins):

            # cell of a binary array
            if self.shape == "square":
                cell = Square(
                        side_length=self.cell_side_length,
                        stroke_color=self.cell_stroke_color,
                        stroke_opacity=self.cell_stroke_opacity,
                        stroke_width=self.cell_stroke_width,
                        fill_color=cell_color,
                        fill_opacity=self.cell_fill_opacity)

            elif self.shape == "dot":
                cell = Dot(
                        radius=self.cell_side_length / 2,
                        stroke_color=self.cell_stroke_color,
                        stroke_opacity=self.cell_stroke_opacity,
                        stroke_width=self.cell_stroke_width,
                        fill_color=cell_color,
                        fill_opacity=self.cell_fill_opacity)
            else:
                cell = None

            # cell index label
            if self.show_value:
                label = Integer(number=self.trackers[k].get_value(), edge_to_fix=[0, 0, 0])
            elif self.show_index and not self.show_value:
                label = Integer(number=k, edge_to_fix=[0, 0, 0])
            else:
                label = Integer(edge_to_fix=[0, 0, 0]).set_opacity(0)

            # noinspection PyTypeChecker
            label.set_color(text_color)

            # book-keeping attributes to control each cell's state
            label = label.set(index=k, tracker=self.trackers[k])

            # create VGroup to associate this label and cell
            vgroup = VDict(dict(cell=cell, label=label))

            # add to book-keeping list of bins
            self.bins.append(vgroup)
            self.add(vgroup)

        self.fit_text()

        # add updater function to mobjects
        self.__add_updater()

    def fit_text(self):

        # fit all digit labels in their cells and make sure all have same font size
        max_height = -1e100
        max_h_label = None
        max_width = -1e100
        max_w_label = None
        for b in self.bins:
            label = b["label"]
            label_height = label.get_height()
            label_width = label.get_width()

            if label_width > max_width:
                max_width = label_width
                max_w_label = label

            if label_height > max_height:
                max_height = label_height
                max_h_label = label

        if max_height > max_width:
            # set height
            max_h_label.set_height(self.cell_side_length - 2 * self.cell_side_length * self.cell_text_buff)
            scaled_font_size = max_h_label.get_font_size()
        else:
            # set width
            max_w_label.set_width(self.cell_side_length - 2 * self.cell_side_length * self.cell_text_buff)
            scaled_font_size = max_w_label.get_font_size()

        for b in self.bins:
            label = b["label"]
            label.set_font_size(scaled_font_size)
            #label.move_to(b["cell"].get_center())

    def set_value(self, new_code, anim=True):
        if anim:
            return AnimationGroup(*[self.trackers[k].animate.set_value(new_code[k]) for k in range(self.num_bins)])
        else:
            for k in range(self.num_bins):
                self.trackers[k].set_value(new_code[k])
            self.__update_array()
            return self

    def permutate(self):

        # permutate indices
        permutated_indices = list(range(self.num_bins))
        np.random.shuffle(permutated_indices)
        permutated_bins = [self.bins[i].copy() for i in permutated_indices]

        # move bins to their new index positions, but preserve index labels
        for i in range(self.num_bins):
            b = permutated_bins[i]
            b.generate_target()
            b.target.move_to(self.bins[i].get_center())

        self.bins = permutated_bins
        self.submobjects = permutated_bins

        return AnimationGroup(*[MoveToTarget(b) for b in self.submobjects])

    def add_background(self):
        self.add_background_rectangle(opacity=0.25, stroke_opacity=1, stroke_width=3, stroke_color=GREY_B,
                                      buff=2.5 * SMALL_BUFF, color=Colors.gray_a.value,
                                      corner_radius=self.cell_side_length)
