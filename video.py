import math
from manimlib import *

ACCENT_COLOR = '#66cb51'
SECONDARY_COLOR = '#be2540'
TERTIARY_COLOR = '#ffffff'

class PascalTriangle:
    def __init__(self, number_scale=2):
        self.group = VGroup()
        self.number_scale = number_scale
    
    def calculate_collumn(self, row, col):
        return int(math.factorial(row)/(math.factorial(col)*math.factorial(row-col)))

    def focus_on(self, row):
        self.focused_on = self.group.submobjects[row]
        self.original_focused_on = self.focused_on.copy()
        return [FadeOut(_) for _ in self.group.submobjects if _ != self.focused_on]

    def unfocus(self):
        animations = [*(FadeIn(_) for _ in self.group.submobjects if _ != self.focused_on), Transform(self.focused_on, self.original_focused_on)]
        self.focused_on = None
        self.original_focused_on = None
        return animations

    def generate_next_row(self):
        current_row = len(self.group.submobjects) - 1
        next_row = current_row + 1
        next_row_group = VGroup()
        for col in range(next_row + 1):
            collumn_value = self.calculate_collumn(next_row, col)
            collumn = Tex(str(collumn_value))
            collumn.set_color(ACCENT_COLOR)
            collumn.scale(self.number_scale)
            if col > 0:
                collumn.move_to(next_row_group[col - 1]).shift(RIGHT * 2)
            next_row_group.add(collumn)
        if current_row == -1:
            next_row_group.move_to(ORIGIN)
        else:
            current_row_group = self.group[current_row]
            next_row_group.next_to(current_row_group, DOWN)
        self.group.add(next_row_group)
    
    def generate(self, up_to):
        self.group = VGroup()
        for _ in range(up_to + 1):
            self.generate_next_row()
        self.group.move_to(ORIGIN)

# adapted code from itertools
def find_choices(options, choices):
    # find_choices(VGroup(A, B, C, D), 2) --> VGroup(VGroup(A, B), VGroup(A, C), VGroup(A, D), VGroup(B, C), VGroup(B, D), VGroup(C, D))
    # where every choice is a copy of the original object
    pool = options.submobjects
    n = len(pool)
    if choices > n:
        return
    indices = list(range(choices))
    combinations = VGroup(VGroup(*(pool[i].copy() for i in indices)))
    while True:
        for i in reversed(range(choices)):
            if indices[i] != i + n - choices:
                break
        else:
            return combinations
        indices[i] += 1
        for j in range(i+1, choices):
            indices[j] = indices[j-1] + 1
        combinations.add(VGroup(*(pool[i].copy() for i in indices)))

class Presentation(Scene):
    def find_pairs_from_row(self, row):
        triangle_row = self.triangle.submobjects[row - 1]
        pairs = []
        for i, col in enumerate(triangle_row.submobjects):
            if i < len(triangle_row.submobjects) - 1:
                next_col = triangle_row.submobjects[i + 1]
                pairs.append(VGroup(col, next_col))
        return pairs

    def create_next_row(self, total_run_time=1):
        current_row = len(self.triangle.submobjects)
        next_row = current_row + 1
        next_row_index = next_row - 1
        above_pairs = self.find_pairs_from_row(current_row)
        next_row_group = VGroup()
        collumn_tex_scale = 2
        for col, pair in enumerate(above_pairs):
            collumn_value = int(math.factorial(next_row)/(math.factorial(col + 1)*math.factorial(next_row - col - 1)))
            collumn = Tex(str(collumn_value))
            collumn.set_color(ACCENT_COLOR)
            collumn.scale(collumn_tex_scale)
            if col > 0:
                collumn.move_to(next_row_group[col - 1]).shift(RIGHT * 2)
            else:
                collumn.next_to(pair, DOWN)
            next_row_group.add(collumn)
            self.play(TransformFromCopy(pair, collumn), run_time = total_run_time / (next_row_index+2))
        first_one = Tex('1')
        first_one.set_color(ACCENT_COLOR)
        first_one.scale(collumn_tex_scale)
        first_one.move_to(next_row_group.submobjects[0])
        first_one.shift(LEFT * 2)
        second_one = Tex('1')
        second_one.set_color(ACCENT_COLOR)
        second_one.scale(collumn_tex_scale)
        last_col = next_row_group.submobjects[len(next_row_group.submobjects) - 1]
        second_one.move_to(last_col)
        second_one.shift(RIGHT * 2)
        next_row_group.add_to_back(first_one)
        next_row_group.add(second_one)
        self.play(FadeIn(first_one), FadeIn(second_one))
        self.triangle.add(next_row_group)

    def construct(self):
        one = Tex('1').set_color(ACCENT_COLOR).scale(2)
        self.play(Write(one))
        self.wait()
        second_one = one.copy()

        first_row = VGroup(one, second_one)

        self.add(second_one)
        self.play(second_one.animate.shift(RIGHT), one.animate.shift(LEFT))
        self.wait()

        self.triangle = VGroup(first_row)

        self.create_next_row(2)
        self.wait()
        self.create_next_row(2)
        self.wait()
        self.create_next_row()
        self.play(self.triangle.animate.to_edge(UP))

