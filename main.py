import bpy
import mathutils
import math
import random
import time
from collections import namedtuple

'''
filename_test = "C:/Users/cthatcher/Desktop/blender hackathon/test.py"
exec(compile(open(filename_test).read(), filename_test, 'exec'))
'''
should_delete = False
for key in bpy.data.objects.keys():
    if "road" in key:
        bpy.data.objects.get(key).select = True
        should_delete = True

if should_delete:
    bpy.ops.object.delete()

name_counter_deal = 0
spawned_roads = []


def draw_line(objname, curvename, cList):
    global name_counter_deal

    name_counter_deal += 1
    curvedata = bpy.data.curves.new(name=curvename + str(name_counter_deal), type='CURVE')
    curvedata.dimensions = '3D'

    objectdata = bpy.data.objects.new(objname + str(name_counter_deal), curvedata)
    objectdata.location = (0, 0, 0)
    bpy.context.scene.objects.link(objectdata)

    polyline = curvedata.splines.new('POLY')
    polyline.points.add(len(cList)-1)
    for num, list_item in enumerate(cList):
        x, y, z = list_item
        polyline.points[num].co = (x, y, z, 0)


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


def spawn_roads_within_grid(grid, road_size):
    global spawned_roads
    side_data = [
        mathutils.Vector((1, 0, 0)),
        mathutils.Vector((-1, 0, 0)),
        mathutils.Vector((0, 1, 0)),
        mathutils.Vector((0, -1, 0))
    ]
    side_range = [
        mathutils.Vector((0, 1, 0)),
        mathutils.Vector((0, 1, 0)),
        mathutils.Vector((1, 0, 0)),
        mathutils.Vector((1, 0, 0))
    ]
    side_max = [
        grid.width,
        grid.width,
        grid.height,
        grid.height
    ]
    side_range_max = [
        grid.height,
        grid.height,
        grid.width,
        grid.width
    ]

    num_main_roads = random.randint(2, 3)
    roads_spawned = 0
    while roads_spawned < num_main_roads:
        spawn_side = random.randint(0, 3)

        start_pos = grid.center + side_data[spawn_side] * side_max[spawn_side] + side_range[spawn_side] * side_range_max[spawn_side] * (mathutils.noise.random() * 2 - 1)

        main_road = Wanderer()
        main_road.position = start_pos
        main_road.forward = (grid.center - start_pos).normalized()
        main_road.cur_angle = main_road.forward.angle(mathutils.Vector((1, 0, 0)))

        generated_points = []
        counter = 0     # prevent infinite loops
        while len(generated_points) < 100 and counter < 2000:
            counter += 1
            generated_points = []
            inner_counter = 0
            while True:
                inner_counter += 1
                if inner_counter > 5000:
                    generated_points = []
                    break
                main_road.update(0.025)
                generated_points += [main_road.position.copy()]
                if not grid.is_point_inside(main_road.position):
                    if len(generated_points) >= 100:
                        roads_spawned += 1
                        newly_created_road = Road(road_size, generated_points)
                        spawned_roads += [newly_created_road]
                        newly_created_road.draw()

                        num_mediums = random.randint(1, 8)
                        while num_mediums > 0:
                            num_mediums -= 1
                            start_point, start_dir = randomly_select_road_start(generated_points)
                            spawn_road(start_point, start_dir, road_size-1, grid)
                        num_smalls = random.randint(10, 20)
                        while num_smalls > 0:
                            num_smalls -= 1
                            start_point, start_dir = randomly_select_road_start(generated_points)
                            spawn_road(start_point, start_dir, 1, grid)
                    # choose 10 random children
                    break


def spawn_road(position, direction, road_size, grid):
    global spawned_roads

    road_wanderer = Wanderer()
    road_wanderer.position = position
    road_wanderer.forward = direction if direction != mathutils.Vector((0, 0, 0)) else mathutils.noise.random_unit_vector()
    road_wanderer.cur_angle = road_wanderer.forward.angle(mathutils.Vector((1, 0, 0)))

    possible_lengths = [
        (5, 30),
        (20, 30),
        (25, 50)
    ]
    child_range = [
        (0, 1),
        (1, 2),
        (1, 8)
    ]

    rand_length = random.randint(*possible_lengths[road_size])
    points_created = []

    while len(points_created) < rand_length and grid.is_point_inside(road_wanderer.position):
        road_wanderer.update(0.025)
        points_created += [road_wanderer.position.copy()]

    if len(points_created) <= 0:
        return

    newly_created_road = Road(road_size, points_created)
    spawned_roads += [newly_created_road]

    if road_size < 1:
        return
    if len(points_created) < 3:
        return

    num_children = random.randint(*child_range[road_size])
    i = 0
    while i < num_children:
        i += 1
        chosen_point, chosen_dir = randomly_select_road_start(points_created)
        spawn_road(chosen_point, chosen_dir, road_size-1, grid)


def randomly_select_road_start(points_created):
    chosen_point_spot = random.randint(1, len(points_created)-2)
    chosen_point = points_created[chosen_point_spot].copy()
    chosen_dirs = get_perpendicular_directions(points_created[chosen_point_spot-1], points_created[chosen_point_spot], points_created[chosen_point_spot+1])
    chosen_dir = chosen_dirs[random.randint(0, 1)]
    return chosen_point, chosen_dir


def get_perpendicular_directions(first, middle, last):
    to_first = (first - middle).normalized()
    to_last = (last - middle).normalized()
    try:
        between = to_first.slerp(to_last, 0.5).normalized()
    except:
        between = mathutils.Vector((-to_first.y, to_first.x, 0)).normalized()
    return (between, -between)


class HeatmapSquare():
    def __init__(self, center=None, value=None):
        self.center = center
        self.value = value


def generate_heatmap(grid, roads):
    global HEATMAP_SIZE

    # create base, and initialize centers
    x_move = mathutils.Vector((1, 0, 0)) * (grid.width * 2 / HEATMAP_SIZE)
    y_move = mathutils.Vector((0, 1, 0)) * (grid.height * 2 / HEATMAP_SIZE)
    bottom_left_point = grid.center - mathutils.Vector((grid.width, grid.height, 0)) + x_move * 0.5 + y_move * 0.5
    heatmap = [[HeatmapSquare(center=(bottom_left_point + x_move * x + y_move * y)) for y in range(HEATMAP_SIZE)] for x in range(HEATMAP_SIZE)]

    # loop through each tile
    # calculate closest distance to each road
    # if it's outside the falloff, forget about it, otherwise add it to the road_size indicator
    unique_road_sizes = set()
    for road in roads:
        unique_road_sizes.add(road.road_size)

    for row in heatmap:
        for tile in row:
            tile.value = {}
            for unique_road_size in unique_road_sizes:
                tile.value[unique_road_size] = 0

    # complexity n*m*x where n=# tiles, m=# roads, x=# points per road (also known as: terrible)
    for row in heatmap:
        for tile in row:
            for road in roads:
                closest_point = (None, float("inf"))
                for point in road.points:
                    to_point = point - tile.center
                    if to_point.length_squared < closest_point[1]:
                        closest_point = (to_point.copy(), to_point.length_squared)
                tile.value[road.road_size] += 1 / closest_point[1]

    return heatmap


HEATMAP_SIZE = 1000

timer_start = time.time()
grid = Grid(mathutils.Vector((0, 0, 0)), 5, 5)
spawn_roads_within_grid(grid, 3)

heatmap = generate_heatmap(grid, spawned_roads)

for road in spawned_roads:
    road.draw()

print("timed the whole thing {0}".format(time.time() - timer_start))


print ("done")
