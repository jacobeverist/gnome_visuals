# Math Animation
# Colors
import colorcet as cc
import matplotlib as mpl  # mpl.colormaps.get_cmap
import seaborn as sns
from manim import *
from manim.utils.color import Colors

testcc = cc.gray
cmap = mpl.colormaps.get_cmap

# Parts
from gnome import GnomeCode, Neuron, Cell

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
        neuron = Neuron(neuron_fill_color=colors[0]).shift(UP * 3)
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
        neuron = Neuron(neuron_fill_color=colors[0]).shift(UP * 3)
        self.add(neuron)

        code = GnomeCode(shape='square', n=self.CONFIG["num_inputs"])
        code.arrange(RIGHT, buff=0.08).move_to(config.bottom).shift(UP)
        code.add_background()
        self.add(code)

        # connect input layer to neuron
        sparse_elements = [0, ] * int(code.num_bins / 2) + [1, ] * int(code.num_bins / 2)
        connections = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        for i, is_connected in enumerate(connections):
            if is_connected:
                self.add(self.create_edge(neuron, code.bins[i]))

        w = int(code.num_bins / 2)
        sparse_elements = [0, ] * (code.num_bins - w) + [1, ] * w
        new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        print(new_code)
        code.set_value(new_code, anim=False)

        new_code = self.rng.choice(sparse_elements, code.num_bins, replace=False, shuffle=True)
        print(new_code)
        self.play(code.set_value(new_code), run_time=1)
