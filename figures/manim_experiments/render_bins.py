from colour import Color
from manim import *
from manim import config as global_config
import numpy as np


# bin2.align_to(bin1, RIGHT)
# diff_bin = Difference(bin1, bin2, color=GREEN, stroke_width=stroke_width, stroke_color=stroke_color,
#                      fill_opacity=1)
# and_bin = Intersection(bin1, bin2, color=YELLOW, stroke_width=stroke_width, stroke_color=stroke_color,
#                       fill_opacity=1)
# and_parts = []
# for path in and_bin.get_subpaths():
#     and_parts.append(
#             Polygon(*path, color=YELLOW, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=1)
#     )
# NumberLine
# DEFAULT_ARROW_TIP_LENGTH: float = 0.35
# tip_width: float = DEFAULT_ARROW_TIP_LENGTH,
# tip_height: float = DEFAULT_ARROW_TIP_LENGTH,
# font_size: float = 36,
#
# from manim import config as global_config
# config = global_config.copy()
# config.frame_y_radius
# config.frame_height

class RectangleSeparationExample(Scene):
    def construct(self):
        bin1 = Rectangle(color=RED, width=4, stroke_width=1, stroke_color=WHITE, fill_opacity=0.8)
        bin1.move_to([-4, 0, 0])

        bin2 = Rectangle(color=BLUE, width=1, stroke_width=1, stroke_color=WHITE, fill_opacity=0.8)
        bin2.move_to(bin1.get_center())
        # bin2.shift(UP * 0.5)

        stroke_width = bin1.get_stroke_width()
        stroke_color = bin1.get_stroke_color()

        # section that is removed
        and_bin = Intersection(bin1, bin2)
        and_bin.shift(RIGHT * 8)
        and_parts = [
                Polygon(*path, color=RED, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
                for path in and_bin.get_subpaths()]

        # section that remains
        diff_bin = Difference(bin1, bin2)
        diff_bin.shift(RIGHT * 8)
        diff_parts = [
                Polygon(*path, color=RED, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
                for path in diff_bin.get_subpaths()]

        self.add(bin1, bin2)
        self.add(*diff_parts)
        self.add(*and_parts)


class BrickSplitExample(Scene):

    # brick1 red, remains stationary
    # brick2 blue, falls from above
    # on contact with brick1, brick2 separates into components from brick1 intersection/difference
    # intersected components stop falling and remain on top of brick1
    # difference components keep falling and stop at same level as brick1

    def construct(self):
        stroke_width = 1
        stroke_color = WHITE

        brick1 = Rectangle(color=RED, width=4, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
        brick1.move_to([0, -2, 0])
        # brick2 = Rectangle(color=BLUE, width=4, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
        # brick2.move_to([1, 2, 0])
        brick2 = Rectangle(color=BLUE, width=6, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
        brick2.move_to([0, 2, 0])

        # brick fall
        self.add(brick1, brick2)
        target_point = brick1.get_top()
        point_to_align = brick2.get_bottom()
        # self.play(brick2.animate(rate_func=rate_functions.ease_in_circ).shift((target_point - point_to_align)*UP))
        self.play(brick2.animate(rate_func=rate_functions.rush_into).shift((target_point - point_to_align) * UP))

        # change brick
        self.remove(brick2)
        brick3 = brick2.copy()
        brick3.move_to(brick1, coor_mask=UP)

        # section that is removed
        and_bin = Intersection(brick1, brick3)
        and_parts = [
                Polygon(*path, color=BLUE, stroke_width=stroke_width,
                        stroke_color=stroke_color, fill_opacity=0.8).move_to(brick2, coor_mask=UP)
                # stroke_color=stroke_color, fill_opacity=0.8).move_to(brick2, coor_mask=UP)
                for path in and_bin.get_subpaths()
        ]

        # section that remains
        diff_bin = Difference(brick3, brick1)
        diff_parts = [
                Polygon(*path, color=BLUE, stroke_width=stroke_width,
                        stroke_color=stroke_color, fill_opacity=0.8).move_to(brick2, coor_mask=UP)
                for path in diff_bin.get_subpaths()
        ]

        self.add(*diff_parts)
        self.add(*and_parts)

        # fall to bottom
        # diff_anims = [part.animate(rate_func=rate_functions.ease_out_circ).shift((target_point - point_to_align) * UP) for part in diff_parts]
        diff_anims = [part.animate(rate_func=rate_functions.rush_from).shift((target_point - point_to_align) * UP) for
                      part in diff_parts]
        self.play(*diff_anims)

        # rate_functions

        # rate_functions.linear
        # rate_func=rate_functions.ease_in_sine

        diff_anims = [part.animate.shift((target_point - point_to_align) * DOWN) for part in diff_parts]
        and_anims = [part.animate.shift((target_point - point_to_align) * DOWN) for part in and_parts]

        self.play(*diff_anims, *and_anims)
        # for part in diff_parts:
        #     self.play(part.animate.shift((target_point - point_to_align)*DOWN))
        #
        # for part in and_parts:
        #     self.play(part.animate.shift((target_point - point_to_align)*DOWN))

        # brick3.set_color(GREEN)
        # self.add(brick3)

        # brick rise
        # self.play(brick3.animate.shift((target_point - point_to_align)*DOWN))

        # self.play(brick2.animate.to_edge(brick1, UP, buff=0))
        # self.play(brick2.animate.next_to(brick1, UP, buff=0))
        # self.play(brick2.animate.next_to(brick1, UP, buff=0))
        # self.play(brick2.animate.set_y(brick1.get_top()[1]))

        # target_point = target_aligner.get_critical_point(aligned_edge + direction)
        # point_to_align = aligner.get_critical_point(aligned_edge - direction)
        # self.shift((target_point - point_to_align + buff * direction) * coor_mask)

        # brick2.move_to(brick1.get_top())

        # self.play(Create(s))
        # self.play(s.animate.shift(RIGHT).scale(2).rotate(PI / 2))
        # self.play(Uncreate(s))

        # section that is removed
        # and_bin = Intersection(bin1, bin2)
        # and_bin.shift(RIGHT * 8)
        # and_parts = [
        #         Polygon(*path, color=RED, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
        #         for path in and_bin.get_subpaths()]

        # section that remains
        # diff_bin = Difference(bin1, bin2)
        # diff_bin.shift(RIGHT * 8)
        # diff_parts = [
        #         Polygon(*path, color=RED, stroke_width=stroke_width, stroke_color=stroke_color, fill_opacity=0.8)
        #         for path in diff_bin.get_subpaths()]

        # self.add(*diff_parts)
        # self.add(*and_parts)


class SingleLevelTetrisBricksExample(Scene):

    # brick1 red, remains stationary
    # brick2 blue, falls from above
    # on contact with brick1, brick2 separates into components from brick1 intersection/difference
    # intersected components stop falling and remain on top of brick1
    # difference components keep falling and stop at same level as brick1

    def create_textbox(self, string, *args, **kwargs):
        result = VGroup()
        box = Rectangle(*args, **kwargs)
        text = Text(string).move_to(box.get_center())
        result.add(box, text)
        return result

    def intersect(self, rvg1, rvg2):

        poly1 = rvg1.submobjects[0]
        poly2 = rvg2.submobjects[0]

        text1 = rvg1.submobjects[1]

        poly1_params = {
                "fill_opacity": poly1.fill_opacity,
                "stroke_width": poly1.stroke_width,
                "fill_color": poly1.fill_color,
                "stroke_color": poly1.stroke_color
        }

        and_bin = Intersection(poly1, poly2)
        and_parts = [VGroup(Polygon(*path, **poly1_params))
                     for path in and_bin.get_subpaths()
                     ]
        for part in and_parts:
            part.add(text1.copy().move_to(part.get_center()))

        return and_parts

    def difference(self, rvg1, rvg2):

        poly1 = rvg1.submobjects[0]
        poly2 = rvg2.submobjects[0]

        text1 = rvg1.submobjects[1]

        poly1_params = {
                "fill_opacity": poly1.fill_opacity,
                "stroke_width": poly1.stroke_width,
                "fill_color": poly1.fill_color,
                "stroke_color": poly1.stroke_color
        }

        diff_bin = Difference(poly1, poly2)
        diff_parts = [VGroup(Polygon(*path, **poly1_params))
                      for path in diff_bin.get_subpaths()
                      ]
        for part in diff_parts:
            part.add(text1.copy().move_to(part.get_center()))

        return diff_parts

    def construct(self):
        stroke_width = 1
        stroke_color = WHITE
        # unit height
        uh = 0.5

        # unit time
        ut = 0.5

        nl = NumberLine(
                x_range=[0, 1, 0.2],
                length=10,
                include_tip=True,
                tip_width=0.25,
                tip_height=0.2,
                include_numbers=True,
                font_size=32,
                stroke_width=4
        ).align_on_border(DOWN, buff=0.15)
        self.add(nl)

        floor_line = Rectangle(color=LIGHT_BROWN,
                               width=global_config.frame_width,
                               height=0.05,
                               stroke_width=0,
                               fill_opacity=0.8
                               ).align_on_border(DOWN, buff=1)
        self.add(floor_line)

        # first brick on floor
        brick1 = self.create_textbox("0", color=RED, width=4, height=uh, stroke_width=stroke_width,
                                     stroke_color=stroke_color, fill_opacity=0.8)

        brick1.next_to(floor_line, UP, buff=0)
        self.add(brick1)

        # second brick in sky
        brick2 = self.create_textbox("1", color=BLUE, width=6, height=uh, stroke_width=stroke_width,
                                     stroke_color=stroke_color, fill_opacity=0.8)
        self.add(brick2)

        # brick2 falls to next level
        target_point = brick1.get_top()
        point_to_align = brick2.get_bottom()

        # compute fall distance to scale running time
        fall_dist1 = np.linalg.norm(UP * (target_point - point_to_align))

        # falling with ease_in_sine as rate_func
        self.play(brick2.animate(rate_func=rate_functions.ease_in_sine, run_time=ut * fall_dist1).shift(
                (target_point - point_to_align) * UP))

        # create temporary brick to perform diff/intersect comparisons
        tmp_brick = brick2.copy()
        tmp_brick.move_to(brick1, coor_mask=UP)

        # section that is stopped, stays above brick1
        and_parts = self.intersect(tmp_brick, brick1)
        for part in and_parts:
            part.move_to(brick2, coor_mask=UP)

        # section that keeps falling, falls down to brick1 level
        diff_parts = self.difference(tmp_brick, brick1)
        for part in diff_parts:
            part.move_to(brick2, coor_mask=UP)

        # remove old brick and replace with its separated parts
        self.remove(brick2)
        self.add(*and_parts, *diff_parts)

        # splitting parts fall to next level, rate_func is ease_out_sine on impact with floor
        target_point = brick1.get_bottom()
        point_to_align = tmp_brick.get_top()

        # compute fall distance to scale running time
        fall_dist2 = np.linalg.norm(UP * (target_point - point_to_align))

        diff_anims = [
                part.animate(rate_func=rate_functions.ease_out_sine, run_time=ut * fall_dist2).shift(
                        (target_point - point_to_align) * UP) for
                part in diff_parts]
        self.play(*diff_anims)

        # wait 1 second
        self.play(Wait(1))


class TetrisBricksExample(Scene):
    stroke_width = 1
    stroke_color = WHITE

    # brick height and font size
    uh = 0.5
    font_size = 24

    # unit time
    ut = 0.5

    def create_textbox(self, string, *args, **kwargs):
        result = VGroup()
        box = Rectangle(*args, **kwargs)
        text = Text(string, font_size=self.font_size).move_to(box.get_center())
        result.add(box, text)
        return result

    @staticmethod
    def intersect(rvg1, rvg2):

        poly1 = rvg1.submobjects[0]
        poly2 = rvg2.submobjects[0]

        text1 = rvg1.submobjects[1]

        poly1_params = {
                "fill_opacity": poly1.fill_opacity,
                "stroke_width": poly1.stroke_width,
                "fill_color": poly1.fill_color,
                "stroke_color": poly1.stroke_color
        }

        and_bin = Intersection(poly1, poly2)
        and_parts = [VGroup(Polygon(*path, **poly1_params))
                     for path in and_bin.get_subpaths()
                     ]
        for part in and_parts:
            part.add(text1.copy().move_to(part.get_center()))

        return and_parts

    @staticmethod
    def difference(rvg1, rvg2):

        poly1 = rvg1.submobjects[0]
        poly2 = rvg2.submobjects[0]

        text1 = rvg1.submobjects[1]

        poly1_params = {
                "fill_opacity": poly1.fill_opacity,
                "stroke_width": poly1.stroke_width,
                "fill_color": poly1.fill_color,
                "stroke_color": poly1.stroke_color
        }

        diff_bin = Difference(poly1, poly2)
        diff_parts = [VGroup(Polygon(*path, **poly1_params))
                      for path in diff_bin.get_subpaths()
                      ]
        for part in diff_parts:
            part.add(text1.copy().move_to(part.get_center()))

        return diff_parts

    def drop(self, static_group, *falling_parts: Mobject):
        """

        Static Group:  set of polygrams that have settled to ground
        Falling Group:  set of polygrams that fall a level at a time,
                        contact, split, and add to static group

        Steps
        1) fall all parts until contact level
        2) is this the bottom?  If so quit, otherwise continue
        for each falling part, do #3, #4, #5
        3) intersect with union of parts a unit height below
        4) split shape into falling parts and static parts
        5) add static parts to new static group, add falling parts to new falling group
        6) merge old static group with new static group
        7) go to #1 with new static and falling group

        :param static_group:
        :param falling_parts:
        :return:
        """

        brick2 = falling_parts[0]

        # top and bottom of level falling to
        curr_level_top = static_group.get_top()
        curr_level_bottom = static_group.get_bottom()

        # brick2 falls to next level
        brick_bottom = brick2.get_bottom()

        # compute fall distance to scale running time
        fall_dist1 = np.linalg.norm(UP * (curr_level_top - brick_bottom))

        # falling with ease_in_sine as rate_func
        self.play(brick2.animate(rate_func=rate_functions.ease_in_sine, run_time=self.ut * fall_dist1).shift(
                (curr_level_top - brick_bottom) * UP))

        # create temporary brick to perform diff/intersect comparisons
        tmp_brick = brick2.copy()
        tmp_brick.move_to(static_group, coor_mask=UP)

        # section that is stopped, stays above static_group
        and_parts = self.intersect(tmp_brick, static_group)
        for part in and_parts:
            part.move_to(brick2, coor_mask=UP)

        # section that keeps falling, falls down to static_group level
        diff_parts = self.difference(tmp_brick, static_group)
        for part in diff_parts:
            part.move_to(brick2, coor_mask=UP)

        # remove old brick and replace with its separated parts
        self.remove(brick2)
        self.add(*and_parts, *diff_parts)

        # splitting parts fall to next level, rate_func is ease_out_sine on impact with floor
        brick_bottom = tmp_brick.get_top()

        # compute fall distance to scale running time
        fall_dist2 = np.linalg.norm(UP * (curr_level_bottom - brick_bottom))

        diff_anims = [
                part.animate(rate_func=rate_functions.ease_out_sine, run_time=self.ut * fall_dist2).shift(
                        (curr_level_bottom - brick_bottom) * UP) for
                part in diff_parts]
        self.play(*diff_anims)

        # wait 1 second
        self.play(Wait(1))




    def construct(self):

        nl = NumberLine(
                x_range=[0, 1, 0.2],
                length=10,
                include_tip=True,
                tip_width=0.25,
                tip_height=0.2,
                include_numbers=True,
                font_size=32,
                stroke_width=4
        ).align_on_border(DOWN, buff=0.15)
        self.add(nl)

        floor_line = Rectangle(color=LIGHT_BROWN,
                               width=global_config.frame_width,
                               height=0.05,
                               stroke_width=0,
                               fill_opacity=0.8
                               ).align_on_border(DOWN, buff=1)
        self.add(floor_line)

        # first brick on floor
        brick1 = self.create_textbox("0", color=RED, width=4, height=self.uh, stroke_width=self.stroke_width,
                                     stroke_color=self.stroke_color, fill_opacity=0.8)

        brick1.next_to(floor_line, UP, buff=0)
        self.add(brick1)

        # second brick in sky
        brick2 = self.create_textbox("1", color=BLUE, width=6, height=self.uh,
                                     stroke_width=self.stroke_width,
                                     stroke_color=self.stroke_color, fill_opacity=0.8)
        self.add(brick2)


        # drop brick2 on brick1
        self.drop(brick1, brick2)

        return

        # brick2 falls to next level
        target_point = brick1.get_top()
        point_to_align = brick2.get_bottom()

        # compute fall distance to scale running time
        fall_dist1 = np.linalg.norm(UP * (target_point - point_to_align))

        # falling with ease_in_sine as rate_func
        self.play(brick2.animate(rate_func=rate_functions.ease_in_sine, run_time=self.ut * fall_dist1).shift(
                (target_point - point_to_align) * UP))

        # create temporary brick to perform diff/intersect comparisons
        tmp_brick = brick2.copy()
        tmp_brick.move_to(brick1, coor_mask=UP)

        # section that is stopped, stays above brick1
        and_parts = self.intersect(tmp_brick, brick1)
        for part in and_parts:
            part.move_to(brick2, coor_mask=UP)

        # section that keeps falling, falls down to brick1 level
        diff_parts = self.difference(tmp_brick, brick1)
        for part in diff_parts:
            part.move_to(brick2, coor_mask=UP)

        # remove old brick and replace with its separated parts
        self.remove(brick2)
        self.add(*and_parts, *diff_parts)

        # splitting parts fall to next level, rate_func is ease_out_sine on impact with floor
        target_point = brick1.get_bottom()
        point_to_align = tmp_brick.get_top()

        # compute fall distance to scale running time
        fall_dist2 = np.linalg.norm(UP * (target_point - point_to_align))

        diff_anims = [
                part.animate(rate_func=rate_functions.ease_out_sine, run_time=self.ut * fall_dist2).shift(
                        (target_point - point_to_align) * UP) for
                part in diff_parts]
        self.play(*diff_anims)


        # third brick in sky
        brick3 = self.create_textbox("2", color=GREEN, width=8, height=self.uh,
                                     stroke_width=self.stroke_width,
                                     stroke_color=self.stroke_color, fill_opacity=0.8)
        self.add(brick3)




        # wait 1 second
        self.play(Wait(1))
