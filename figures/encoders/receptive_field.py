from manim import *
from manim.mobject.geometry.tips import *

# appending a path
sys.path.append("../../")


class ExampleFunctionGraph(Scene):
    def construct(self):
        # gauss function parameters
        sigma = 0.5
        amp = 1
        mu = 2.5

        # xrange
        xmin = -2.0
        xmax = 6.0

        # shift origin to make y-axis at border of number plane
        yaxis_shift = -xmin

        # camera frame parameters
        frame_height = self.camera.frame_height
        frame_width = self.camera.frame_width

        # size of numberplane scaled to fit camera frame
        x_frame_pad = 0.7
        y_frame_pad = 0.5
        x_length = frame_width - 2*x_frame_pad
        y_length = frame_height - 2*y_frame_pad

        number_plane = NumberPlane(
                background_line_style={
                        "stroke_color": TEAL,
                        "stroke_width": 2,
                        "stroke_opacity": 0.4
                },

                # x-axis config
                x_axis_config={"include_numbers": False, "include_tip": True,
                               "tip_shape": StealthTip, "tip_height": 0.15},
                x_range=[xmin + yaxis_shift, xmax + yaxis_shift + 0.001, 1],
                x_length=x_length,

                # y-axis config
                y_axis_config={"label_direction": LEFT, "include_numbers": True, "include_tip": True,
                               "tip_shape": StealthTip, "tip_height": 0.15},
                y_range=[0, 1.001, 0.25],
                y_length=y_length
        )

        # Shift x-axis labels by mu
        label_indices = np.arange(xmin + yaxis_shift, xmax + yaxis_shift + 0.001, 1).astype(int)
        shifted_xlabels = np.arange(xmin, xmax + 0.001, 1).astype(int)
        label_dict = {k: v for (k, v) in zip(label_indices, shifted_xlabels)}
        number_plane.x_axis.add_labels(label_dict)
        self.add(number_plane)

        # Plot gaussian function
        def gauss_func(t):
            t_shift = t - yaxis_shift
            return amp * np.exp(-(t_shift - mu) * (t_shift - mu) / (2 * sigma * sigma))

        gauss_graph = number_plane.plot(gauss_func, color=RED, use_smoothing=False,
                                        x_range=[xmin + yaxis_shift, xmax + yaxis_shift + 0.001, 0.001])
        self.add(gauss_graph)

        # print(number_plane.coords_to_point([LEFT, ]))
        # print(number_plane.y_axis.number_to_point(-1.0))
        # print(LEFT * number_plane.x_axis.number_to_point(10.0))
