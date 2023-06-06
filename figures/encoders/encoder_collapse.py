from math import *

import colorcet as cc
from colour import Color
from manim import *
from manim import config as global_config
import seaborn as sns

# appending a path
sys.path.append("../../")

from gnomecode import *

# ensures colorcet doesn't get autoformatted away by smart IDE
testgray = cc.gray


class NumberSlider(VGroup):
    def __init__(self, x_range=(0, 1, 0.2), length=10, **kwargs):
        """A class to represent a number together with an associated slider.

        Args:
            x_range (list): A list of 3 floats representing x_min, x_max and x_step.
            length (float): Length of the line.
        """
        self.tracker = ValueTracker(0)

        decimal_number = DecimalNumber(self.tracker.get_value(), num_decimal_places=2)

        number_line = NumberLine(
                x_range=x_range,
                length=length,
                **kwargs,
        )

        self.nl = number_line

        arrow = Arrow(5 * UP, DOWN / 2, stroke_width=2, tip_length=0.2, buff=0).next_to(
            number_line.n2p(self.tracker.get_value()), UP)
        arrow.add_updater(lambda obj: obj.become(obj.copy().next_to(number_line.n2p(self.tracker.get_value()), UP)))

        decimal_number.next_to(arrow, UP, buff=MED_SMALL_BUFF)
        decimal_number.add_updater(
                lambda obj: obj.set_value(
                        self.tracker.get_value(),
                ).next_to(number_line.n2p(self.tracker.get_value()) + 6 * UP, UP, buff=0)  # MED_SMALL_BUFF)
        )
        # ).next_to(arrow.get_top(), UP, buff=MED_SMALL_BUFF)

        super().__init__(decimal_number, number_line, arrow)


