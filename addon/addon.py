import bpy
from bpy.props import (StringProperty, PointerProperty, IntProperty)                    
from bpy.types import (Panel, PropertyGroup, Operator)
from bpy_extras.io_utils import ExportHelper

import os
from math import radians
from mathutils import Euler, Matrix, Quaternion, Vector
from struct import pack, unpack

import subprocess

# ===============================

def write_headerstring(file, value):
    bytes = value.encode('utf-8')
    file.write(bytes)
    file.write(b'\x0a')  # '\n'

def write_cstring(file, value):
    bytes = value.encode('ascii')
    file.write(bytes)
    file.write(b'\x00')

def write_int(file, value):
    file.write(pack('<i', value))

def write_float(file, value):
    file.write(pack('<f', value))

def write_vector4_raw(file, value):
    file.write(pack('<4f', *value))

# ================================

def detect_armature():
    found = None
    for ob in bpy.context.selected_objects:
        if ob.type == 'ARMATURE':
            found = ob
            break
    return found

# ================================

class Transform(object):
    def __init__(self):
        self.translation = Vector((0, 0, 0))
        self.rotation = Quaternion()
        self.scale = Vector((1, 1, 1))

    def write(self, file):
        v = self.translation
        v = (v.x, v.y, v.z, 0)
        q = self.rotation
        q = (q.x, q.y, q.z, q.w)
        s = self.scale
        s = (s.x, s.y, s.z, 1)

        write_vector4_raw(file, v)
        write_vector4_raw(file, q)
        write_vector4_raw(file, s)

# ================================

def export(startFrame, endFrame, out_bin_file):
    arm_ob = detect_armature()
    bpy.context.view_layer.objects.active = arm_ob
    bpy.context.active_object.select_set(state=True)

    numOriginalFrames = endFrame - startFrame
    duration = float(numOriginalFrames - 1) * 0.0333333333333333

    print("numFrames " + str(numOriginalFrames))
    print("duration " + str(duration))

    tracks = {}
    for bone in arm_ob.data.bones:
        tracks[bone.name] = []

    numTracks = len(tracks)
    print("numTracks " + str(numTracks))

    current_frame = 0
    for current_frame in range(numOriginalFrames + 1):
        current_time = current_frame * 0.0333333333333333
        bpy.context.scene.frame_set(current_frame + startFrame)

        for pose_bone in arm_ob.pose.bones:
            if pose_bone.name not in tracks:
                continue
            bone = pose_bone.bone
            
            if pose_bone.parent:
                m = pose_bone.parent.matrix.inverted() @ pose_bone.matrix
            else:
                m = pose_bone.matrix

            location, rotation, scale = m.decompose()
            t = Transform()
            t.translation = location
            t.rotation = rotation
            t.scale = scale
            tracks[pose_bone.name].append(t)

    with open(out_bin_file, 'wb') as file:
        write_int(file, numOriginalFrames)
        write_int(file, numTracks)
        write_float(file, duration)
        
        for track_name in tracks:
            print("Bone : " + track_name)
            write_cstring(file, track_name)
            
        for current_frame in range(numOriginalFrames + 1):
            for track_name in tracks:
                transform = tracks[track_name][current_frame]
                transform.write(file)

# ================================

class BlenderAssistProperties(PropertyGroup):
    # Import
    input_pap_import: StringProperty(
        name = "",
        default = "/tmp/original_animation.pap",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )
    input_sklb_import: StringProperty(
        name = "",
        default = "/tmp/original_skeleton.sklb",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )
    # Export
    output_path: StringProperty(
        name = "",
        default = "/tmp/out.pap",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )
    input_pap: StringProperty(
        name = "",
        default = "/tmp/original_animation.pap",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )
    input_sklb: StringProperty(
        name = "",
        default = "/tmp/original_skeleton.sklb",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )
    start_frame: IntProperty(
        name = "Start Frame",
        default = 1,
        min = 1
    )
    end_frame: IntProperty(
        name = "End Frame",
        default = 10,
        min = 10
    )
    anim_idx: IntProperty(
        name = "Original Animation Index",
        default = 0,
        min = 0
    )

# ================================

