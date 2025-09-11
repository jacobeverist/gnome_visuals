from math import *
# appending a path
# appending a path
import sys

import colorcet as cc
from colour import Color
from manim import *
from manim import config as global_config

import matplotlib as mpl  # mpl.colormaps.get_cmap
import seaborn as sns

from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService


sys.path.append("../../")
sys.path.append("../discrete_neurons/")

# algorithm classes
from gnomevisual import *

# manim classes
from gnome import GnomeCode

# ensures colorcet doesn't get autoformatted away by smart IDE
testgray = cc.gray
LinearSegmentedColormap = mpl.colors.LinearSegmentedColormap


class NumberSlider(VGroup):
    def __init__(self, x_range=(0, 1, 0.2), length=10, height=12.5, tracker=None, **kwargs):
        """A class to represent a number together with an associated slider.

        Args:
            x_range (list): A list of 3 floats representing x_min, x_max and x_step.
            length (float): Length of the line.
        """

        if tracker is None:
            self.tracker = ValueTracker(0.00)
        else:
            self.tracker = tracker

        decimal_number = DecimalNumber(self.tracker.get_value(), num_decimal_places=2)
        decimal_number.set_fill(BLACK)

        num_height = decimal_number.get_height()
        num_width = decimal_number.get_width()

        background_rectangle = Rectangle(fill_color=WHITE, fill_opacity=1.0,
                                         height=num_height + 2 * SMALL_BUFF,
                                         width=num_width + 2 * SMALL_BUFF,
                                         stroke_opacity=1,
                                         stroke_width=3,
                                         stroke_color=BLACK)

        number_line = NumberLine(
                x_range=x_range,
                length=length,
                color=BLACK,
                **kwargs,
        )
        number_line.numbers.set_color(BLACK)

        self.nl = number_line

        arrow = Arrow(height * UP, DOWN / 2, stroke_color=BLACK, stroke_width=2, tip_length=0.2, buff=0).next_to(
                number_line.n2p(self.tracker.get_value()), UP)
        # arrow.add_updater(lambda obj: obj.become(obj.copy().next_to(number_line.n2p(self.tracker.get_value()), UP)))
        arrow.add_updater(lambda obj: obj.next_to(number_line.n2p(self.tracker.get_value()), UP))

        # background_rectangle.next_to(arrow, UP, buff=0*SMALL_BUFF)
        # background_rectangle.add_updater(
        #         lambda obj: obj.next_to(arrow, UP, buff=0*SMALL_BUFF)
        # )
        background_rectangle.move_to(arrow.get_top()).shift(UP*background_rectangle.height/2.0).set_x(number_line.n2p(self.tracker.get_value())[0])
        background_rectangle.add_updater(
                lambda obj: obj.move_to(arrow.get_top()).shift(UP * background_rectangle.height / 2.0).set_x(number_line.n2p(self.tracker.get_value())[0])
        )

        # decimal_number.next_to(arrow, UP, buff=SMALL_BUFF)
        decimal_number.move_to(background_rectangle)
        # decimal_number.move_to(background_rectangle.get_center()).align_to(background_rectangle, RIGHT).shift(0.1*LEFT)
        decimal_number.add_updater(
                lambda obj: obj.set_value(
                        self.tracker.get_value(),
                # ).next_to(arrow, UP, buff=SMALL_BUFF)
                # ).move_to(background_rectangle.get_center()).align_to(background_rectangle, RIGHT).shift(0.1*LEFT)
                ).move_to(background_rectangle)
        )


        super().__init__(background_rectangle, decimal_number, number_line, arrow)





