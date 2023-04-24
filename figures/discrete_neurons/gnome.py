# Colors
import colorcet as cc
import matplotlib as mpl  # mpl.colormaps.get_cmap
import seaborn as sns
from manim import *
from manim.utils.color import Colors

testcc = cc.gray
cmap = mpl.colormaps.get_cmap


class Synapse(VGroup):
    CONFIG = {
            "edge_color": WHITE,
            "edge_stroke_width": 4,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)
    colors = sns.color_palette("colorblind").as_hex()

    def __init__(self, neuron, mob, ori="vert", do_cross=True, cross_color=RED, **kwargs):

        # update local CONFIG
        for k, v in {k: v for k, v in kwargs.items() if k in self.CONFIG}.items():
            self.CONFIG[k] = kwargs.pop(k)

        # set CONFIG key-value pairs as member variables of this class instance
        for attr, value in self.CONFIG.items():
            setattr(self, attr, value)

        super().__init__(**kwargs)

        # get point on neuron boundary in the direction of mob we connect to
        diff_vec = mob.get_center() - neuron.get_center()
        normvec = diff_vec / np.linalg.norm(diff_vec)
        try:
            end_point = neuron.radius * normvec + neuron.get_center()
        except:
            # neuron is not a circle, so perhaps it is a square
            # find closest boundary edge of mob to connect to
            min_dist = 1e100
            min_pnt = None
            if ori == "vert":
                cand_points = [neuron.get_edge_center(direction) for direction in [UP, DOWN]]
            elif ori == "hori":
                cand_points = [neuron.get_edge_center(direction) for direction in [LEFT, RIGHT]]
            else:
                cand_points = [neuron.get_edge_center(direction) for direction in [UP, DOWN, LEFT, RIGHT]]

            for pnt in cand_points:
                diff_vec = pnt - mob.get_center()
                dist = np.linalg.norm(diff_vec)
                if dist < min_dist:
                    min_dist = dist
                    min_pnt = pnt
            end_point = min_pnt


        # find closest boundary edge of mob to connect to
        min_dist = 1e100
        min_pnt = None
        if ori == "vert":
            cand_points = [mob.get_edge_center(direction) for direction in [UP, DOWN]]
        elif ori == "hori":
            cand_points = [mob.get_edge_center(direction) for direction in [LEFT, RIGHT]]
        else:
            cand_points = [mob.get_edge_center(direction) for direction in [UP, DOWN, LEFT, RIGHT]]

        for pnt in cand_points:
            diff_vec = pnt - end_point
            dist = np.linalg.norm(diff_vec)
            if dist < min_dist:
                min_dist = dist
                min_pnt = pnt
        start_point = min_pnt


        edge_color = mpl.colors.rgb2hex(mpl.colormaps.get_cmap("cet_blues")(0.25))
        #edge_color = mpl.colors.rgb2hex(sns.color_palette("tab10")[9])


        # tip_length = 1,
        self.line = Line(
                start_point,
                end_point,
                # max_tip_length_to_length_ratio=0.08,
                # max_stroke_width_to_length_ratio=2,
                buff=0,
                #stroke_color=self.CONFIG["edge_color"],
                stroke_color=edge_color,
                # stroke_width=self.CONFIG["edge_stroke_width"],
                stroke_opacity=1,
        )

        self.add(self.line)

        if do_cross:
            # noinspection PyTypeChecker
            self.cross = Cross(stroke_width=self.CONFIG["edge_stroke_width"],
                               stroke_color=cross_color)
            #self.cross = Cross(stroke_width=self.CONFIG["edge_stroke_width"],
            #                   stroke_color=self.colors[8])
            #self.cross = Cross(stroke_width=self.CONFIG["edge_stroke_width"],
            #                   stroke_color=self.colors[8])
            self.cross.move_to(self.line.get_center()).set_height(0.15).rotate(self.line.get_angle())

            self.add(self.cross)


class NaiveNeuron(Circle):
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