class NChooseK(Scene):
    def construct(self):
        self.ptriangle = PascalTriangle()
        self.ptriangle.generate(4)
        self.ptriangle.group.remove(self.ptriangle.group.submobjects[0])
        self.ptriangle.group.to_edge(UP)
        self.add(self.ptriangle.group)
        self.wait(2)
        
        self.play(*self.ptriangle.focus_on(2))
        self.square = Square(1).set_stroke(SECONDARY_COLOR)
        self.circle = Circle().scale(0.5).set_stroke(SECONDARY_COLOR)
        self.triangle = Triangle().scale(0.65).set_stroke(SECONDARY_COLOR)
        self.square.next_to(self.circle, LEFT)
        self.triangle.next_to(self.circle, RIGHT)
        self.object_choose_group = VGroup(self.square, self.circle, self.triangle)
        self.play(self.ptriangle.focused_on.animate.to_edge(UP), ShowCreation(self.object_choose_group))
        self.play(self.object_choose_group.animate.next_to(self.ptriangle.focused_on, DOWN, 0.5))
        self.wait(2)

        self.separator_line = Line(LEFT * 10, RIGHT * 10).set_color(TERTIARY_COLOR).next_to(self.object_choose_group, DOWN, 0.4)

        self.play(ShowCreation(self.separator_line), run_time=2)

        self.choose_1 = self.object_choose_group.copy()
        self.choose_1.move_to(ORIGIN)
        self.choose_1.space_out_submobjects(1.5)
        self.choose_1_arrow = Arrow(self.choose_1.get_edge_center(RIGHT), self.choose_1.get_edge_center(RIGHT) + RIGHT * 2).set_color(TERTIARY_COLOR).to_edge(RIGHT).shift(LEFT/2)
        self.choose_1_result = Tex('3').set_color(ACCENT_COLOR).scale(2).next_to(self.choose_1_arrow, RIGHT)

        self.play(TransformFromCopy(self.object_choose_group, self.choose_1), FadeIn(self.choose_1_arrow), TransformFromCopy(self.ptriangle.focused_on.submobjects[1], self.choose_1_result), run_time=1.5)

        self.wait(2)

        self.choose_2 = VGroup(VGroup(self.square.copy(), self.circle.copy()), VGroup(self.square.copy(), self.triangle.copy()), VGroup(self.circle.copy(), self.triangle.copy()))
        for i, choice in enumerate(self.choose_2.submobjects):
            if i > 0:
                last_choice = self.choose_2.submobjects[i - 1]
                choice.next_to(last_choice, RIGHT)
            else:
                choice.move_to(ORIGIN)
            choice.submobjects[1].next_to(choice.submobjects[0], RIGHT)
        self.choose_2.space_out_submobjects(1.1)
        self.choose_2.move_to(ORIGIN)
        self.choose_2.shift(DOWN * 1.5)
        self.choose_2_arrow = Arrow(self.choose_2.get_edge_center(RIGHT), self.choose_2.get_edge_center(RIGHT) + RIGHT * 2).set_color(TERTIARY_COLOR).to_edge(RIGHT).shift(LEFT/2)
        self.choose_2_result = Tex('3').set_color(ACCENT_COLOR).scale(2).next_to(self.choose_2_arrow, RIGHT)

        self.play(TransformFromCopy(self.object_choose_group, self.choose_2), FadeIn(self.choose_2_arrow), TransformFromCopy(self.ptriangle.focused_on.submobjects[2], self.choose_2_result), run_time=3)

        self.wait(2)

        self.choose_3 = self.object_choose_group.copy()
        self.choose_3.move_to(ORIGIN)
        self.choose_3.shift(DOWN * 3)
        self.choose_3_arrow = Arrow(self.choose_3.get_edge_center(RIGHT), self.choose_3.get_edge_center(RIGHT) + RIGHT * 2).set_color(TERTIARY_COLOR).to_edge(RIGHT).shift(LEFT/2)
        self.choose_3_result = Tex('1').set_color(ACCENT_COLOR).scale(2).next_to(self.choose_3_arrow, RIGHT)

        self.play(TransformFromCopy(self.object_choose_group, self.choose_3), FadeIn(self.choose_3_arrow), TransformFromCopy(self.ptriangle.focused_on.submobjects[3], self.choose_3_result), run_time=3)

        self.wait(2)

        self.play(Indicate(self.choose_1_result), Indicate(self.ptriangle.focused_on.submobjects[1]))
        self.play(Indicate(self.choose_2_result), Indicate(self.ptriangle.focused_on.submobjects[2]))
        self.play(Indicate(self.choose_3_result), Indicate(self.ptriangle.focused_on.submobjects[3]))


        self.wait(3)

        self.play(*self.ptriangle.unfocus(), FadeOut(self.choose_1), FadeOut(self.choose_2), FadeOut(self.choose_3), FadeOut(self.choose_1_arrow), FadeOut(self.choose_2_arrow), FadeOut(self.choose_3_arrow), FadeOut(self.choose_1_result), FadeOut(self.choose_2_result), FadeOut(self.choose_3_result), FadeOut(self.separator_line), FadeOut(self.object_choose_group))

