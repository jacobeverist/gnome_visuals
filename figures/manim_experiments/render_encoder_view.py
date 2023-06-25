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


class EncoderTetrisView(Scene):
    stroke_width = 1
    stroke_color = WHITE

    # brick height and font size
    uh = 0.5
    font_size = 24

    # unit time
    ut = 0.3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.encoder = PlaceCellEncoder()

        self.nl = NumberLine(
                x_range=[0, 1, 0.2],
                length=10,
                include_tip=True,
                tip_width=0.25,
                tip_height=0.2,
                include_numbers=True,
                font_size=32,
                stroke_width=4
        ).align_on_border(DOWN, buff=0.15)

        self.floor_line = Rectangle(color=Color(hex=LIGHT_BROWN),
                                    width=global_config.frame_width,
                                    height=0.05,
                                    stroke_width=0,
                                    fill_opacity=0.8
                                    ).align_on_border(DOWN, buff=0.95)

        # constant starting height
        self.ground_height = self.floor_line.get_top()[1]
        self.start_height = self.ground_height + 3

        self.levels = [self.ground_height + i * self.uh for i in range(11)]
        self.curr_id = 0

        self.whole_blocks = []
        self.sectioned_blocks = []
        self.section_weights = []
        self.section_levels = []

        self.colors = sns.color_palette("cet_glasbey_dark", as_cmap=True).colors
        # print(self.colors)

    def create_textbox(self, string, *args, **kwargs):
        result = VGroup()
        box = Rectangle(*args, **kwargs)
        text = Text(string, font_size=self.font_size).move_to(box.get_center())
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
            brick = brick_sections[brick_i]
            self.add(brick)

            section_brick_center = brick.get_center()

            section_start_level = target_level_height
            section_end_level = level_sections[brick_i]

            fall_dist2 = section_start_level - section_end_level
            section_end_point = RIGHT * section_brick_center + UP * section_end_level

            if fall_dist2 > 0:
                diff_anims.append(
                        brick.animate(rate_func=rate_functions.ease_out_sine, run_time=self.ut * fall_dist2).move_to(
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

    def construct(self):

        self.add(self.nl)
        self.add(self.floor_line)

        # subject_encoder = FixedWeightEncoder(n=11, w=3)
        #
        # for b in subject_encoder.bins:
        #     self.drop_brick(b.lower, b.upper)

        self.drop_brick(0.15, 0.35)
        self.drop_brick(0.05, 0.3)
        self.drop_brick(0.15, 0.3)
        self.drop_brick(0.1, 0.2)
        self.drop_brick(0.2, 0.3)
        self.drop_brick(0.3, 0.4)
        self.drop_brick(0.1, 0.4)
        # wait 1 second
        self.play(Wait(1))
