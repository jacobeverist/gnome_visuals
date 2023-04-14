import itertools as it

from manim import *

# printing boolean arrays neatly
np.set_printoptions(
        precision=3, suppress=True, threshold=1000000, linewidth=400,
        formatter={'bool': lambda bin_val: 'X' if bin_val else '-'})


# manimgl code, needs to be modified to manim_community


class NetworkMobject(VGroup):
    CONFIG = {
            "neuron_radius": 0.15,
            "neuron_to_neuron_buff": MED_SMALL_BUFF,
            "layer_to_layer_buff": LARGE_BUFF,
            "neuron_stroke_color": BLUE,
            "neuron_stroke_width": 3,
            "neuron_fill_color": GREEN,
            "edge_color": GREY_B,
            "edge_stroke_width": 2,
            "edge_propogation_color": YELLOW,
            "edge_propogation_time": 1,
            "max_shown_neurons": 16,
            "brace_for_large_layers": True,
            "average_shown_activation_of_large_layer": True,
            "include_output_labels": False,
    }

    def __init__(self, sizes, **kwargs):
        VGroup.__init__(self, **kwargs)

        self.__dict__.update(**self.CONFIG)

        # neural_networks needs to provide sizes array, integer size for each layer
        # and get_activation_of_all_layers(input_vector) method
        self.layer_sizes = sizes
        self.add_neurons()
        self.add_edges()

    def add_neurons(self):
        layers = VGroup(*[
                self.get_layer(size)
                for size in self.layer_sizes
        ])
        layers.arrange(RIGHT, buff=self.layer_to_layer_buff)
        self.layers = layers
        self.add(self.layers)
        if self.include_output_labels:
            self.add_output_labels()

    def get_layer(self, size):
        layer = VGroup()
        n_neurons = size
        if n_neurons > self.max_shown_neurons:
            n_neurons = self.max_shown_neurons
        neurons = VGroup(*[
                Circle(
                        radius=self.neuron_radius,
                        stroke_color=self.neuron_stroke_color,
                        stroke_width=self.neuron_stroke_width,
                        fill_color=self.neuron_fill_color,
                        fill_opacity=0,
                )
                for x in range(n_neurons)
        ])
        neurons.arrange(
                DOWN, buff=self.neuron_to_neuron_buff
        )
        for neuron in neurons:
            neuron.edges_in = VGroup()
            neuron.edges_out = VGroup()
        layer.neurons = neurons
        layer.add(neurons)

        """
        
        if size > n_neurons:
            dots = OldTex("\\vdots")
            dots.move_to(neurons)
            VGroup(*neurons[:len(neurons) // 2]).next_to(
                dots, UP, MED_SMALL_BUFF
            )
            VGroup(*neurons[len(neurons) // 2:]).next_to(
                dots, DOWN, MED_SMALL_BUFF
            )
            layer.dots = dots
            layer.add(dots)
            if self.brace_for_large_layers:
                brace = Brace(layer, LEFT)
                brace_label = brace.get_tex(str(size))
                layer.brace = brace
                layer.brace_label = brace_label
                layer.add(brace, brace_label)
        """

        return layer

    def add_edges(self):
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.neurons, l2.neurons):
                edge = self.get_edge(n1, n2)
                edge_group.add(edge)
                n1.edges_out.add(edge)
                n2.edges_in.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)

    def get_edge(self, neuron1, neuron2):
        return Line(
                neuron1.get_center(),
                neuron2.get_center(),
                buff=self.neuron_radius,
                stroke_color=self.edge_color,
                stroke_width=self.edge_stroke_width,
        )

    def deactivate_layers(self):
        all_neurons = VGroup(*it.chain(*[
                layer.neurons
                for layer in self.layers
        ]))
        all_neurons.set_fill(opacity=0)
        return self

    def add_output_labels(self):
        self.output_labels = VGroup()
        for n, neuron in enumerate(self.layers[-1].neurons):
            # label = OldTex(str(n))
            label = Text(str(n))
            label.set_height(0.75 * neuron.get_height())
            label.move_to(neuron)
            label.shift(neuron.get_width() * RIGHT)
            self.output_labels.add(label)
        self.add(self.output_labels)


class NetworkScene(Scene):
    CONFIG = {
            "layer_sizes": [8, 6, 6, 4],
            "network_mob_config": {},
    }


    def construct(self):
        self.setup()

    def setup(self):
        self.add_network()
        self.remove_random_edges(prop=0.5)

    def add_network(self):
        # self.network = Network(sizes = self.layer_sizes)

        self.network_mob = NetworkMobject([8, 4, 8, 16, 4])
        self.add(self.network_mob)

    def remove_random_edges(self, prop=0.9):
        for edge_group in self.network_mob.edge_groups:
            for edge in list(edge_group):
                if np.random.random() < prop:
                    edge_group.remove(edge)
