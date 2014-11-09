from models import Wanderer, Road
import mathutils
import random


def spawn_roads_within_grid(grid, road_size):
    spawned_roads = []
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
                        spawned_roads.append(newly_created_road)
                        newly_created_road.draw()

                        num_mediums = random.randint(1, 8)
                        while num_mediums > 0:
                            num_mediums -= 1
                            start_point, start_dir = randomly_select_road_start(generated_points)
                            spawned_roads.extend(spawn_roads(start_point, start_dir, road_size-1, grid))
                        num_smalls = random.randint(10, 20)
                        while num_smalls > 0:
                            num_smalls -= 1
                            start_point, start_dir = randomly_select_road_start(generated_points)
                            spawned_roads.extend(spawn_roads(start_point, start_dir, 1, grid))
                    # choose 10 random children
                    break

    return spawned_roads


def spawn_roads(position, direction, road_size, grid):
    new_roads = []

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
        return []

    new_roads.append(Road(road_size, points_created))

    if road_size < 1:
        return []
    if len(points_created) < 3:
        return []

    num_children = random.randint(*child_range[road_size])
    i = 0
    while i < num_children:
        i += 1
        chosen_point, chosen_dir = randomly_select_road_start(points_created)
        new_roads.extend(spawn_roads(chosen_point, chosen_dir, road_size-1, grid))

    return new_roads


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