# note: uses a custom tofbx which exports to binary
# https://github.com/lmcintyre/fbx2havok/blob/master/Core/FBXCommon.cxx#L75
class BlenderAssistImport(Operator):
    bl_idname = "b_assist_props.blender_assist_import"
    bl_label = "Blender Assist Operator"

    def execute(self, context):
        scene = context.scene
        b_assist_props = scene.b_assist_props

        anim_in = b_assist_props.input_pap_import
        skl_in = b_assist_props.input_sklb_import

        dirname = os.path.dirname(os.path.abspath(__file__))
        
        skl_hkx = dirname + '/tmp/import_skl.hkx'
        anim_hkx = dirname + '/tmp/import_anim.hkx'
        fbx_out = dirname + '/tmp/import.fbx'

        command = dirname + '/bin/blenderassist.exe'
        print(command + " " + skl_in + " " + anim_in + " " + skl_hkx + " " + anim_hkx)
        subprocess.run([command, 'extract', skl_in, anim_in, skl_hkx, anim_hkx])

        command = dirname + '/bin/tofbx.exe'
        print(command + " " + skl_hkx + " " + anim_hkx + " " + fbx_out)
        subprocess.run([command, '-hk_skeleton', skl_hkx, '-hk_anim', anim_hkx, '-fbx', fbx_out])

        bpy.ops.import_scene.fbx( filepath = fbx_out )

        return {'FINISHED'}

class BlenderAssistExport(Operator):
    bl_idname = "b_assist_props.blender_assist_export"
    bl_label = "Blender Assist Operator"

    def execute(self, context):
        scene = context.scene
        b_assist_props = scene.b_assist_props

        output_pap = b_assist_props.output_path
        anim_in = b_assist_props.input_pap
        skl_in = b_assist_props.input_sklb
        anim_idx = str(b_assist_props.anim_idx)

        dirname = os.path.dirname(os.path.abspath(__file__))
        
        basename = os.path.basename(output_pap)
        basename, extension = os.path.splitext(basename)
        anim_bin_file = dirname + '/tmp/' + basename + '.bin'

        print("Starting exporting to bin: " + anim_bin_file)
        export(
            b_assist_props.start_frame,
            b_assist_props.end_frame,
            anim_bin_file
        )

        print("Finished exporting to bin")
        command = dirname + '/bin/blenderassist.exe'
        print(command + " " + str(anim_idx) + " " + anim_bin_file + " " + skl_in + " " + anim_in + " -> " + output_pap)
        subprocess.run([command, 'pack', str(anim_idx), anim_bin_file, skl_in, anim_in, output_pap])

        return {'FINISHED'}
        
class BlenderAssistPanelExport(bpy.types.Panel):
    bl_idname = "BA_PT_Export"
    bl_label = "Export"
    bl_category = "BlenderAssist"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        b_assist_props = scene.b_assist_props

        if context.object != None and context.object.type == 'ARMATURE':
            split = layout.row().split(factor=0.244)
            split.column().label(text="Target:")
            split.column().label(text=context.object.name, icon='ARMATURE_DATA')
        
            layout.label(text="Output PAP:")
            col = layout.column(align=True)
            col.prop(b_assist_props, "output_path", text="")

            layout.prop(b_assist_props, "start_frame")
            layout.prop(b_assist_props, "end_frame")     

            layout.label(text="Original Animation PAP:")
            col = layout.column(align=True)
            col.prop(b_assist_props, "input_pap", text="")

            layout.prop(b_assist_props, "anim_idx")

            layout.label(text="Original Skeleton SKLB:")
            col = layout.column(align=True)
            col.prop(b_assist_props, "input_sklb", text="")
            
            layout.operator(BlenderAssistExport.bl_idname, text="Export as .pap", icon="PLAY")    
        else:
            layout.label(text='No armature selected', icon='ERROR')

# ================================

class BlenderAssistPanelImport(bpy.types.Panel):
    bl_idname = "BA_PT_Import"
    bl_label = "Import"
    bl_category = "BlenderAssist"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        b_assist_props = scene.b_assist_props

        layout.label(text="Animation PAP:")
        col = layout.column(align=True)
        col.prop(b_assist_props, "input_pap_import", text="")

        layout.label(text="Skeleton SKLB:")
        col = layout.column(align=True)
        col.prop(b_assist_props, "input_sklb_import", text="")

        layout.operator(BlenderAssistImport.bl_idname, text="Import", icon="PLAY")    

# ================================
        
classes = (
    BlenderAssistProperties,
    BlenderAssistPanelImport,
    BlenderAssistPanelExport,
    BlenderAssistImport,
    BlenderAssistExport
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.b_assist_props = PointerProperty(type=BlenderAssistProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)  
    del bpy.types.Scene.b_assist_props


if __name__ == "__main__":
    register()
