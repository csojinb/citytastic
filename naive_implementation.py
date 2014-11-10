from buildings import generate_buildings
import mathutils


def get_build_grid(size, center, width, height):
    x_move = mathutils.Vector((1, 0, 0)) * (width * 2 / size)
    y_move = mathutils.Vector((0, 1, 0)) * (height * 2 / size)
    bottom_left_point = center - mathutils.Vector((width, height, 0)) + x_move * 0.5 + y_move * 0.5
    ret = [(bottom_left_point + x_move * x + y_move * y, (width * 2 / size) * 0.45, (height * 2 / size) * 0.45) for y in range(size) for x in range(size)]

    return ret


def get_buildings(heatmap):
    building_grid_size = 50
    DELETE_ME = get_build_grid(building_grid_size, mathutils.Vector((0, 0, 0)), 5, 5)
    return generate_buildings(heatmap, DELETE_ME)
