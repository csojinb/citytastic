from roads import spawn_roads_within_grid
from heatmap import generate_heatmap
# from buildings import generate_buildings
from naive_implementation import get_buildings
from models import Grid
import bpy
import mathutils
import time

from lots import select_lots

HEATMAP_SIZE = 20


def cleanup():
    should_delete = False
    for key in bpy.data.objects.keys():
        if "road" in key or "Building" in key:
            bpy.data.objects.get(key).select = True
            should_delete = True

    if should_delete:
        bpy.ops.object.delete()


# first, delete the objects generated and drawn from the last city generated
cleanup()

timer_start = time.time()
grid = Grid(mathutils.Vector((0, 0, 0)), 5, 5)

spawned_roads = spawn_roads_within_grid(grid, 3)
heatmap = generate_heatmap(grid, spawned_roads, HEATMAP_SIZE)


for road in spawned_roads:
    road.draw()

buildings = get_buildings(heatmap)

for b in buildings:
    b.draw()

lots = select_lots(spawned_roads)

for lot in lots:
    lot.draw()


print("timed the whole thing {0}".format(time.time() - timer_start))


print("done")
