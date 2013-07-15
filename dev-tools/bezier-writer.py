'''
Serializer for bezier curves.

Usage:
1. Create a bezier curve (supports internal curves for subtraction).
2. Locate the panel in the Properties Sidebar of the 3D View
3. Click the "Generate bezier coords" button.
4. Output is in a new text datablock called bezier-code.txt
'''
import bpy

def generalPacker(packList, delimiter, groupSuffix):
    j = ""
    
    for i in range(len(packList)):
        j += str(packList[i])
        if i < len(packList) - 1:
            j += delimiter + groupSuffix
    j = "[" + j + "]"
    
    return j

def rTh(valueList):
    newList = ["{:.3f}".format(i) for i in valueList] #[round(i, 3) for i in valueList]
    return generalPacker(newList, ", ", "")

def appendToList(baseList, newEntry):
    baseList.append(rTh(newEntry))

def main():
    Obj = bpy.context.active_object
    Data = Obj.data

    immediate = []
    deferred = []
    segments = []
    splines = []
    fullPack = []
    
    for i in Data.splines:
        for j in i.bezier_points:
            if len(deferred) == 0:
                appendToList(deferred, j.handle_left)
                appendToList(deferred, j.co)
            if len(immediate) == 0:
                appendToList(immediate, j.co)
                appendToList(immediate, j.handle_right)
            elif len(immediate) == 2:
                appendToList(immediate, j.handle_left)
                appendToList(immediate, j.co)

                segments.append(generalPacker(immediate, ", ", ""))

                immediate = []
                appendToList(immediate, j.co)
                appendToList(immediate, j.handle_right)

        if len(deferred) > 0:
            immediate.append(deferred[0])
            immediate.append(deferred[1])

            segments.append(generalPacker(immediate, ", ", ""))
            deferred = []
            immediate = []
        
        splines.append(generalPacker(segments, ",", "\n"))
        segments = []
    output_filename = "bezier-code.txt"
    
    if output_filename in bpy.data.texts.keys():
        output = bpy.data.texts[output_filename]
        output.clear()
    else:
        output = bpy.data.texts.new(name=output_filename)
    
    output.write("'" + bpy.context.active_object.name + "': " + generalPacker(splines, ",", "\n") + ",\n")

class VIEW3D_OT_bezier_writer(bpy.types.Operator):
    '''Write bezier coords to text file'''
    bl_idname = "view3d.bezier_writer"
    bl_label = "Bezier Writer"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == "CURVE"

    def execute(self, context):
        main()
        self.report({'INFO'}, "Bezier coordinates written to 'bezier-code.txt'")
        return {'FINISHED'}

class VIEW3D_PT_bezier_writer(bpy.types.Panel):
    bl_label = "Generate Bezier Coordinates"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.operator("view3d.bezier_writer", text="Generate bezier coords", icon="PLAY")
        
        row = layout.row()
        row.label(text="Active object is: " + obj.name)


def register():
    bpy.utils.register_class(VIEW3D_PT_bezier_writer)
    bpy.utils.register_class(VIEW3D_OT_bezier_writer)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_bezier_writer)
    bpy.utils.unregister_class(VIEW3D_OT_bezier_writer)


if __name__ == "__main__":
    register()