class EncoderCollapse(Scene, VoiceoverScene):
    stroke_width = 1
    stroke_color = BLACK

    # brick height and font size
    uh = 0.2
    font_size = 12

    # unit time
    ut = 1.5


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.encoder = PlaceCellEncoder()
        self.tracker = ValueTracker(-0.001)

        # self.nl = NumberLine(
        self.slider = NumberSlider(
                x_range=[0, 1.01, 0.2],
                length=10,
                tracker=self.tracker,
                include_tip=True,
                tip_width=0.25,
                tip_height=0.2,
                include_numbers=True,
                font_size=32,
                stroke_width=4
        ) #.align_on_border(DOWN, buff=0.15)

        self.nl = self.slider.nl

        self.floor_line = Rectangle(color=Color(hex=LIGHT_BROWN),
                                    width=global_config.frame_width,
                                    height=0.05,
                                    stroke_width=0,
                                    fill_opacity=1.0
                                    ) #.align_on_border(DOWN, buff=0.95)

        # constant starting height
        # self.ground_height = self.floor_line.get_top()[1]
        # self.start_height = self.ground_height + 3
        # self.levels = [self.ground_height + i * self.uh for i in range(1000)]

        self.curr_id = 0

        self.whole_blocks = []
        self.whole_dists = []
        self.whole_endpoint = []

        self.sectioned_blocks = []
        self.section_weights = []
        self.section_levels = []
        self.section_dists = []
        self.section_endpoints = []

        self.colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors

    def create_textbox(self, string, sec_lower, sec_upper, *args, color: Color = WHITE, fill_opacity=0.0,
                       add_updater=True, **kwargs):

        # cell_cmap = LinearSegmentedColormap.from_list("cell_X", [WHITE, color.get_rgb()])
        # temp_color1 = cell_cmap(0.6)
        # temp_color2 = cell_cmap(0.6)[:-1]
        # temp_color3 = Color(rgb=temp_color2)
        # print(temp_color1)
        # print(temp_color2)
        # print(temp_color3)

        result = VGroup()
        box = Rectangle(*args, color=color, fill_opacity=fill_opacity, **kwargs)
        box.sec_lower = sec_lower
        box.sec_upper = sec_upper
        # text = Text(string, color=BLACK, font_size=self.font_size).move_to(box.get_center())
        text = Integer(number=int(string), edge_to_fix=[0, 0, 0]).move_to(box.get_center())
        # text = Integer(number=int(string), stroke_color=BLACK, font_size=self.font_size, edge_to_fix=[0, 0, 0]).move_to(box.get_center())
        # text = Text(string, font_size=self.font_size, fill_opacity=fill_opacity).move_to(box.get_center())

        text.set_color(BLACK)

        box_height = box.get_height()
        box_width = box.get_width()

        label_height = text.get_height()
        label_width = text.get_width()

        # box and label ratio
        box_ratio = box_width / box_height
        label_ratio = label_width / label_height

        if box_ratio > label_ratio:
            # height dominates
            text.set_height(box_height - 2 * box_height * 0.2)
        else:
            # width dominates
            text.set_width(box_width - 2 * box_height * 0.2)

        # this_one_color = self.colors[bin_index]
        # self.colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors

        # block_color = Color(rgb=self.colors[self.curr_id])
        # cell_cmap = LinearSegmentedColormap.from_list("cell_X", [WHITE, color.get_rgb()])

        if add_updater:
            pass
            # box.add_updater(
            #         lambda obj: obj.set_opacity(1.0)
            #         if (sec_lower <= self.tracker.get_value() < sec_upper)
            #         else obj.set_opacity(0.5)
            # )

        # highlight if value is within bin boundaries
        # box.add_updater(
        #         lambda obj: obj.set_fill(color)
        #         if (sec_lower <= self.tracker.get_value() < sec_upper)
        #         else obj.set_fill(Color(rgb=cell_cmap(0.6)))
        # )

        result.add(box, text)
        return result

    def get_nearest_boundary_index(self, value):

        nearest_index = None
        nearest_dist = 1e100

        num_bounds = len(self.encoder.region_boundaries)
        for i in range(num_bounds):
            x = self.encoder.region_boundaries[i]
            curr_dist = fabs(value - x)
            if curr_dist < nearest_dist:
                nearest_dist = curr_dist
                nearest_index = i

        return nearest_index

    def add_brick(self, bin_lower, bin_upper):
        """
        1) create whole rectangle for each new block
        2) create sectioned set for each block from above process
        3) store in parallel
        4) fall whole rectangle to max height within cell's region
        5) switch from whole to sectioned set
        6) for each section fall to its associated height from code weight
        7) run anims in parallel


        :param bin_lower:
        :param bin_upper:
        :return:
        """

        # add new place cell to encoder
        self.encoder.add_cell(bin_lower, bin_upper)

        # color for this block
        block_color = Color(rgb=self.colors[self.curr_id])

        # get regions within newly added bin
        lower_index = self.get_nearest_boundary_index(bin_lower)
        upper_index = self.get_nearest_boundary_index(bin_upper)

        # divide into sections at point where weight changes
        weights = self.encoder.region_weights
        boundaries = self.encoder.region_boundaries

        # max weight within cell region
        max_weight = max(weights[lower_index:upper_index + 1])

        by_weight = False

        if by_weight:
            start_level_height = self.nl.get_top()[1] + max_weight * self.uh - self.uh/2.0
            # start_level_height = self.levels[max_weight] - self.uh / 2.0
        else:
            # by level
            start_level_height = self.nl.get_top()[1] + self.curr_id * self.uh + self.uh/2.0
            # start_level_height = self.levels[self.curr_id] + self.uh / 2.0

        # create whole block
        sec_lower = boundaries[lower_index]
        sec_upper = boundaries[upper_index]
        scene_bin_lower = self.nl.number_to_point(sec_lower)[0]
        scene_bin_upper = self.nl.number_to_point(sec_upper)[0]
        new_width = scene_bin_upper - scene_bin_lower
        new_center_whole = scene_bin_lower + new_width / 2.0
        starting_point_whole = RIGHT * new_center_whole + UP * start_level_height

        whole_brick = self.create_textbox(str(self.curr_id),
                                          sec_lower,
                                          sec_upper,
                                          add_updater=False,
                                          color=block_color,
                                          width=new_width,
                                          height=self.uh,
                                          stroke_width=self.stroke_width,
                                          stroke_color=self.stroke_color,
                                          fill_opacity=1.0).move_to(starting_point_whole)

        # highlight if value is within bin boundaries
        # whole_brick.add_updater(
        #         lambda obj: obj[0].set_fill(DARKER_GRAY)
        #         if sec_upper > self.tracker.get_value() >= sec_lower
        #         else obj[0].set_fill(block_color)
        # )
        self.whole_blocks.append(whole_brick)

        # create pieces of sectioned block
        brick_sections = []
        weight_sections = []
        level_sections = []
        fall_dist_sections = []
        fall_endpoint_sections = []

        section_max_weight = max(weights[lower_index:upper_index + 1])
        # mid_level_height = self.levels[section_max_weight] - self.uh / 2.0
        mid_level_height = self.nl.get_top()[1] + section_max_weight * self.uh - self.uh / 2.0

        lo_index = lower_index
        while lo_index < upper_index:
            hi_index = lo_index + 1

            # until boundary or weight chnage
            while hi_index != upper_index and weights[lo_index] == weights[hi_index]:
                hi_index += 1

            # get rectangle parameters in SCENE coordinates
            sec_lower = boundaries[lo_index]
            sec_upper = boundaries[hi_index]
            scene_bin_lower = self.nl.number_to_point(sec_lower)[0]
            scene_bin_upper = self.nl.number_to_point(sec_upper)[0]
            new_width = scene_bin_upper - scene_bin_lower
            new_center = scene_bin_lower + new_width / 2.0
            # settled_level_height = self.levels[weights[lo_index]] - self.uh / 2.0
            settled_level_height = self.nl.get_top()[1] + weights[lo_index] * self.uh - self.uh / 2.0

            section_brick_center = RIGHT * new_center + UP * mid_level_height

            # create visual of brick
            new_sectioned_brick = self.create_textbox(str(self.curr_id),
                                                      boundaries[lo_index],
                                                      boundaries[hi_index],
                                                      # boundaries[lower_index],
                                                      # boundaries[upper_index],
                                                      add_updater=False,
                                                      color=block_color,
                                                      width=new_width,
                                                      height=self.uh,
                                                      stroke_width=self.stroke_width,
                                                      stroke_color=self.stroke_color,
                                                      fill_opacity=1.0).move_to(section_brick_center)

            # highlight if value is within bin boundaries
            # new_sectioned_brick.add_updater(
            #         lambda obj: obj[0].set_fill(DARKER_GRAY)
            #         if sec_upper > self.tracker.get_value() >= sec_lower
            #         else obj[0].set_fill(block_color)
            # )

            section_start_level = mid_level_height
            section_end_level = settled_level_height
            fall_dist2 = section_start_level - section_end_level
            section_end_point = RIGHT * section_brick_center + UP * section_end_level

            lo_index = hi_index

            brick_sections.append(new_sectioned_brick)
            weight_sections.append(weights[lo_index])
            level_sections.append(settled_level_height)
            fall_dist_sections.append(fall_dist2)
            fall_endpoint_sections.append(section_end_point)

        self.sectioned_blocks.append(brick_sections)
        self.section_weights.append(weight_sections)
        self.section_levels.append(level_sections)
        self.section_dists.append(fall_dist_sections)
        self.section_endpoints.append(fall_endpoint_sections)

        for brick_i in range(len(brick_sections)):
            brick_vg = brick_sections[brick_i]
            # ADD SECTIONED BRICKS
            self.add(brick_vg)
            brick_vg.set_opacity(0)

        # ADD WHOLE BRICK
        self.add(whole_brick)
        # self.nl.add(whole_brick)

        ending_point_whole = RIGHT * new_center_whole + UP * mid_level_height
        fall_dist1 = np.linalg.norm(starting_point_whole - ending_point_whole)

        self.whole_dists.append(fall_dist1)
        self.whole_endpoint.append(ending_point_whole)

        # end of method call
        self.curr_id += 1

    def split_brick(self, cell_i):

        whole_brick = self.whole_blocks[cell_i]
        fall_dist1 = self.whole_dists[cell_i]
        whole_endpoint = self.whole_endpoint[cell_i]

        brick_sections = self.sectioned_blocks[cell_i]
        fall_dist_sections = self.section_dists[cell_i]
        fall_endpoint_sections = self.section_endpoints[cell_i]

        # SECTIONED
        diff_anims = []
        for brick_i in range(len(brick_sections)):
            brick_vg = brick_sections[brick_i]

            wait_anim = Wait(self.ut * fall_dist1)
            fade_anim = ApplyMethod(brick_vg.set_opacity, 1.0, run_time=0.0)

            fall_dist2 = fall_dist_sections[brick_i]
            section_end_point = fall_endpoint_sections[brick_i]

            if fall_dist2 > 0:
                fall_anim = brick_vg.animate(rate_func=rate_functions.linear,
                                             run_time=self.ut * fall_dist2).set_opacity(1.0).move_to(
                        section_end_point)
                diff_anims.append(Succession(wait_anim, fade_anim, fall_anim))
            else:
                diff_anims.append(Succession(wait_anim, fade_anim))

        whole_brick_anim = whole_brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist1).move_to(
                whole_endpoint)

        whole_fade_anim1 = ApplyMethod(whole_brick[0].set_opacity, 0.0, run_time=0.0)
        whole_fade_anim2 = ApplyMethod(whole_brick[1].set_opacity, 0.0, run_time=0.0)

        diff_anims.append(Succession(whole_brick_anim, whole_fade_anim1, whole_fade_anim2))

        return diff_anims

    def construct(self):

        # create floor visual
        self.add(self.floor_line)

        # initialize
        self.tracker.set_value(-0.001)

        # create number slider
        self.add_foreground_mobject(self.slider)

        # create encoder
        subject_encoder = MultiEncoder()
        for k in [7, 11, 13]:
            subject_encoder.add_encoder(TaperingWeightEncoder(n=k, w=3))

        # create and show brick objects for encoder bin
        for b in subject_encoder.bins:
            self.add_brick(b.lower, b.upper)

        # pause 1s
        self.play(Wait(1))

        # creating brick falling, splitting, and settling animations
        all_anims = []
        for cell_i in range(self.curr_id):
            diff_anims = self.split_brick(cell_i)
            if len(diff_anims) > 0:
                all_anims += diff_anims

        # play animations
        if len(all_anims) > 0:
            self.play(*all_anims)

        # pause 1s
        self.play(Wait(1))