class NChooseKRelationProof(Scene):
    def construct(self):
        self.ptriangle = PascalTriangle()
        self.ptriangle.generate(4)
        # self.ptriangle.group.remove(self.ptriangle.group.submobjects[0])
        self.ptriangle.group.submobjects[0].set_opacity(0)
        self.ptriangle.group.to_edge(UP)
        self.ptriangle.group.shift(UP * 1.25)
        self.add(self.ptriangle.group)

        self.wait(4)

        self.square = Square(1).set_stroke(SECONDARY_COLOR)
        self.circle = Circle().scale(0.5).set_stroke(SECONDARY_COLOR)
        self.triangle = Triangle().scale(0.65).set_stroke(SECONDARY_COLOR)
        self.pentagon = RegularPolygon(5).scale(0.5).set_stroke(SECONDARY_COLOR)
        self.square.next_to(self.circle, LEFT)
        self.triangle.next_to(self.circle, RIGHT)
        self.pentagon.next_to(self.triangle, RIGHT)
        self.objects_to_choose = VGroup(self.square, self.circle, self.triangle, self.pentagon)
        self.objects_to_choose.to_corner(RIGHT + DOWN)
        self.play(ShowCreation(self.objects_to_choose))

        self.wait(3)

        self.choose_2 = find_choices(self.objects_to_choose, 2)
        for i, choice in enumerate(self.choose_2.submobjects):
            for j, object in enumerate(choice.submobjects):
                if j > 0:
                    last_object = choice.submobjects[j - 1]
                    object.next_to(last_object, RIGHT)
                else:
                    object.move_to(ORIGIN)
            if i > 0:
                last_choice = self.choose_2.submobjects[i - 1]
                choice.next_to(last_choice, RIGHT)
            else:
                choice.move_to(ORIGIN)
        self.choose_2.space_out_submobjects(1.1)
        self.choose_2.move_to(ORIGIN)
        self.choose_2.shift(DOWN)
        self.choose_2.scale(0.5)
        self.play(TransformFromCopy(self.objects_to_choose, self.choose_2))

        self.wait(2)

        self.play(Indicate(self.choose_2), Indicate(self.ptriangle.group.submobjects[4].submobjects[2]))

        self.wait(3)

        self.play(
            Indicate(VGroup(
                self.choose_2.submobjects[0].submobjects[0], 
                self.choose_2.submobjects[1].submobjects[0],
                self.choose_2.submobjects[2].submobjects[0],
                self.ptriangle.group.submobjects[3].submobjects[1]
            ))
        )
        
        self.wait(2)
        
        self.play(
            Indicate(VGroup(
                self.choose_2.submobjects[3].submobjects[0], 
                self.choose_2.submobjects[4].submobjects[0],
                self.ptriangle.group.submobjects[2].submobjects[1]
            ))
        )
        
        self.wait(2)
        
        self.play(
            Indicate(VGroup(
                self.choose_2.submobjects[5].submobjects[0],
                self.ptriangle.group.submobjects[1].submobjects[1]
            ))
        )

        self.wait(3)

        self.play(
            TransformFromCopy(VGroup(
                self.ptriangle.group.submobjects[3].submobjects[1],
                self.ptriangle.group.submobjects[3].submobjects[2]
            ), self.ptriangle.group.submobjects[4].submobjects[2].copy())
        )

        self.wait(2)

        self.play(
            TransformFromCopy(VGroup(
                self.ptriangle.group.submobjects[2].submobjects[1], 
                self.ptriangle.group.submobjects[2].submobjects[2]
            ), self.ptriangle.group.submobjects[3].submobjects[2].copy())
        )

        self.wait(2)

        self.play(
            TransformFromCopy(VGroup(
                self.ptriangle.group.submobjects[3].submobjects[1],
                self.ptriangle.group.submobjects[2].submobjects[1], 
                self.ptriangle.group.submobjects[2].submobjects[2]
            ), self.ptriangle.group.submobjects[4].submobjects[2].copy())
        )

        self.wait(2)

        self.play(
            Indicate(VGroup(
                self.ptriangle.group.submobjects[1].submobjects[1],
                self.ptriangle.group.submobjects[2].submobjects[2]
            ))
        )

        self.wait(2)

        self.play(
            TransformFromCopy(VGroup(
                self.ptriangle.group.submobjects[3].submobjects[1],
                self.ptriangle.group.submobjects[2].submobjects[1], 
                self.ptriangle.group.submobjects[1].submobjects[1]
            ), self.ptriangle.group.submobjects[4].submobjects[2].copy())
        )

        self.wait(2)

        self.ptriangle.generate_next_row()
        self.hexagon = RegularPolygon(6).scale(0.5).set_stroke(SECONDARY_COLOR)
        self.hexagon.next_to(self.objects_to_choose, RIGHT)
        self.objects_to_choose.add(self.hexagon)
        self.play(self.objects_to_choose.animate.shift(LEFT))
        self.choose_2_other = find_choices(self.objects_to_choose, 2)
        for i, choice in enumerate(self.choose_2_other.submobjects):
            for j, object in enumerate(choice.submobjects):
                if j > 0:
                    last_object = choice.submobjects[j - 1]
                    object.next_to(last_object, RIGHT)
                else:
                    object.move_to(ORIGIN)
            if i > 0:
                last_choice = self.choose_2_other.submobjects[i - 1]
                choice.next_to(last_choice, RIGHT)
            else:
                choice.move_to(ORIGIN)
        self.choose_2_other.space_out_submobjects(1.2)
        self.choose_2_other.move_to(ORIGIN)
        self.choose_2_other.shift(DOWN * 1.3)
        self.choose_2_other.scale(0.43)
        self.play(GrowFromCenter(self.ptriangle.group.submobjects[len(self.ptriangle.group.submobjects) - 1]), TransformMatchingParts(self.choose_2, self.choose_2_other))

        self.wait(2)

        self.play(Indicate(self.choose_2_other), Indicate(self.ptriangle.group.submobjects[5][2]))

        self.wait(2)

        self.play(
            Indicate(VGroup(
                self.choose_2_other.submobjects[0].submobjects[0], 
                self.choose_2_other.submobjects[1].submobjects[0],
                self.choose_2_other.submobjects[2].submobjects[0],
                self.choose_2_other.submobjects[3].submobjects[0],
                self.ptriangle.group.submobjects[4].submobjects[1]
            ))
        )

        self.wait(2)

        self.play(
            Indicate(VGroup(
                self.choose_2_other.submobjects[4].submobjects[0], 
                self.choose_2_other.submobjects[5].submobjects[0],
                self.choose_2_other.submobjects[6].submobjects[0],
                self.ptriangle.group.submobjects[3].submobjects[1]
            ))
        )

        self.wait(2)

        self.play(
            Indicate(VGroup(
                self.choose_2_other.submobjects[7].submobjects[0], 
                self.choose_2_other.submobjects[8].submobjects[0],
                self.ptriangle.group.submobjects[2].submobjects[1]
            ))
        )

        self.wait(2)

        self.play(
            Indicate(VGroup(
                self.choose_2_other.submobjects[9].submobjects[0],
                self.ptriangle.group.submobjects[1].submobjects[1]
            ))
        )

        self.wait(2)

        self.play(TransformFromCopy(VGroup(
            self.ptriangle.group.submobjects[1].submobjects[1],
            self.ptriangle.group.submobjects[2].submobjects[1],
            self.ptriangle.group.submobjects[3].submobjects[1],
            self.ptriangle.group.submobjects[4].submobjects[1],
        ), self.ptriangle.group.submobjects[5].submobjects[2].copy()))

        self.wait(3)

        self.play(FadeOut(self.objects_to_choose), FadeOut(self.choose_2_other))

