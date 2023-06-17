from manim import *
from manim.mobject.geometry.tips import *

# appending a path
sys.path.append("../../")


class ShiftedAxisGraph(Scene):
    """
    Demonstration of shifting the y-axis to the left-side border of NumberPlane
    Cannot move yaxis directly without screwing up the internal NumberPlane class calculations
    Instead, we use a yaxis_shift variable in all calculations and relabel the x-axis ticks
    """

    def construct(self):

        # xrange
        xmin = -2.0
        xmax = 6.0

        # shift origin to make y-axis at border of number plane
        yaxis_shift = -xmin

        # size of numberplane scaled to fit camera frame
        x_frame_pad = 0.7
        y_frame_pad = 0.5
        x_length = self.camera.frame_width - 2 * x_frame_pad
        y_length = self.camera.frame_height - 2 * y_frame_pad

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

        # add zero to y-axis since it is normally removed
        number_plane.y_axis.add_labels({0: 0.0})

        # add to scene
        self.add(number_plane)

        # define function to plot
        def gauss_func(t):
            # gauss function parameters
            sigma = 0.5
            amp = 1
            mu = 2.5

            # shift input
            t_shift = t - yaxis_shift
            return amp * np.exp(-(t_shift - mu) * (t_shift - mu) / (2 * sigma * sigma))

        # plot gaussian function
        gauss_graph = number_plane.plot(gauss_func, color=RED, use_smoothing=False,
                                        x_range=[xmin + yaxis_shift, xmax + yaxis_shift + 0.001, 0.001])
        self.add(gauss_graph)


        # Ways to convert NumberPlane coordinates to scene points

        # points on x-axis: 2, 4
        pnt_2 = RIGHT * (yaxis_shift + 2.0)
        pnt_4 = RIGHT * (yaxis_shift + 4.0)
        x_points = number_plane.coords_to_point([pnt_2, pnt_4])

        # add them to scene
        for pnt in x_points:
            self.add(Dot(pnt, color=YELLOW))

        # points on y-axis using axis directly: 0.6
        pntx = number_plane.y_axis.number_to_point(0.6)
        self.add(Dot(pntx, color=GREEN))

        # points on numberplane:  (1, 0.5), (4, 0.75)
        pnt_1__0_5 = RIGHT * (yaxis_shift + 1.0) + UP * 0.5
        pnt_4__0_75 = RIGHT * (yaxis_shift + 4.0) + UP * 0.75
        xy_points = number_plane.coords_to_point([pnt_1__0_5, pnt_4__0_75])

        # add them to scene
        for pnt in xy_points:
            self.add(Dot(pnt, color=BLUE))