class AnimateEncoding(EncoderCollapse):

    def construct(self):
        # Initialize speech synthesis using Azure's TTS API
        self.set_speech_service(
            AzureService(
                # voice="en-US-JacobNeural",
                voice="en-US-GuyNeural", style="newscast",
                # voice="en-US-JasonNeural", style="friendly",
                # voice="en-US-DavisNeural", style="friendly",
                # voice="en-US-TonyNeural", style="friendly",
                # style="newscast-casual",  # global_speed=1.15
                # style="friendly",  # global_speed=1.15
                prosody={"rate": 1.25}
            )
        )

        self.camera.background_color = GRAY

        self.ut = self.ut * 0.2

        # create floor visual
        # self.floor_line.align_on_border(DOWN, buff=0.95)
        # self.add(self.floor_line)

        self.tracker.set_value(-0.001)

        # create number slider
        self.slider.scale(0.5).move_to(ORIGIN).align_on_border(DOWN, buff=0.4) #.shift(UP*2)
        # self.slider.scale(0.5).move_to(ORIGIN).next_to(self.floor_line, UP, buff=0.15)
        # self.slider.scale(0.5).move_to(ORIGIN).align_to(self.floor_line, DOWN)
        # self.slider.scale(0.5).move_to(ORIGIN).align_on_border(DOWN, buff=0.15)
        # self.slider.align_on_border(DOWN, buff=0.15)
        self.add_foreground_mobject(self.slider)

        # self.slider.scale(0.5)
        # self.floor_line.scale(0.5)

        # create encoder
        subject_encoder = MultiEncoder()
        for k in [7, 11, 13]:
            subject_encoder.add_encoder(TaperingWeightEncoder(n=k, w=3))

        num_outputs = len(subject_encoder.bins)
        output_code = GnomeCode(shape='square', n=num_outputs)  # , cell_stroke_color=GRAY_C)
        # output_code.arrange_in_grid(cols=16, buff=(0.01, 0.01)).scale(0.7).move_to(config.top).shift(0.6 * DOWN)
        output_code.arrange_in_grid(cols=4, buff=(0.01, 0.01)).scale(0.7).align_on_border(RIGHT, buff=0.2)#move_to(config.right_side)
        output_code.add_updater(
                lambda obj: obj.set_value(subject_encoder.encode(self.tracker.get_value()), anim=False)
        )
        output_code.set_value(subject_encoder.encode(self.tracker.get_value()), anim=False)
        self.add(output_code)

        # self.slider.scale(0.5)

        # create and show brick objects for encoder bin
        for b in subject_encoder.bins:
            self.add_brick(b.lower, b.upper)



        # return

        self.play(Wait(0.2))

        for cell_i in range(self.curr_id):
            brick_vg = self.whole_blocks[cell_i]
            box = brick_vg[0]
            cell_cmap = LinearSegmentedColormap.from_list("cell_%d" % cell_i, [WHITE, self.colors[cell_i]])
            one_color = Color(rgb=cell_cmap(1.0)[:3])
            zero_color = Color(rgb=cell_cmap(0.0)[:3])
            box.add_updater(
                    lambda obj, dt, one_color=one_color, zero_color=zero_color:
                    obj.set_fill(one_color, opacity=1)
                    if (obj.sec_lower <= self.tracker.get_value() < obj.sec_upper)
                    else obj.set_fill(zero_color, opacity=1)
            )

        self.play(self.tracker.animate.set_value(1.001), run_time=1.0,
                  rate_func=rate_functions.linear)
        self.play(Wait(0.2))
        self.play(self.tracker.animate.set_value(-0.001), run_time=1.0,
                  rate_func=rate_functions.linear)

        for cell_i in range(self.curr_id):
            brick_vg = self.whole_blocks[cell_i]
            box = brick_vg[0]
            box.remove_updater(box.updaters[-1])
            cell_cmap = LinearSegmentedColormap.from_list("cell_%d" % cell_i, [WHITE, self.colors[cell_i]])
            one_color = Color(rgb=cell_cmap(1.0)[:3])
            box.set_fill(one_color, opacity=1)

        # pause 1s
        self.play(Wait(0.2))

        # creating brick falling, splitting, and settling animations
        all_anims = []
        for cell_i in range(self.curr_id):
            diff_anims = self.split_brick(cell_i)
            if len(diff_anims) > 0:
                all_anims += diff_anims

        # play animations
        if len(all_anims) > 0:
            self.play(*all_anims)

        self.play(Wait(0.2))

        for cell_i in range(self.curr_id):
            brick_vg = self.whole_blocks[cell_i]
            encoder_bin = subject_encoder.bins[cell_i]

            brick_sections = self.sectioned_blocks[cell_i]
            for brick_i in range(len(brick_sections)):
                brick_vg2 = brick_sections[brick_i]
                box = brick_vg2[0]

                cell_cmap = LinearSegmentedColormap.from_list("cell_%d" % cell_i, [WHITE, self.colors[cell_i]])
                one_color = Color(rgb=cell_cmap(1.0)[:3])
                cong_color = Color(rgb=cell_cmap(0.2)[:3])
                zero_color = Color(rgb=cell_cmap(0.0)[:3])

                box.add_updater(
                        lambda obj, dt, lower=encoder_bin.lower, upper=encoder_bin.upper,
                               one_color=one_color, cong_color=cong_color, zero_color=zero_color:
                        obj.set_fill(one_color, opacity=1)
                        if (obj.sec_lower <= self.tracker.get_value() < obj.sec_upper)
                        else (
                                obj.set_fill(cong_color, opacity=1) if (lower <= self.tracker.get_value() < upper)
                                else obj.set_fill(zero_color, opacity=1)
                        )
                )

                # Region Highlight Only
                # box.add_updater(
                #         lambda obj, dt, one_color=one_color, zero_color=zero_color:
                #         obj.set_fill(one_color, opacity=1)
                #         if (obj.sec_lower <= self.tracker.get_value() < obj.sec_upper)
                #         else obj.set_fill(zero_color, opacity=1)
                # )

                # box.add_updater(
                #         lambda obj, dt, lower=encoder_bin.lower, upper=encoder_bin.upper, one_color=one_color,
                #                zero_color=zero_color:
                #         obj.set_fill(one_color, opacity=1)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_fill(zero_color, opacity=1)
                # )

                # box.add_updater(
                #         lambda obj, dt, b=encoder_bin, one_color=one_color, zero_color=zero_color:
                #         obj.set_fill(one_color, opacity=1).set_stroke_width(3 * self.stroke_width)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_fill(zero_color, opacity=1).set_stroke_width(self.stroke_width)
                # )

                # box.add_updater(
                #         lambda obj, dt, b=encoder_bin, one_color=Color(rgb=cell_cmap(1.0))[:3], zero_color=Color(rgb=cell_cmap(0.6))[:3]:
                #         obj.set_fill(one_color, opacity=1).set_sheen(0.0001, DR).set_stroke_width(2 * self.stroke_width)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_fill(zero_color, opacity=1).set_sheen(0.7, DR).set_stroke_width(self.stroke_width)
                # )

                # cell_cmap = LinearSegmentedColormap.from_list("cell_X", [WHITE, color.get_rgb()])
                # highlight if value is within bin boundaries
                # box.add_updater(
                #         lambda obj: obj.set_fill(color)
                #         if (sec_lower <= self.tracker.get_value() < sec_upper)
                #         else obj.set_fill(Color(rgb=cell_cmap(0.6)))
                # )

                # box.add_updater(
                #         lambda obj, dt, b=encoder_bin: obj.set_sheen(0.4, DR).set_stroke_width(2*self.stroke_width)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_sheen(0.0001).set_stroke_width(self.stroke_width)
                # )
                # box.add_updater(
                #         lambda obj, dt, b=encoder_bin: obj.set_stroke_color(GRAY).set_stroke_width(2*self.stroke_width)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_stroke_color(self.stroke_color).set_stroke_width(self.stroke_width)
                # )
                # box.add_updater(
                #         lambda obj, dt, b=encoder_bin: obj.set_stroke_width(2*self.stroke_width)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_stroke_width(self.stroke_width)
                # )
                # box.add_updater(
                #         lambda obj, dt, b=encoder_bin: obj.set_opacity(1.0)
                #         if (b.lower <= self.tracker.get_value() < b.upper)
                #         else obj.set_opacity(0.5)
                # )
                # brick_vg2.resume_updating()

        # self.slider.tracker.set_value(0.5)
        # self.play(self.tracker.animate.set_value(0.999), run_time=3,
        #           rate_func=rate_functions.there_and_back_with_pause)
        self.play(self.tracker.animate.set_value(1.001), run_time=1.0,
                  rate_func=rate_functions.linear)
        self.play(Wait(0.2))
        self.play(self.tracker.animate.set_value(-0.001), run_time=1.0,
                  rate_func=rate_functions.linear)

        # pause 1s
        self.play(Wait(0.2))

        # self.play(self.slider.tracker.animate.set_value(0.5), run_time=1)