class RowSums(Scene):
    def construct(self):
        self.ptriangle = PascalTriangle()
        self.ptriangle.generate(5)
        # self.ptriangle.group.remove(self.ptriangle.group.submobjects[0])
        self.ptriangle.group.submobjects[0].set_opacity(0)
        self.ptriangle.group.to_edge(UP)
        self.ptriangle.group.shift(UP * 1.25)
        self.add(self.ptriangle.group)

        self.wait(5)

        power_2_s = VGroup()
        for i, row in enumerate(self.ptriangle.group.submobjects):
            if i > 0:
                self.play(row.animate.to_edge(LEFT))
                result_arrow = Arrow(row.get_edge_center(RIGHT), row.get_edge_center(RIGHT) + RIGHT * 2).set_color(TERTIARY_COLOR)
                result = Tex(str(2**i)).set_color(SECONDARY_COLOR).next_to(result_arrow, RIGHT).scale(1.5)
                power_2 = VGroup(result_arrow, result)
                power_2_s.add(power_2)
                power_2.to_edge(RIGHT)
                self.play(GrowFromCenter(result_arrow), TransformFromCopy(row, result))
        etcetera = Tex(r'\cdots', r'\text{?}').set_color(TERTIARY_COLOR).scale(2)
        etcetera.set_color_by_tex_to_color_map({
            r'\text{?}': ACCENT_COLOR
        })
        etcetera.next_to(power_2_s, DOWN, 2)
        self.play(GrowFromCenter(etcetera), GrowFromCenter(etcetera.copy().next_to(self.ptriangle.group.submobjects[5], DOWN, 2)))

        self.wait(3)

        self.play(Indicate(power_2_s.submobjects[0]))

        self.wait(2)

        self.play(Indicate(power_2_s.submobjects[1]))

        self.wait(2)

        self.play(Indicate(power_2_s.submobjects[2]))

        self.wait(2)

        self.play(Indicate(power_2_s.submobjects[3]))

        self.wait(2)

        self.play(Indicate(power_2_s.submobjects[4]))

        self.wait(3)
        
        self.play(*(FadeOut(obj) for obj in self.mobjects))

