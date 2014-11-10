from models import Building
import mathutils


def random_within_range(min_val, max_val):
    rand_range = max_val - min_val
    return mathutils.noise.random() * rand_range + min_val


def _find_closest_heatmap_tile(point, heatmap):
    closest_tile = (None, float("inf"))
    for row in heatmap:
        for tile in row:
            to_tile = tile.center - point
            if to_tile.length_squared < closest_tile[1]:
                closest_tile = (tile, to_tile.length_squared)
    return closest_tile[0]


def generate_buildings(heatmap, lots):
    buildings = []

    min_placeable_height = 0.4
    max_height = 4

    for lot in lots:
        closest_tile = _find_closest_heatmap_tile(lot.center, heatmap)

        building_heat_value = (closest_tile.value[1] ** 0.25) / 5
        if building_heat_value > min_placeable_height:
            building_height = random_within_range(building_heat_value * 0.5, building_heat_value * 1.5)
            if building_height > max_height:
                building_height = random_within_range(max_height * 0.8, max_height)
            new = Building(position=lot.center, width=lot.base_size, height=lot.base_size, depth=building_height / 2)
            buildings += [new]

    for building in buildings:
        building.generate_points()

    return buildings
