'''
Draw the selected curve at the mouse position

Usage:
    1. Create a curve/text object and select it.
    2. Run this script (Alt+P)
    3. Invoke the "Simple Modal View3D Operator" in the 3D View (spacebar, type part of the name)
    4. Profit!
'''

import bpy
import bgl
import blf
import math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

def draw_callback_px(self, context):
    print("mouse points", len(self.mouse_path))

    font_id = 0  # XXX, need to find out how best to get this.

    # draw some text
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, "Hello Word " + str(len(self.mouse_path)))

    # 50% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)
    self.alpha = self.alpha - 0.02
    if self.alpha < 0.05: self.alpha = 0.05
    bgl.glColor4f(1.0, 1.0, 1.0, self.alpha)
    bgl.glLineWidth(2)

#    if not self.hide_mouse:
    drawCurve(bpy.context.active_object, 8  , 200, [self.pointer_location[0], self.pointer_location[1]])

    '''
    points = createPoints(bpy.context.active_object)
    if len(points):
        bgl.glBegin(bgl.GL_POLYGON)
        for i in points:
            bgl.glVertex2f(100*i[0], 100*i[1])
        bgl.glEnd()

    
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for x, y in self.mouse_path:
        bgl.glVertex2i(x, y)

    bgl.glEnd()
    '''

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

def createPoints(curve):
    points = []
    if curve.type != 'CURVE':
        return points
    
    Data = curve.data
    for i in Data.splines:
        for j in i.bezier_points:
            points.append(j.co)
    
    return points

def rTh(valueList):
    newList = [round(i, 3) for i in valueList]
    return newList #generalPacker(newList, ", ", "")


def appendToList(baseList, newEntry):
    baseList.append(rTh(newEntry))


def findPointInSegment(segment, t):
    if len(segment) != 4:
        raise "Bezier segment must have 4 coordinates"
    
    p = segment
    x = p[0][0]*math.pow(1 - t, 3) + 3*p[1][0]*t*math.pow(1 - t, 2) + 3*p[2][0]*t*t*(1 - t) + p[3][0]*math.pow(t, 3)
    y = p[0][1]*math.pow(1 - t, 3) + 3*p[1][1]*t*math.pow(1 - t, 2) + 3*p[2][1]*t*t*(1 - t) + p[3][1]*math.pow(t, 3)
    
    return [x, y]

def getSegments(spline):
    segments = []
    
    immediate = []
    deferred = []
        
    for j in spline.bezier_points:
        if len(deferred) == 0:
            deferred.append(j.handle_left)
            deferred.append(j.co)
        if len(immediate) == 0:
            immediate.append(j.co)
            immediate.append(j.handle_right)
        elif len(immediate) == 2:
            immediate.append(j.handle_left)
            immediate.append(j.co)
            
            segments.append(immediate)
            
            immediate = []
            immediate.append(j.co)
            immediate.append(j.handle_right)
    
    if len(deferred) > 0:
        immediate.append(deferred[0])
        immediate.append(deferred[1])
        
        segments.append(immediate)
    
    return segments

def drawCurve(curve, resolution, size, offset):
    #segments = getSegments(curve.data.splines[0])
    
    polylines = []
    for spl in curve.data.splines:
        segments = getSegments(spl)
        print("Segments:\n", segments)
        polylines.append(segmentsToPolyline(segments, 6, 100))
    print("="*80, "\n", polylines)
    chainedPolyLines = []
    for i in polylines:
        for j in i:
            chainedPolyLines.append(j)
        
    tess = tessellate_polygon(polylines)
    
    bgl.glBegin(bgl.GL_TRIANGLES)
    for i in tess:
        bgl.glVertex2f(chainedPolyLines[i[0]][0]*size + offset[0], chainedPolyLines[i[0]][1]*size + offset[1])
        bgl.glVertex2f(chainedPolyLines[i[1]][0]*size + offset[0], chainedPolyLines[i[1]][1]*size + offset[1])
        bgl.glVertex2f(chainedPolyLines[i[2]][0]*size + offset[0], chainedPolyLines[i[2]][1]*size + offset[1])
    bgl.glEnd()
    
    '''
    # Initial testing, went OK
    bgl.glBegin(bgl.GL_POLYGON)
    
    for i in segments:
        for step in range(resolution):
            x, y = findPointInSegment(i, float(step)/float(resolution))
            bgl.glVertex2f(size*x, size*y)
    
    bgl.glEnd()
    '''

def segmentsToPolyline(segments, resolution, size):
    polyline = []
    
    for i in segments:
        for step in range(resolution):
            x, y = findPointInSegment(i, float(step)/float(resolution))
            polyline.append(Vector([x, y]))

    return polyline

class ModalDrawOperator(bpy.types.Operator):
    '''Draw a line with the mouse'''
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"

    def modal(self, context, event):
        context.area.tag_redraw()
        
        self.hide_mouse = False
        print(event.type)
        
        if event.type == 'MOUSEMOVE':
            self.mouse_path.append((event.mouse_region_x, event.mouse_region_y))
            self.pointer_location = [event.mouse_region_x, event.mouse_region_y]

        elif event.type == 'RIGHTMOUSE':
            #context.region.callback_remove(self._handle)
            #return {'FINISHED'}
            self.alpha = 1.0

        elif event.type in ('HIDE-RIGHTMOUSE', 'ESC'):
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}
        
        elif event.type in ('MIDDLEMOUSE'):
            self.pointer_location = [event.mouse_region_x, event.mouse_region_y]
            self.hide_mouse = True

        #return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)

            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = context.region.callback_add(draw_callback_px, (self, context), 'POST_PIXEL')
            #self._handle = context.area.callback_add(draw_callback_px, (self, context), 'POST_PIXEL')

            self.mouse_path = []
            self.alpha = 0.05

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)

if __name__ == "__main__":
    register()