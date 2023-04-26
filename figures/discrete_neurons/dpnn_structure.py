# Math Animation
# Colors
import colorcet as cc
import matplotlib as mpl  # mpl.colormaps.get_cmap

# seaborn perceptually uniform color maps:
# "rocket", "mako", "flare", "crest", "magma", "viridis"
import seaborn as sns

from manim import *
from manim.utils.color import Colors

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
            "edge_color": WHITE,
            "edge_stroke_width": 2,
            "num_inputs": 16,
    }

    def create_edge(self, neuron, mob):

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

        self.camera.background_color = BLACK

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
                                             buff=2.5 * SMALL_BUFF, color=Colors.gray_a.value,
                                             corner_radius=squares[0].cell_side_length)
        self.add(input_layer)

        # connect input layer to neuron
        for i, mob in enumerate(input_layer.squares):
            if i % 2 == 0:
                self.add(self.create_edge(neuron, mob))


class GnomeInputNeuronScene(Scene):
    CONFIG = {
            "edge_color": WHITE,
            "edge_stroke_width": 2,
            "num_inputs": 16,
    }
    rng = np.random.default_rng(0)

    def create_edge(self, neuron, mob, ori="vert"):

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

        self.camera.background_color = BLACK

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
            "edge_color": WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = BLACK
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
            "edge_color": WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = BLACK
        colors = self.colors


        # add single neuron
        neuron = NeuronWithOperations().shift(UP)
        self.add(neuron)

        sum_arrow = Arrow(start=neuron.counter.get_edge_center(RIGHT),
                          end=neuron.counter.get_edge_center(RIGHT) + 5*RIGHT,
                          buff=0.05)
        winner_arrow = Arrow(start=neuron.activation.get_edge_center(RIGHT) + 5*RIGHT,
                             end=neuron.activation.get_edge_center(RIGHT),
                             buff=0.05)
        self.add(sum_arrow)
        self.add(winner_arrow)


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
        #self.add(Synapse(neuron, output_code.bins[int(num_outputs / 2)], do_cross=False))
        self.add(Synapse(neuron.activation, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        for i, is_connected in enumerate(connections):
            if is_connected:
                self.add(Synapse(neuron.counter, input_code.bins[i]))

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


class SynapticBusScene(Scene):
    CONFIG = {
            "edge_color": WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = BLACK
        colors = self.colors


        # add single neuron
        neuron = NeuronWithOperations().shift(UP)
        self.add(neuron)

        arrow_color = mpl.colors.rgb2hex(mpl.colormaps.get_cmap("cet_blues")(0.25))
        tip_color = mpl.colors.rgb2hex(mpl.colormaps.get_cmap("cet_blues")(1.0))
        #arrow_color = mpl.colors.rgb2hex(sns.color_palette("tab10")[6])
        sum_arrow = Arrow(start=neuron.counter.get_edge_center(RIGHT),
                          end=neuron.counter.get_edge_center(RIGHT) + 5*RIGHT,
                          buff=0.05, stroke_color=arrow_color, stroke_width=12, fill_opacity=1, fill_color=tip_color)
        winner_arrow = Arrow(start=neuron.activation.get_edge_center(RIGHT) + 5*RIGHT,
                             end=neuron.activation.get_edge_center(RIGHT),
                             buff=0.05, stroke_color=arrow_color, stroke_width=12, fill_opacity=1, fill_color=tip_color)
        self.add(sum_arrow)
        self.add(winner_arrow)


        # output layer
        num_outputs = 17
        output_code = GnomeCode(shape='square', n=num_outputs) #, cell_stroke_color=GRAY_C)
        output_code.arrange(RIGHT, buff=0.01).move_to(config.top).shift(0.8 * DOWN)
        diff_vec = neuron.get_x() - output_code.bins[int(num_outputs / 2)].get_x()
        output_code.shift(RIGHT * diff_vec)
        output_code.add_background()
        self.add(output_code)

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"]) #, cell_stroke_color=BLACK)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)
        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()
        self.add(input_code)

        # connect neuron to output layer with axon
        self.add(Synapse(neuron.activation, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        synapses = []
        for i, is_connected in enumerate(connections):
            if is_connected:
                if i % 2 == 0:
                    #synapse = Synapse(neuron.counter, input_code.bins[i], cross_color="#3b7cb2")
                    synapse = Synapse(neuron.counter, input_code.bins[i], cross_color=GREEN)
                else:
                    #synapse = Synapse(neuron.counter, input_code.bins[i], cross_color=WHITE)
                    synapse = Synapse(neuron.counter, input_code.bins[i], cross_color=RED)
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


class WindowedNetworkScene(Scene):
    CONFIG = {
            "edge_color": WHITE,
            "edge_stroke_width": 3,
            "num_inputs": 17,
    }
    rng = np.random.default_rng(0)

    # Name of a seaborn palette (deep, muted, bright, pastel, dark, colorblind)
    colors = sns.color_palette("colorblind").as_hex()

    # colorcet category palette
    # colors = cc.b_glasbey_category10

    def construct(self):

        self.camera.background_color = BLACK
        colors = self.colors

        # add single neuron
        neuron = NeuronWithWindow().shift(UP)
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
        #output_code.background_rectangle.set_sheen(-0.3, DR)
        #output_code.set_sheen(-0.3, DR)
        self.add(output_code)

        # input layer
        input_code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"])  # , cell_stroke_color=BLACK)
        input_code.arrange(RIGHT, buff=0.01).move_to(config.bottom).shift(0.8 * UP)

        # grid arrangement of layer
        # input_code.arrange_in_grid(buff=(0.01, 0.01)).center().move_to(config.bottom).shift(1.5 * UP)

        input_code.shift(RIGHT * diff_vec)
        input_code.add_background()

        self.add(input_code)

        # connect neuron to output layer with axon
        self.add(Synapse(neuron.activation, output_code.bins[int(num_outputs / 2)], do_gate=False))

        # connect input layer to neuron with synapses
        sparse_elements = [0, ] * int(input_code.num_bins / 2) + [1, ] * (
                input_code.num_bins - int(input_code.num_bins / 2))
        connections = self.rng.choice(sparse_elements, input_code.num_bins, replace=False, shuffle=True)
        synapses = []
        for i, is_connected in enumerate(connections):
            if is_connected:
                if i % 2 == 0:
                    # synapse = Synapse(neuron.counter, input_code.bins[i], cross_color="#3b7cb2")
                    synapse = Synapse(neuron.counter_box, input_code.bins[i], cross_color=GREEN, do_gate=True)
                else:
                    # synapse = Synapse(neuron.counter, input_code.bins[i], cross_color=WHITE)
                    synapse = Synapse(neuron.counter_box, input_code.bins[i], cross_color=RED, do_gate=True)
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