class NeuronWithOperations(VGroup):
    CONFIG = {
            "neuron_radius": 1.0,
            "neuron_stroke_color": WHITE,
            "neuron_stroke_width": 3,
            "neuron_fill_color": GRAY_C,
    }

    def __init__(self, **kwargs):

        # update local CONFIG
        for k, v in {k: v for k, v in kwargs.items() if k in self.CONFIG}.items():
            self.CONFIG[k] = kwargs.pop(k)

        # set CONFIG key-value pairs as member variables of this class instance
        for attr, value in self.CONFIG.items():
            setattr(self, attr, value)
        self.radius = self.neuron_radius

        super().__init__(**kwargs)

        # create circle
        self.circle = Circle(
                radius=self.neuron_radius,
                stroke_color=self.neuron_stroke_color,
                stroke_width=self.neuron_stroke_width,
                fill_color=self.neuron_fill_color,
                fill_opacity=1,
                **kwargs,
        )

        self.add(self.circle)

        # box_factor = box_len / self.neuron_radius
        # box_factor = 0.72
        box_factor = 0.74

        buff = 0.05
        # box_len = self.neuron_radius/2.0
        # box_len = 0.36
        box_len = box_factor * self.neuron_radius

        box_color = "#3b7cb2"

        # counter operation
        self.counter = Rectangle(fill_color=box_color,
                                 fill_opacity=1,
                                 stroke_color=BLACK,
                                 height=box_len,
                                 width=box_len * 1.2)
        self.counter.shift(DOWN * (self.neuron_radius / 2.0 - buff / 2.0 - 1.5 * buff))

        # activation operation
        self.activation = Rectangle(fill_color=box_color,
                                    fill_opacity=1,
                                    stroke_color=BLACK,
                                    height=box_len,
                                    width=box_len * 1.2)
        self.activation.next_to(self.counter, UP, buff=buff)


        # scale of unit step function
        scale = 0.4
        width_scale = 0.7

        # individual lines to create unit step function (3 lines)
        # line1 = Line(ORIGIN, RIGHT * scale, buff=0, color=BLACK, stroke_width=1.5 * DEFAULT_STROKE_WIDTH)

        # line2 = Line(line1.get_end(), line1.get_end() + 1.2 * UP * scale, buff=0, color=BLACK,
        #             stroke_width=1.5 * DEFAULT_STROKE_WIDTH)

        # line3 = Line(line2.get_end(), line2.get_end() + RIGHT * scale, buff=0, color=BLACK,
        #             stroke_width=1.5 * DEFAULT_STROKE_WIDTH)

        # Raw VMObject to draw unit step function
        vertices = [ORIGIN, RIGHT * scale * width_scale, RIGHT * scale * width_scale + 1.2 * UP * scale,
                    2 * RIGHT * scale * width_scale + 1.2 * UP * scale]
        poly_path = VMobject(color=BLACK, stroke_width=1.8 * DEFAULT_STROKE_WIDTH)
        first_vertex, *vertices = vertices
        first_vertex = np.array(first_vertex)
        poly_path.start_new_path(first_vertex)
        poly_path.add_points_as_corners(np.array([np.array(vertex) for vertex in vertices]))

        # self.activation_label = VDict(dict(line1=line1, line2=line2, line3=line3))
        self.activation_label = VDict(dict(step_func=poly_path))
        self.activation_label.move_to(self.activation.get_center())

        # counter as sigma summation symbol
        self.counter_label = MathTex("\sum", color=BLACK, stroke_width=0.8 * DEFAULT_STROKE_WIDTH).move_to(
            self.counter.get_center()).scale(0.8)

        # noinspection PyTypeChecker
        # label1.set_color(text_color)

        self.operations = VDict(dict(counter=self.counter,
                                     activation=self.activation,
                                     counter_label=self.counter_label,
                                     activation_label=self.activation_label))

        self.add(self.operations)


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
            "cell_text_buff": 0.2
    }

    def __init__(self, shape="square", n=32, **kwargs):

        print(self.CONFIG)

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

        #self.colormap = "cet_CET_L1"
        self.colormap = "cet_blues"
        #self.colormap = "cet_blues"
        self.cmap = mpl.colormaps.get_cmap(self.colormap)
        #self.cmap = sns.color_palette("coolwarm", as_cmap=True)

        print("blues:", self.cmap(0.0), self.cmap(1.0))
        print("blues:", self.cmap(0), self.cmap(255))
        print(self.cmap.N)
        cell_color = mpl.colors.rgb2hex(self.cmap(1.0))
        print(cell_color)
        # (0.94334, 0.94353, 0.94348, 1.0)
        #
        # "#3b7cb2"

        #mpl.colors.LinearSegmentedColormap

        #mpl.colormaps.LinearSegmentedColormap

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
            cell_color = mpl.colors.rgb2hex(self.cmap(val))

            # change text value and color by "becoming" one of two different saved text mobjects
            # text_rgb = [val for _ in range(3)]
            # text_color = rgb_to_color(text_rgb)
            text_color = mpl.colors.rgb2hex(self.cmap(1.0-val))
            text_color = BLACK

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

        cell_color = mpl.colors.rgb2hex(self.cmap(1.0))
        #text_color = mpl.colors.rgb2hex(self.cmap(0.0))
        text_color = BLACK

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
                label = Integer(number=0, edge_to_fix=[0, 0, 0])
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
            # label.move_to(b["cell"].get_center())

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
        self.add_background_rectangle(opacity=1,
                                      color=Colors.gray_c.value,
                                      stroke_opacity=1,
                                      stroke_width=3,
                                      stroke_color=Colors.white.value,
                                      #buff=2.5 * SMALL_BUFF, color=Colors.gray_a.value,
                                      buff=2.5 * SMALL_BUFF,
                                      corner_radius=self.cell_side_length)
