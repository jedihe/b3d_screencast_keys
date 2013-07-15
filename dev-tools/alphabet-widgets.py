import bpy

#Create an 'A' text object, set all properties (font, height 1 Blender Unit, etc)
#Leave it selected in the 3D View
chars = []
for char in range(ord('B'), ord('Z') + 1):
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(1, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
    bpy.context.active_object.name = chr(char)
    bpy.context.active_object.data.body = chr(char)
    chars.append(bpy.context.active_object)

    for char in range(ord('B'), ord('Z') + 1):
        bpy.context.scene.objects.active = bpy.data.objects[chr(char)]
        bpy.data.objects[chr(char)].select = True
        bpy.ops.object.convert(target='CURVE', keep_original=False)

# Convert the 'A' text object to curve (Alt+C) (remember to leave a copy of the original!)
# Adjust the origin of each character to the xmin, ymin of the bound box (be careful with the ymin,
#   since rounded characters have a lower "bump" that must be lower than ymin on other chars)

# Done. widgets are now ready to be converted to code representation (another script is needed for that).