class EncoderCollapse(Scene):
    stroke_width = 1
    stroke_color = WHITE

    # brick height and font size
    # uh = 0.5
    # font_size = 24
    uh = 0.2
    font_size = 12

    # unit time
    ut = 0.3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.encoder = PlaceCellEncoder()

        # self.nl = NumberLine(
        self.slider = NumberSlider(
                x_range=[0, 1, 0.2],
                length=10,
                include_tip=True,
                tip_width=0.25,
                tip_height=0.2,
                include_numbers=True,
                font_size=32,
                stroke_width=4
        ).align_on_border(DOWN, buff=0.15)

        self.nl = self.slider.nl

        self.floor_line = Rectangle(color=Color(hex=LIGHT_BROWN),
                                    width=global_config.frame_width,
                                    height=0.05,
                                    stroke_width=0,
                                    fill_opacity=0.8
                                    ).align_on_border(DOWN, buff=0.95)

        # constant starting height
        self.ground_height = self.floor_line.get_top()[1]
        self.start_height = self.ground_height + 3

        self.levels = [self.ground_height + i * self.uh for i in range(1000)]
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
        # print(self.colors)

    def create_textbox(self, string, *args, **kwargs):
        result = VGroup()
        box = Rectangle(*args, **kwargs)
        text = Text(string, font_size=self.font_size).move_to(box.get_center())

        box_height = box.get_height()
        box_width = box.get_width()

        label_height = text.get_height()
        label_width = text.get_width()

        # box and label ratio
        box_ratio = box_width / box_height
        label_ratio = label_width / label_height

        if box_ratio > label_ratio:
            # height dominates
            text.set_height(box_height - 2 * box_height * 0.1)
        else:
            # width dominates
            text.set_width(box_width - 2 * box_height * 0.1)

        # if box_height < box_width:
        # box_width > box_height so set height
        # text.set_height(box_height - 2 * box_height * 0.1)
        # else:
        # box_height > box_width, so set width
        # text.set_width(box_width - 2 * box_height * 0.1)

        result.add(box, text)
        return result

    def get_max_level(self):
        # get max level
        if len(self.encoder.region_weights) == 0:
            max_level = 0
        else:
            max_level = max(self.encoder.region_weights)

        return max_level

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

    def drop_brick(self, bin_lower, bin_upper):
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

        # level_height = self.levels[self.curr_id] + self.uh / 2.0
        target_level_height = self.levels[max_weight] - self.uh / 2.0

        # create whole block
        sec_lower = boundaries[lower_index]
        sec_upper = boundaries[upper_index]
        scene_bin_lower = self.nl.number_to_point(sec_lower)[0]
        scene_bin_upper = self.nl.number_to_point(sec_upper)[0]
        new_width = scene_bin_upper - scene_bin_lower
        new_center_whole = scene_bin_lower + new_width / 2.0
        # starting_point = RIGHT * new_center + UP * level_height
        starting_point_whole = RIGHT * new_center_whole + UP * self.start_height

        whole_brick = self.create_textbox(str(self.curr_id),
                                          color=block_color,
                                          width=new_width,
                                          height=self.uh,
                                          stroke_width=self.stroke_width,
                                          stroke_color=self.stroke_color,
                                          fill_opacity=0.8).move_to(starting_point_whole)

        self.whole_blocks.append(whole_brick)

        # create pieces of sectioned block
        brick_sections = []
        weight_sections = []
        level_sections = []

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
            settled_level_height = self.levels[weights[lo_index]] - self.uh / 2.0
            # starting_point = RIGHT * new_center + UP * level_height
            level_point = RIGHT * new_center + UP * target_level_height

            # create visual of brick
            new_sectioned_brick = self.create_textbox(str(self.curr_id),
                                                      color=block_color,
                                                      width=new_width,
                                                      height=self.uh,
                                                      stroke_width=self.stroke_width,
                                                      stroke_color=self.stroke_color,
                                                      fill_opacity=0.8).move_to(level_point)
            lo_index = hi_index

            brick_sections.append(new_sectioned_brick)
            weight_sections.append(weights[lo_index])
            level_sections.append(settled_level_height)

        self.sectioned_blocks.append(brick_sections)
        self.section_weights.append(weight_sections)
        self.section_levels.append(level_sections)

        # ANIMATION

        # WHOLE
        self.add(whole_brick)

        # compute fall distance to scale running time
        ending_point_whole = RIGHT * new_center_whole + UP * target_level_height
        # level_point = RIGHT * new_center + UP * target_level_height
        fall_dist1 = np.linalg.norm(starting_point_whole - ending_point_whole)

        # falling with ease_in_sine as rate_func
        self.play(whole_brick.animate(rate_func=rate_functions.ease_in_sine, run_time=self.ut * fall_dist1).move_to(
                ending_point_whole))

        self.remove(whole_brick)

        # SECTIONED
        diff_anims = []
        for brick_i in range(len(brick_sections)):
            brick_vg = brick_sections[brick_i]
            self.add(brick_vg)
            # brick = brick_vg[0]

            section_brick_center = brick_vg.get_center()

            section_start_level = target_level_height
            section_end_level = level_sections[brick_i]

            fall_dist2 = section_start_level - section_end_level
            section_end_point = RIGHT * section_brick_center + UP * section_end_level

            if fall_dist2 > 0:
                diff_anims.append(
                        brick_vg.animate(rate_func=rate_functions.ease_out_sine, run_time=self.ut * fall_dist2).move_to(
                                section_end_point))

        if len(diff_anims) > 0:
            self.play(*diff_anims)

        # end of method call
        self.curr_id += 1

    def block_all_regions(self):
        """
        # create a section for each subregion of a block
        for i in range(num_sections):
            sec_lower = self.encoder.region_boundaries[lower_index + i]
            sec_upper = self.encoder.region_boundaries[lower_index + i + 1]

            # get rectangle parameters in SCENE coordinates
            scene_bin_lower = self.nl.number_to_point(sec_lower)[0]
            scene_bin_upper = self.nl.number_to_point(sec_upper)[0]
            new_width = scene_bin_upper - scene_bin_lower
            new_center = scene_bin_lower + new_width / 2.0

            level_height = self.levels[self.curr_id] + self.uh / 2.0

            starting_point = RIGHT * new_center + UP * level_height

            # create visual of brick
            new_brick = self.create_textbox(str(self.curr_id), color=Color(hex=RED), width=new_width, height=self.uh,
                                            stroke_width=self.stroke_width, stroke_color=self.stroke_color,
                                            fill_opacity=0.8)
            #
            new_brick.move_to(starting_point)
            self.add(new_brick)
        """
        pass

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
            start_level_height = self.levels[max_weight] - self.uh / 2.0
        else:
            # by level
            start_level_height = self.levels[self.curr_id] + self.uh / 2.0

        # create whole block
        sec_lower = boundaries[lower_index]
        sec_upper = boundaries[upper_index]
        scene_bin_lower = self.nl.number_to_point(sec_lower)[0]
        scene_bin_upper = self.nl.number_to_point(sec_upper)[0]
        new_width = scene_bin_upper - scene_bin_lower
        new_center_whole = scene_bin_lower + new_width / 2.0
        # starting_point = RIGHT * new_center + UP * level_height
        starting_point_whole = RIGHT * new_center_whole + UP * start_level_height

        whole_brick = self.create_textbox(str(self.curr_id),
                                          color=block_color,
                                          width=new_width,
                                          height=self.uh,
                                          stroke_width=self.stroke_width,
                                          stroke_color=self.stroke_color,
                                          fill_opacity=0.8).move_to(starting_point_whole)

        self.whole_blocks.append(whole_brick)

        # create pieces of sectioned block
        brick_sections = []
        weight_sections = []
        level_sections = []
        fall_dist_sections = []
        fall_endpoint_sections = []

        section_max_weight = max(weights[lower_index:upper_index + 1])
        mid_level_height = self.levels[section_max_weight] - self.uh / 2.0

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
            settled_level_height = self.levels[weights[lo_index]] - self.uh / 2.0
            # starting_point = RIGHT * new_center + UP * level_height
            # section_brick_center = RIGHT * new_center + UP * target_level_height
            section_brick_center = RIGHT * new_center + UP * mid_level_height

            # create visual of brick
            new_sectioned_brick = self.create_textbox(str(self.curr_id),
                                                      color=block_color,
                                                      width=new_width,
                                                      height=self.uh,
                                                      stroke_width=self.stroke_width,
                                                      stroke_color=self.stroke_color,
                                                      fill_opacity=0.8).move_to(section_brick_center)

            # section_brick_center = level_point
            # section_start_level = target_level_height
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
            self.add(brick_vg)
            brick_vg.set_opacity(0)
            # brick = brick_vg[0]
            # label = brick_vg[1]
            # brick.set_opacity(0)
            # label.set_opacity(0)

        # ANIMATION

        # WHOLE
        self.add(whole_brick)

        # compute fall distance to scale running time
        # ending_point_whole = RIGHT * new_center_whole + UP * target_level_height
        ending_point_whole = RIGHT * new_center_whole + UP * mid_level_height
        # level_point = RIGHT * new_center + UP * target_level_height
        fall_dist1 = np.linalg.norm(starting_point_whole - ending_point_whole)

        self.whole_dists.append(fall_dist1)
        self.whole_endpoint.append(ending_point_whole)

        # whole_brick.move_to(ending_point_whole)

        # end of method call
        self.curr_id += 1

        # falling with ease_in_sine as rate_func
        # self.play(whole_brick.animate(rate_func=rate_functions.ease_in_sine, run_time=self.ut * fall_dist1).move_to(
        #         ending_point_whole))

    def split_brick(self, cell_i):

        whole_brick = self.whole_blocks[cell_i]
        fall_dist1 = self.whole_dists[cell_i]
        whole_endpoint = self.whole_endpoint[cell_i]

        brick_sections = self.sectioned_blocks[cell_i]
        fall_dist_sections = self.section_dists[cell_i]
        fall_endpoint_sections = self.section_endpoints[cell_i]

        # opaque_changes = [brick_sections[brick_i].animate(run_time=0.001).set_opacity(1) for brick_i in range(len(brick_sections))]
        # opaque_changes += [whole_brick.animate(run_time=0.001).set_opacity(0),]

        # opaque_changes = [FadeIn(brick_sections[brick_i], run_time=0.001) for brick_i in range(len(brick_sections))]
        # opaque_changes += [FadeOut(whole_brick, run_time=0.001),]

        # print(opaque_changes)

        # foo_anims = [
        #         whole_brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist1).move_to(
        #                 whole_endpoint),
        #         AnimationGroup(*opaque_changes),
        # ]

        # whole_brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist1).move_to(whole_endpoint)

        # AnimationGroup()

        # self.remove(whole_brick)

        # opaque_changes = [FadeIn(brick_sections[brick_i], run_time=0.001) for brick_i in range(len(brick_sections))]
        # opaque_changes += [FadeOut(whole_brick, run_time=0.001), ]
        # print(opaque_changes)

        # Value Tracker
        # for brick_i in range(len(brick_sections)):
        #     brick_vg = brick_sections[brick_i]
        #     brick_vg.vt = ValueTracker(0.0)
        #     brick_vg.add_updater(lambda m: m[0].set_opacity(brick_vg.vt.get_value()))

        # SECTIONED
        diff_anims = []
        for brick_i in range(len(brick_sections)):
            brick_vg = brick_sections[brick_i]
            brick = brick_vg[0]
            label = brick_vg[1]

            wait_anim = Wait(self.ut * fall_dist1)
            # fade_anim = FadeIn(brick_sections[brick_i], run_time=0.001)
            # fade_anim = brick_sections[brick_i].animate(run_time=0.001).set(fill_opacity=1)
            #fade_anim = brick_sections[brick_i].vt.set_value(1.0)

            # fade_anim1 = ApplyMethod(brick.set_opacity, 0.8, run_time=0.1)
            # fade_anim2 = ApplyMethod(label.set_opacity, 0.8, run_time=0.1)
            fade_anim = ApplyMethod(brick_vg.set_opacity, 0.8, run_time=0.0)

            fall_dist2 = fall_dist_sections[brick_i]
            section_end_point = fall_endpoint_sections[brick_i]

            if fall_dist2 > 0:
                print(cell_i, "section fall", brick_i, fall_dist2, section_end_point)
                # fall_dist2 = fall_dist2 * 10

                # fall_anim = fade_anim.target_mobject.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist2).set_opacity(0.8).move_to(
                #         section_end_point)

                fall_anim = brick_vg.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist2).set_opacity(0.8).move_to(
                    section_end_point)
                # fall_anim1 = brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist2).set_opacity(0.8).move_to(
                #         section_end_point)
                # fall_anim2 = label.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist2).move_to(
                #         section_end_point)

                # diff_anims.append(LaggedStart(fade_anim))

                # diff_anims.append(fade_anim1)
                # diff_anims.append(fade_anim2)
                # diff_anims.append(fall_anim1)
                # diff_anims.append(fall_anim2)
                # diff_anims.append(fall_anim)
                #diff_anims.append(Succession(fade_anim1, fall_anim1, fall_anim2))
                diff_anims.append(Succession(wait_anim, fade_anim, fall_anim))
                # diff_anims.append(Succession(wait_anim, fade_anim, fall_anim))
                # diff_anims.append(
                #         brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist2).move_to(
                #                 section_end_point))
            else:
                diff_anims.append(Succession(wait_anim, fade_anim))
                # diff_anims.append(fade_anim)
                # diff_anims.append(fade_anim2)
                # diff_anims.append(Succession(fade_anim1, fade_anim2))
                pass

        # print(cell_i, "whole fall", fall_dist1, whole_endpoint)

        whole_brick_anim = whole_brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist1).move_to(
                whole_endpoint)
        # whole_fade_anim = FadeOut(whole_brick, run_time=0.001)

        whole_fade_anim1 = ApplyMethod(whole_brick[0].set_opacity, 0.0, run_time=0.0)
        whole_fade_anim2 = ApplyMethod(whole_brick[1].set_opacity, 0.0, run_time=0.0)

        diff_anims.append(Succession(whole_brick_anim, whole_fade_anim1, whole_fade_anim2))
        # swap_anim = AnimationGroup(*opaque_changes)
        # section_anim = AnimationGroup(*diff_anims)

        # succession_anims = [
        # drop whole brick
        # whole_brick.animate(rate_func=rate_functions.linear, run_time=self.ut * fall_dist1).move_to(
        #         whole_endpoint),
        # swap mobs
        # AnimationGroup(*opaque_changes),
        # ]
        # foo_anims = [Succession(whole_brick_anim, swap_anim, run_time=self.ut*fall_dist1+self.ut*falL_dist2),]
        # foo_anims = [Succession(whole_brick_anim, swap_anim, section_anim,
        #                         run_time=self.ut * fall_dist1 + self.ut * fall_dist2), ]
        # foo_anims = [Succession(whole_brick_anim, swap_anim, section_anim),]
        # Succession(whole_brick_anim, swap_anim, section_anim)
        # if len(diff_anims) > 0:
        #     Succession(whole_brick_anim, swap_anim, section_anim)
        # else:
        #     Succession(whole_brick_anim, swap_anim)

        # succession_anims.append(AnimationGroup(*diff_anims))

        # foo_anims = [Succession(*succession_anims),]

        # return foo_anims

        return diff_anims

    def construct(self):

        self.add(self.floor_line)
        self.add(self.slider)

        # self.play(self.slider.tracker.animate.set_value(0.5), run_time=1)

        # 1) create step layout
        # 2) drop each block in order
        # 3) done

        # 1) create step layout
        # 2) drop all blocks at same time

        subject_encoder = MultiEncoder()
        for k in [7, 11]:
            subject_encoder.add_encoder(TaperingWeightEncoder(n=k, w=3))
        for b in subject_encoder.bins:
            self.add_brick(b.lower, b.upper)
        self.play(Wait(1))
        all_anims = []
        for cell_i in range(self.curr_id):
            diff_anims = self.split_brick(cell_i)
            if len(diff_anims) > 0:
                all_anims += diff_anims
        if len(all_anims) > 0:
            self.play(*all_anims)
        self.play(Wait(1))

        # self.play(self.slider.tracker.animate.set_value(0.5), run_time=1)
        # self.play(Wait(1))

        # subject_encoder = RandomizedPlaceCellEncoder(n=100, seed=0)
        # for b in subject_encoder.bins:
        #     self.add_brick(b.lower, b.upper)
        # self.play(Wait(1))
        # all_anims = []
        # for cell_i in range(self.curr_id):
        #     diff_anims = self.split_brick(cell_i)
        #     if len(diff_anims) > 0:
        #         all_anims += diff_anims
        # if len(all_anims) > 0:
        #     self.play(*all_anims)
        # self.play(Wait(1))

        # subject_encoder = TaperingWeightEncoder(n=11, w=3)
        # for b in subject_encoder.bins:
        #     self.add_brick(b.lower, b.upper)
        # self.play(Wait(1))
        # all_anims = []
        # for cell_i in range(self.curr_id):
        #     diff_anims = self.split_brick(cell_i)
        #     if len(diff_anims) > 0:
        #         all_anims += diff_anims
        # if len(all_anims) > 0:
        #     self.play(*all_anims)
        # self.play(Wait(1))

        # subject_encoder = FixedWeightEncoder(n=11, w=3)
        # for b in subject_encoder.bins:
        #     self.add_brick(b.lower, b.upper)
        # self.play(Wait(1))
        # all_anims = []
        # for cell_i in range(self.curr_id):
        #     diff_anims = self.split_brick(cell_i)
        #     if len(diff_anims) > 0:
        #         all_anims += diff_anims
        # if len(all_anims) > 0:
        #     self.play(*all_anims)
        # self.play(Wait(1))

        # self.add_brick(0.15, 0.35)
        # self.add_brick(0.05, 0.3)
        # self.add_brick(0.15, 0.3)
        # self.add_brick(0.1, 0.2)
        # self.add_brick(0.2, 0.3)
        # self.add_brick(0.3, 0.4)
        # self.add_brick(0.1, 0.4)
        # self.play(Wait(1))
        # all_anims = []
        # for cell_i in range(self.curr_id):
        #     diff_anims = self.split_brick(cell_i)
        #     if len(diff_anims) > 0:
        #         all_anims += diff_anims
        # if len(all_anims) > 0:
        #     self.play(*all_anims)
        # self.play(Wait(1))

        # self.drop_brick(0.15, 0.35)
        # self.drop_brick(0.05, 0.3)
        # self.drop_brick(0.15, 0.3)
        # self.drop_brick(0.1, 0.2)
        # self.drop_brick(0.2, 0.3)
        # self.drop_brick(0.3, 0.4)
        # self.drop_brick(0.1, 0.4)
        # wait 1 second
        # self.play(Wait(1))
