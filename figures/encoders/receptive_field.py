from manim import *

# appending a path
sys.path.append("../../")


class ExampleFunctionGraph(Scene):
    def construct(self):
        # gauss function parameters
        sigma = 0.5
        amp = 1

        # shift origin to make y-axis at border of number plane
        mu = 2.0

        # distance from origin to end of x-range
        xpad = mu

        number_plane = NumberPlane(
                background_line_style={
                        "stroke_color": TEAL,
                        "stroke_width": 4,
                        "stroke_opacity": 0.6
                },
                axis_config={"include_numbers": True},
                x_axis_config={"include_numbers": False},
                y_axis_config={"label_direction": LEFT},
                x_range=[-xpad + mu, xpad + mu + 0.001, 1],
                y_range=[0, 1.001, 0.25],
                x_length=9,
                y_length=7
        )

        # Shift x-axis labels by mu
        label_indices = range(len(np.arange(-xpad + mu, xpad + mu + 0.001, 1)))
        shifted_xlabels = np.arange(-xpad, xpad + 0.001, 1).astype(int)
        label_dict = {k: v for (k, v) in zip(label_indices, shifted_xlabels)}
        number_plane.x_axis.add_labels(label_dict)
        self.add(number_plane)

        # Plot gaussian function
        def gauss_func(t):
            return amp * np.exp(-(t - mu) * (t - mu) / (2 * sigma * sigma))
        gauss_graph = number_plane.plot(gauss_func, color=RED, use_smoothing=False,
                                        x_range=[-xpad + mu, xpad + mu + 0.001, 0.001])
        self.add(gauss_graph)

        # print(number_plane.coords_to_point([LEFT, ]))
        # print(number_plane.y_axis.number_to_point(-1.0))
        # print(LEFT * number_plane.x_axis.number_to_point(10.0))

