
# appending a path
import sys
sys.path.append("../../")

# Math Animation
# Colors
import colorcet as cc
import holoviews as hv
import matplotlib as mpl  # mpl.colormaps.get_cmap


# seaborn perceptually uniform color maps:
# "rocket", "mako", "flare", "crest", "magma", "viridis"
import seaborn as sns

from manim import *
# from manim.utils.color import Colors
from manim.utils.color import manim_colors

holoview_extension = hv.extension
testgray = cc.gray
cmap = mpl.colormaps.get_cmap

# Parts
from gnome import GnomeCode, NaiveNeuron, Cell, Synapse, NeuronWithOperations, NeuronWithWindow

# printing boolean arrays neatly
np.set_printoptions(
        precision=3, suppress=True, threshold=1000000, linewidth=400,
        formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


# 1) singleton input:  input array, synapses gated with valves, accumulator circle with sigma sum (input stage)
# 2) singleton output:  circle with sigma sum, WTA-rod, activation line, bit box
# 3) ensemble:  input array, gated synapses, dendriditic sum array, accumulator layer, sum line, WTA-layer, activations line, output layer
# 4) layers:  input layer, synapse line, accumulator layer, sum line, WTA-layer, activations line, output layer


class NaiveNeuronScene(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 2,
            "num_inputs": 16,
    }

    def create_edge(self, neuron, mob):
        """

        :param neuron:
        :param mob:
        :return:
        """
        diff_vec = mob.get_center() - neuron.get_center()
        normvec = diff_vec / np.linalg.norm(diff_vec)
        # end_point = mob.get_center() - mob.height/2 * vec
        start_point = mob.get_edge_center(UP)
        end_point = neuron.radius * normvec + neuron.get_center()

        # tip_length = 1,
        return Line(
                start_point,
                end_point,
                # max_tip_length_to_length_ratio=0.08,
                # max_stroke_width_to_length_ratio=2,
                buff=0,
                stroke_color=self.CONFIG["edge_color"],
                # stroke_width=self.CONFIG["edge_stroke_width"],
                stroke_opacity=0.8,
        )

    def construct(self):

        self.camera.background_color = manim_colors.BLACK

        # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
        colors = sns.color_palette("colorblind").as_hex()

        # colorcet category palette
        # colors = cc.b_glasbey_category10

        # add single neuron
        neuron = NaiveNeuron(neuron_fill_color=colors[0]).shift(UP * 3)
        self.add(neuron)

        # add input layer
        squares = [Cell(cell_fill_color=colors[_ % len(colors)]) for _ in range(self.CONFIG["num_inputs"])]
        input_layer = VGroup(*squares)
        input_layer.squares = squares
        input_layer.arrange(RIGHT, buff=0.08).move_to(config.bottom).shift(UP)
        input_layer.add_background_rectangle(opacity=0.25,
                                             stroke_opacity=1, stroke_width=3, stroke_color=GREY_B,
                                             buff=2.5 * SMALL_BUFF, color=manim_colors.GRAY_A, # gray_a.value,
                                             corner_radius=squares[0].cell_side_length)
        self.add(input_layer)

        # connect input layer to neuron
        for i, mob in enumerate(input_layer.squares):
            if i % 2 == 0:
                self.add(self.create_edge(neuron, mob))


class GnomeInputNeuronScene(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 2,
            "num_inputs": 16,
    }
    rng = np.random.default_rng(0)

    def create_edge(self, neuron, mob, ori="vert"):
        """

        :param neuron:
        :param mob:
        :param ori:
        :return:
        """
        # get point on neuron boundary in the direction of mob we connect to
        diff_vec = mob.get_center() - neuron.get_center()
        normvec = diff_vec / np.linalg.norm(diff_vec)
        end_point = neuron.radius * normvec + neuron.get_center()

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

        # tip_length = 1,
        return Line(
                start_point,
                end_point,
                # max_tip_length_to_length_ratio=0.08,
                # max_stroke_width_to_length_ratio=2,
                buff=0,
                stroke_color=self.CONFIG["edge_color"],
                # stroke_width=self.CONFIG["edge_stroke_width"],
                stroke_opacity=0.8,
        )

    def construct(self):

        self.camera.background_color = manim_colors.BLACK

        # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
        colors = sns.color_palette("colorblind").as_hex()

        # colorcet category palette
        # colors = cc.b_glasbey_category10

        # add single neuron
        # neuron = Neuron(neuron_fill_color=colors[0]).shift(UP * 3)
        neuron = NaiveNeuron(neuron_fill_color=colors[0]).shift(UP)
        self.add(neuron)

        # output axon
        num_outputs = 16
        output_code = GnomeCode(shape='square', n=num_outputs, cell_stroke_color=DARK_BROWN)
        output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        output_code.shift(RIGHT * diff_vec)
        output_code.add_background()
        self.add(output_code)

        # connect neuron to output layer
        self.add(self.create_edge(neuron, output_code.bins[int(num_outputs / 2)]))

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"], cell_stroke_color=DARK_BROWN)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)
        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()
        self.add(input_code)

        # connect input layer to neuron
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        for i, is_connected in enumerate(connections):
            if is_connected:
                self.add(self.create_edge(neuron, input_code.bins[i]))

        w = int(input_code.num_bins / 2)
        sparse_elements = [0, ] * (input_code.num_bins - w) + [1, ] * w
        new_code = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        print(new_code)
        input_code.set_value(new_code, anim=False)

        # new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        # print(new_code)
        # self.play(code.set_value(new_code), run_time=1)


class DiscreteSynapseScene(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = manim_colors.BLACK
        colors = self.colors

        # add single neuron
        # neuron = Neuron(neuron_fill_color=colors[0]).shift(UP * 3)
        neuron = NaiveNeuron(neuron_fill_color=colors[0]).shift(UP)
        self.add(neuron)

        # output layer
        num_outputs = 17
        output_code = GnomeCode(shape='square', n=num_outputs, cell_stroke_color=DARK_BROWN)
        output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        output_code.shift(RIGHT * diff_vec)
        output_code.add_background()
        self.add(output_code)

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"], cell_stroke_color=DARK_BROWN)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)
        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()
        self.add(input_code)

        # connect neuron to output layer with axon
        self.add(Synapse(neuron, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        for i, is_connected in enumerate(connections):
            if is_connected:
                self.add(Synapse(neuron, input_code.bins[i]))

        # set the current input and output codes
        w = int(input_code.num_bins / 2)
        sparse_elements = [0, ] * (input_code.num_bins - w) + [1, ] * w
        new_data = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        print(new_data)
        input_code.set_value(new_data, anim=False)

        out_data = np.zeros(17)
        out_data[int(input_code.num_bins / 2)] = 1
        print(out_data)
        output_code.set_value(out_data, anim=False)

        # new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        # print(new_code)
        # self.play(code.set_value(new_code), run_time=1)


class DiscreteOperationsScene(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = manim_colors.BLACK
        colors = self.colors

        # add single neuron
        neuron = NeuronWithOperations().shift(UP)
        self.add(neuron)

        sum_arrow = Arrow(start=neuron.counter_box.get_edge_center(RIGHT),
                          end=neuron.counter_box.get_edge_center(RIGHT) + 5 * RIGHT,
                          buff=0.05)
        winner_arrow = Arrow(start=neuron.activation_box.get_edge_center(RIGHT) + 5 * RIGHT,
                             end=neuron.activation_box.get_edge_center(RIGHT),
                             buff=0.05)
        self.add(sum_arrow)
        self.add(winner_arrow)

        # output layer
        num_outputs = 17
        output_code = GnomeCode(shape='square', n=num_outputs, cell_stroke_color=manim_colors.BLACK)
        # output_code = GnomeCode(shape='square', n=num_outputs, cell_stroke_color=manim_colors.BLACK)
        # output_code = GnomeCode(shape='square', n=num_outputs, cell_stroke_color=DARK_BROWN)
        output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        output_code.shift(RIGHT * diff_vec)
        output_code.add_background()
        self.add(output_code)

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"], cell_stroke_color=manim_colors.BLACK)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)
        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()
        self.add(input_code)

        # connect neuron to output layer with axon
        # self.add(Synapse(neuron, output_code.bins[int(num_outputs / 2)], do_cross=False))
        self.add(Synapse(neuron.activation_box, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        for i, is_connected in enumerate(connections):
            if is_connected:
                self.add(Synapse(neuron.counter_box, input_code.bins[i]))

        # set the current input and output codes
        w = int(input_code.num_bins / 2)
        sparse_elements = [0, ] * (input_code.num_bins - w) + [1, ] * w
        new_data = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        print(new_data)
        input_code.set_value(new_data, anim=False)

        out_data = np.zeros(17)
        out_data[int(input_code.num_bins / 2)] = 1
        print(out_data)
        output_code.set_value(out_data, anim=False)

        # new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        # print(new_code)
        # self.play(code.set_value(new_code), run_time=1)

class GnomeSpace(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = manim_colors.BLACK
        colors = self.colors

        # output layer
        # num_outputs = 17
        # output_code = GnomeCode(shape='square', n=num_outputs, cell_stroke_color=manim_colors.BLACK)
        # output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        # diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        # output_code.shift(RIGHT * diff_vec)
        # output_code.add_background()
        # self.add(output_code)

        # input layer
        # input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"], cell_stroke_color=manim_colors.BLACK)
        input_code = GnomeCode(shape='square', n=64, cell_stroke_color=manim_colors.BLACK)
        input_code.arrange_in_grid(rows=4, buff=(0.01, 0.01)).center()
        # input_code.arrange(RIGHT, buff=0.01)#.move_to(config.center)#.shift(0.8 * UP)
        # input_code.shift(RIGHT * diff_vec)
        input_code.add_background(buff=1.5*0.1)
        self.add(input_code)

        # connect neuron to output layer with axon
        # self.add(Synapse(neuron.activation_box, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        # sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
        #         input_code.num_bins - int(input_code.num_bins / 2))
        # connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        # for i, is_connected in enumerate(connections):
        #     if is_connected:
        #         self.add(Synapse(neuron.counter_box, input_code.bins[i]))

        # set the current input and output codes
        w = int(input_code.num_bins / 2)
        sparse_elements = [0, ] * (input_code.num_bins - w) + [1, ] * w
        new_data = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        print(new_data)
        input_code.set_value(new_data, anim=False)

        # out_data = np.zeros(17)
        # out_data[int(input_code.num_bins / 2)] = 1
        # print(out_data)
        # output_code.set_value(out_data, anim=False)
        #
        # new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        # print(new_code)
        # self.play(code.set_value(new_code), run_time=1)



class SynapticBusScene(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = manim_colors.BLACK
        colors = self.colors

        # add single neuron
        neuron = NeuronWithOperations().shift(UP)
        self.add(neuron)

        arrow_color = mpl.colors.rgb2hex(mpl.colormaps.get_cmap("cet_blues")(0.25))
        tip_color = mpl.colors.rgb2hex(mpl.colormaps.get_cmap("cet_blues")(1.0))
        # arrow_color = mpl.colors.rgb2hex(sns.color_palette("tab10")[6])
        sum_arrow = Arrow(start=neuron.counter_box.get_edge_center(RIGHT),
                          end=neuron.counter_box.get_edge_center(RIGHT) + 5 * RIGHT,
                          buff=0.05, stroke_color=arrow_color, stroke_width=12, fill_opacity=1, fill_color=tip_color)
        winner_arrow = Arrow(start=neuron.activation_box.get_edge_center(RIGHT) + 5 * RIGHT,
                             end=neuron.activation_box.get_edge_center(RIGHT),
                             buff=0.05, stroke_color=arrow_color, stroke_width=12, fill_opacity=1, fill_color=tip_color)
        self.add(sum_arrow)
        self.add(winner_arrow)

        # output layer
        num_outputs = 17
        output_code = GnomeCode(shape='square', n=num_outputs)  # , cell_stroke_color=GRAY_C)
        output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        output_code.shift(RIGHT * diff_vec)
        output_code.add_background()
        self.add(output_code)

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"])  # , cell_stroke_color=manim_colors.BLACK)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)
        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()
        self.add(input_code)

        # connect neuron to output layer with axon
        self.add(Synapse(neuron.activation_box, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        synapses = []
        for i, is_connected in enumerate(connections):
            if is_connected:
                if i % 2 == 0:
                    # synapse = Synapse(neuron.counter_box, input_code.bins[i], cross_color="#3b7cb2")
                    synapse = Synapse(neuron.counter_box, input_code.bins[i], gate_color=GREEN)
                else:
                    # synapse = Synapse(neuron.counter_box, input_code.bins[i], cross_color=manim_colors.WHITE)
                    synapse = Synapse(neuron.counter_box, input_code.bins[i], gate_color=manim_colors.RED)
                synapses.append(synapse)
                self.add(synapse)

        # set the current input and output codes
        w = int(input_code.num_bins / 2)
        sparse_elements = [0, ] * (input_code.num_bins - w) + [1, ] * w
        new_data = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        print(new_data)
        input_code.set_value(new_data, anim=False)

        out_data = np.zeros(17)
        out_data[int(input_code.num_bins / 2)] = 1
        print(out_data)
        output_code.set_value(out_data, anim=False)

        print("DONE")

        # new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        # print(new_code)
        # self.play(code.set_value(new_code), run_time=1)


class ColorScene(Scene):

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    # colors = sns.color_palette("colorblind").as_hex()
    # colors = sns.color_palette("colorblind") #, as_cmap=True)

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    """
    Favorite colors
    0: red
    1: deep green
    2: purple
    4: light green
    5: light orange
    6: pink
    7: muted wood brown
    9: muted light purple
    10: muted stone
    11: muted light brown
    12: muted bluish stone
    14: light light yellow
    15: muted orangish brown
    18: muted gray-purple
    19: muted yellow-green
    """

    def construct(self):
        self.camera.background_color = manim_colors.BLACK

        # map name
        colormap = "cet_glasbey_light"
        # colormap = "cet_blues"

        # color map
        local_cmap = mpl.colormaps.get_cmap(colormap)

        # get sample from continuous map using float, returns float tuple of color
        # continuous_tuple_color = local_cmap(1.0)

        # get sample from categorical  map using index, returns float tuple of color
        categorical_tuple_color = local_cmap(1)

        # convert to hex color used by manim
        # continuous_hex_color = mpl.colors.rgb2hex(continuous_tuple_color)
        categorical_hex_color = mpl.colors.rgb2hex(categorical_tuple_color)

        total_colors = len(local_cmap.colors)
        print(total_colors, "colors")

        """
        Favorite colors
        0: red
        1: deep green
        2: purple
        4: light green
        5: light orange
        6: pink
        7: muted wood brown
        9: muted light purple
        10: muted stone
        11: muted light brown
        12: muted bluish stone
        14: light light yellow
        15: muted orangish brown
        18: muted gray-purple
        19: muted yellow-green
        """

        # muted colors
        color_indices1 = [7, 9, 10, 11, 12, 15, 18, 19]

        # bright colors
        color_indices2 = [0, 1, 2, 4, 5, 6, 14]

        colored_arrows1 = []
        # for k in range(total_colors):
        for k in color_indices1:
            temp_color = mpl.colors.rgb2hex(local_cmap(k))
            temp_arrow = Dot(radius=0.2, color=temp_color)

            label = Integer(number=k, edge_to_fix=[0, 0, 0]).scale(0.4)

            # noinspection PyTypeChecker
            label.set_color(manim_colors.BLACK)

            # create VGroup to associate this label and cell
            vgroup = VDict(dict(temp_arrow=temp_arrow, label=label))

            # temp_arrow = Arrow(start=config.left_side, end=config.left_side + RIGHT,
            #                    buff=0.03, stroke_color=temp_color, stroke_width=5, fill_opacity=1,
            #                    fill_color=temp_color)
            # colored_arrows.append(temp_arrow)
            colored_arrows1.append(vgroup)

        colored_arrows1 = VGroup(*colored_arrows1)

        colored_arrows1.arrange_in_grid(buff=(0.16, 0.16)).center()  # move_to(config.left_side).shift(RIGHT)
        self.add(colored_arrows1)

        colored_arrows2 = []
        for k in color_indices2:
            temp_color = mpl.colors.rgb2hex(local_cmap(k))
            temp_arrow = Dot(radius=0.2, color=temp_color)

            label = Integer(number=k, edge_to_fix=[0, 0, 0]).scale(0.4)

            # noinspection PyTypeChecker
            label.set_color(manim_colors.BLACK)

            # create VGroup to associate this label and cell
            vgroup = VDict(dict(temp_arrow=temp_arrow, label=label))

            colored_arrows2.append(vgroup)

        colored_arrows2 = VGroup(*colored_arrows2)

        colored_arrows2.arrange_in_grid(buff=(0.16, 0.16)).center()  # move_to(config.left_side).shift(RIGHT)
        self.add(colored_arrows2)

        color_comp = VGroup(colored_arrows1, colored_arrows2)
        color_comp.arrange(RIGHT, buff=1.0).center()
        self.add(color_comp)



class WindowedNetworkScene(Scene):
    CONFIG = {
            "edge_color": manim_colors.WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    # colors = sns.color_palette("colorblind").as_hex()
    # colors = sns.color_palette("colorblind") #, as_cmap=True)

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    """
    Favorite colors
    0: red
    1: deep green
    2: purple
    4: light green
    5: light orange
    6: pink
    7: muted wood brown
    9: muted light purple
    10: muted stone
    11: muted light brown
    12: muted bluish stone
    14: light light yellow
    15: muted orangish brown
    18: muted gray-purple
    19: muted yellow-green
    """

    # muted colors
    muted_color_indices = [7, 9, 10, 11, 12, 15, 18, 19]


    def construct(self):

        self.camera.background_color = manim_colors.BLACK

        # add single neuron
        neuron = NeuronWithWindow().shift(UP)
        self.add(neuron)

        colormap = "cet_glasbey_light"
        local_cmap = mpl.colormaps.get_cmap(colormap)

        print([mpl.colors.rgb2hex(local_cmap(k)) for k in self.muted_color_indices])

        # RIGHT SIDE
        color0 = mpl.colors.rgb2hex(local_cmap(self.muted_color_indices[1]))
        color1 = mpl.colors.rgb2hex(local_cmap(self.muted_color_indices[2]))
        sum_arrow = Arrow(start=neuron.counter_box.get_edge_center(RIGHT),
                          end=neuron.counter_box.get_edge_center(RIGHT) + 5 * RIGHT,
                          buff=0.05, stroke_color=color0, stroke_width=12, fill_opacity=1, fill_color=color0)
        winner_arrow = Arrow(start=neuron.activation_box.get_edge_center(RIGHT) + 5 * RIGHT,
                             end=neuron.activation_box.get_edge_center(RIGHT),
                             buff=0.05, stroke_color=color1, stroke_width=12, fill_opacity=1, fill_color=color1)
        sum_arrow.set_sheen(0.4,DR)
        winner_arrow.set_sheen(0.4,DR)
        self.add(sum_arrow)
        self.add(winner_arrow)

        # LEFT SIDE
        color0 = mpl.colors.rgb2hex(local_cmap(self.muted_color_indices[3]))
        color1 = mpl.colors.rgb2hex(local_cmap(self.muted_color_indices[4]))
        sum_arrow2 = Arrow(start=neuron.counter_box.get_edge_center(LEFT),
                          end=neuron.counter_box.get_edge_center(LEFT) + 5 * LEFT,
                          buff=0.05, stroke_color=color0, stroke_width=12, fill_opacity=1, fill_color=color0)
        winner_arrow2 = Arrow(start=neuron.activation_box.get_edge_center(LEFT) + 5 * LEFT,
                             end=neuron.activation_box.get_edge_center(LEFT),
                             buff=0.05, stroke_color=color1, stroke_width=12, fill_opacity=1, fill_color=color1)
        sum_arrow2.set_sheen(0.4,DR)
        winner_arrow2.set_sheen(0.4,DR)
        self.add(sum_arrow2)
        self.add(winner_arrow2)

        # output layer
        num_outputs = 17
        output_code = GnomeCode(shape='square', n=num_outputs)  # , cell_stroke_color=GRAY_C)
        output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        output_code.shift(RIGHT * diff_vec)
        output_code.add_background()
        output_code.background_rectangle.set_sheen(-0.3, UL)
        # output_code.set_sheen(-0.3, DR)
        self.add(output_code)

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"])  # , cell_stroke_color=manim_colors.BLACK)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)

        # grid arrangement of layer
        # input_code.arrange_in_grid(buff=(0.01, 0.01)).center().move_to(config.bottom).shift(1.5 * UP)

        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()
        input_code.background_rectangle.set_sheen(-0.3, UL)

        self.add(input_code)

        # connect neuron to output layer with axon
        self.add(Synapse(neuron.activation_box, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        synapses = []
        for i, is_connected in enumerate(connections):
            if is_connected:
                if i % 2 == 0:
                    # synapse = Synapse(neuron.counter, input_code.bins[i], cross_color="#3b7cb2")
                    synapse = Synapse(neuron.counter_box, input_code.bins[i], gate_color=input_code.one_color,
                                      do_gate=True)
                else:
                    # synapse = Synapse(neuron.counter, input_code.bins[i], cross_color=manim_colors.WHITE)
                    synapse = Synapse(neuron.counter_box, input_code.bins[i], gate_color=input_code.zero_color,
                                      do_gate=True)
                synapses.append(synapse)
                self.add(synapse)

        # set the current input and output codes
        w = int(input_code.num_bins / 2)
        sparse_elements = [0, ] * (input_code.num_bins - w) + [1, ] * w
        new_data = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        print(new_data)
        input_code.set_value(new_data, anim=False)

        out_data = np.zeros(17)
        out_data[int(input_code.num_bins / 2)] = 1
        print(out_data)
        output_code.set_value(out_data, anim=False)

        print("DONE")

        # new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        # print(new_code)
        # self.play(code.set_value(new_code), run_time=1)
