from rendering import draw_line
import mathutils
import math
import bpy


class Road():
    __incrementing_road_id = 0

    def __init__(self, road_size=0, points=[]):
        self.road_size = road_size
        self.points = points
        self.id = self.__incrementing_road_id
        self.__class__.__incrementing_road_id += 1

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


class Building():
    __incrementing_building_id = 0

    def __init__(self, position=mathutils.Vector((0, 0, 0)), width=1, height=1, depth=1):
        self.center = position
        self.width = width
        self.height = height
        self.depth = depth
        self.top_points = []
        self.bottom_points = []
        self.id = self.__incrementing_building_id
        self.__class__.__incrementing_building_id += 1

    def generate_points(self):
        x_vec = mathutils.Vector((self.width, 0, 0))
        y_vec = mathutils.Vector((0, self.height, 0))
        self.bottom_points = [
            x_vec + y_vec,
            x_vec - y_vec,
            -x_vec - y_vec,
            -x_vec + y_vec
        ]
        self.top_points = [bot + mathutils.Vector((0, 0, self.depth)) for bot in self.bottom_points]

    def draw(self):
        vertices = self.bottom_points + self.top_points

        indices = [
            (0, 1, 2, 3),   # bottom
            (4, 5, 6, 7),   # top (maybe wound wrong way)
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7)
        ]

        mesh = bpy.data.meshes.new('Building Mesh ' + str(self.id))
        obj = bpy.data.objects.new("Building Object " + str(self.id), mesh)
        obj.location = self.center
        bpy.context.scene.objects.link(obj)

        mesh.from_pydata(vertices, [], indices)
        mesh.update(calc_edges=True)


class BuildingLot():
    __incrementing_lot_id = 0

    def __init__(self, center, base_size, to_road):
        self.center = center
        self.base_size = base_size
        self.to_road = to_road
        self.id = self.__incrementing_lot_id
        self.__class__.__incrementing_lot_id += 1

    def draw(self):
        draw_line("lot" + str(self.id), "curve" + str(self.id), self._points)

    @property
    def _points(self):
        return [self.center, self.center + self.to_road * self.base_size / 2]
