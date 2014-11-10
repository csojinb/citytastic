from collections import namedtuple
import math
import random

import mathutils

from models import BuildingLot
from rendering import draw_line
from roads import get_perpendicular_directions

ROAD_CLEARANCES = {
    0: 0.005,
    1: 0.01,
    2: 0.015,
    3: 0.02,
}

LOTS_PER_ROAD_POINT = 0.8


LotEdge = namedtuple('LotEdge', ['corner', 'direction'])


def select_lots(roads):
    building_lots = []
    for road in roads:
        building_lots.extend(_select_lots_on_road(road))

    return building_lots


def _select_lots_on_road(road):
    building_lots = []
    for side in [0, 1]:
        lot_edges = _select_lot_edges_on_road(road, side)
        building_lots.extend(_calculate_lots_from_edges(lot_edges))

    return building_lots


def _calculate_lots_from_edges(lot_edges):
    building_lots = []
    for i in range(len(lot_edges) - 1):
        edge1 = lot_edges[i]
        edge2 = lot_edges[i + 1]

        from_road_to_center = (edge1.direction + edge2.direction).normalized()
        between = edge2.corner - edge1.corner

        base_size = between.length
        center = (edge1.corner + between.normalized()*base_size/2 +
                  from_road_to_center * base_size)
        building_lots.append(BuildingLot(center, base_size, -from_road_to_center))

    return building_lots


def _select_lot_edges_on_road(road, side):
    number_of_edges = math.floor(LOTS_PER_ROAD_POINT * len(road.points))
    clearance = ROAD_CLEARANCES[road.road_size]

    addresses = random.sample(list(enumerate(road.points)), number_of_edges)
    addresses.sort(key=lambda x: x[0])
    lot_edges = _select_lot_edges_on_road_side(addresses, clearance, side)

    return lot_edges


def _select_lot_edges_on_road_side(addresses, clearance, side):
    lot_edges = []
    for index, address in addresses:
        try:
            perpendicular = get_perpendicular_directions(
                road.points[index - 1], road.points[index], road.points[index + 1])[side]
        except IndexError:
            continue
        corner = address + perpendicular * clearance
        lot_edges.append(LotEdge(corner=corner, direction=perpendicular))

    return lot_edges

