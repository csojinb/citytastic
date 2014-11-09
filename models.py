from rendering import draw_line
import mathutils
import math


class Road():
    __incrementing_road_id = 0

    def __init__(self, road_size=0, points=[]):
        self.road_size = road_size
        self.points = points
        self.id = self.__incrementing_road_id
        self.__incrementing_road_id += 1

    def draw(self):
        draw_line("road" + str(self.id), "curve" + str(self.id), self.points)


class Wanderer():
    def __init__(self):
        self.circle_radius = .5
        self.max_angle_change_per_delta = 5
        self.move_change_per_delta = 1
        self.rotation_angle_change_per_delta = 360
        self.offset_from_center = 1
        self.cur_angle = mathutils.noise.random() * 360        # random in degrees
        self.position = mathutils.Vector((0, 0, 0))
        self.forward = mathutils.Vector((1, 0, 0))

    def update(self, delta):
        point_on_circle = self._find_point_on_circle()

        turn_to = (point_on_circle - self.position).normalized()
        angle_between = math.degrees(self.forward.angle(turn_to))
        to_rotate_amount = angle_between    # max(min(1.0, self.rotation_angle_change_per_delta/angle_between), 0.0)

        self.forward = self.forward.slerp(turn_to, to_rotate_amount * delta)      # in this setup, the circle will turn independently of the person and they will just approach a single facing direction
        self.forward.normalize()

        self.position += self.forward * self.move_change_per_delta * delta

        self._update_circle_point(delta)

    def _find_point_on_circle(self):
        circle_center = self.position + self.forward * self.offset_from_center
        circle_point = mathutils.Vector((math.cos(self.cur_angle), math.sin(self.cur_angle), 0)) * self.circle_radius

        return circle_center + circle_point

    def _update_circle_point(self, delta):
        randomness = mathutils.noise.random() * 2 - 1
        self.cur_angle += randomness * self.max_angle_change_per_delta * delta


class Grid():
    def __init__(self, center, width, height):
        self.center = center
        self.width = width
        self.height = height

    def is_point_inside(self, point):
        to_position = point - self.center
        return (math.fabs(to_position.x) <= self.width and math.fabs(to_position.y) <= self.height)

    def draw(self):
        grid_points = [
            self.center + mathutils.Vector((-self.width, -self.height, 0)),
            self.center + mathutils.Vector((-self.width, self.height, 0)),
            self.center + mathutils.Vector((self.width, self.height, 0)),
            self.center + mathutils.Vector((self.width, -self.height, 0)),
            self.center + mathutils.Vector((-self.width, -self.height, 0))
        ]
        draw_line('grid', 'square', grid_points)


class HeatmapSquare():
    def __init__(self, center=None, value=None):
        self.center = center
        self.value = value


# has a set of points at the bottom and some at the top
# the plan is that they will have the same X/Y positions, as the bottom set
# however, the Z values for the tops of the buildings can be different heights to give more interesting shapes
class Building():
    def __init__(self):
        self.base_center
        self.width = 1
        self.height = 1     # NOT the height of the building, just trying to be consistent with the (width x height) used throughout the rest of the file
        self.self.depth = 10    # AKA building_height
        self.top_points = []
        self.bottom_points = []

    def generate_points(self):
        x_vec = mathutils.Vector((self.width, 0, 0))
        y_vec = mathutils.Vector((0, self.height, 0))
        self.top_points = [
            self.base_center + x_vec + y_vec,
            self.base_center + x_vec
        ]