class Ending(Scene):
    def find_pairs_from_row(self, row):
        triangle_row = self.triangle.submobjects[row - 1]
        pairs = []
        for i, col in enumerate(triangle_row.submobjects):
            if i < len(triangle_row.submobjects) - 1:
                next_col = triangle_row.submobjects[i + 1]
                pairs.append(VGroup(col, next_col))
        return pairs

    def create_next_row(self, total_run_time=1, scale=1):
        current_row = len(self.triangle.submobjects)
        next_row = current_row + 1
        next_row_index = next_row - 1
        above_pairs = self.find_pairs_from_row(current_row)
        next_row_group = VGroup()
        for col, pair in enumerate(above_pairs):
            collumn_value = int(math.factorial(next_row)/(math.factorial(col + 1)*math.factorial(next_row - col - 1)))
            collumn = Tex(str(collumn_value))
            collumn.set_color(ACCENT_COLOR)
            collumn.scale(2 * scale)
            if col > 0:
                collumn.move_to(next_row_group[col - 1]).shift(RIGHT * 2 * scale)
            else:
                collumn.next_to(pair, DOWN)
            next_row_group.add(collumn)
            self.play(TransformFromCopy(pair, collumn), run_time = total_run_time / (next_row_index+2))
        first_one = Tex('1')
        first_one.set_color(ACCENT_COLOR)
        first_one.scale(2 * scale)
        first_one.move_to(next_row_group.submobjects[0])
        first_one.shift(LEFT * 2 * scale)
        second_one = Tex('1')
        second_one.set_color(ACCENT_COLOR)
        second_one.scale(2 * scale)
        last_col = next_row_group.submobjects[len(next_row_group.submobjects) - 1]
        second_one.move_to(last_col)
        second_one.shift(RIGHT * 2 * scale)
        next_row_group.add_to_back(first_one)
        next_row_group.add(second_one)
        self.play(FadeIn(first_one), FadeIn(second_one))
        self.triangle.add(next_row_group)

    def construct(self):
        one = Tex('1').set_color(ACCENT_COLOR).scale(2)
        one.to_edge(UP)
        self.play(Write(one))
        self.wait()
        second_one = one.copy()

        first_row = VGroup(one, second_one)

        self.add(second_one)
        self.play(second_one.animate.shift(RIGHT), one.animate.shift(LEFT))
        self.wait()

        self.triangle = VGroup(first_row)

        self.create_next_row(1)
        self.wait()
        self.create_next_row(1)
        self.wait()
        self.create_next_row(1)
        self.play(self.triangle.animate.scale(0.5))
        self.play(self.triangle.animate.to_edge(UP))

        self.wait()
        self.create_next_row(0.5, 0.5)
        self.wait()
        self.create_next_row(0.5, 0.5)
        self.wait()
        self.create_next_row(0.5, 0.5)
        self.wait()

        self.play(self.triangle.animate.scale(0.7))
        self.play(self.triangle.animate.to_edge(UP))

        self.wait()
        self.create_next_row(0.35, 0.35)
        self.wait()
        self.create_next_row(0.35, 0.35)
        self.wait()
        self.create_next_row(0.35, 0.35)

class Thumbnail(Scene):
    def construct(self):
        self.triangle = PascalTriangle(3)
        self.triangle.generate(5)
        self.add(self.triangle.group)
