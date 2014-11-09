from models import HeatmapSquare
import mathutils


def generate_heatmap(grid, roads, heatmap_size):
    # create base, and initialize centers
    x_move = mathutils.Vector((1, 0, 0)) * (grid.width * 2 / heatmap_size)
    y_move = mathutils.Vector((0, 1, 0)) * (grid.height * 2 / heatmap_size)
    bottom_left_point = grid.center - mathutils.Vector((grid.width, grid.height, 0)) + x_move * 0.5 + y_move * 0.5
    heatmap = [[HeatmapSquare(center=(bottom_left_point + x_move * x + y_move * y)) for y in range(heatmap_size)] for x in range(heatmap_size)]

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