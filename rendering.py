import bpy

NAME_COUNTER = 0


def draw_line(objname, curvename, cList):
    global NAME_COUNTER

    NAME_COUNTER += 1
    curvedata = bpy.data.curves.new(name=curvename + str(NAME_COUNTER), type='CURVE')
    curvedata.dimensions = '3D'

    objectdata = bpy.data.objects.new(objname + str(NAME_COUNTER), curvedata)
    objectdata.location = (0, 0, 0)
    bpy.context.scene.objects.link(objectdata)

    polyline = curvedata.splines.new('POLY')
    polyline.points.add(len(cList)-1)
    for num, list_item in enumerate(cList):
        x, y, z = list_item
        polyline.points[num].co = (x, y, z, 0)
