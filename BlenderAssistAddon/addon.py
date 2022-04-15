from numpy import true_divide
import bpy
from bpy.props import (StringProperty, PointerProperty, IntProperty, CollectionProperty, BoolProperty)                    
from bpy.types import (PropertyGroup, Operator)

import os
from mathutils import Quaternion, Vector

from . import helper
from . import data
from . import exclude_bones

import subprocess

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

        helper.write_vector4_raw(file, v)
        helper.write_vector4_raw(file, q)
        helper.write_vector4_raw(file, s)

# ================================

def export(startFrame, endFrame, out_bin_file):
    arm_ob = helper.detect_armature()
    bpy.context.view_layer.objects.active = arm_ob
    bpy.context.active_object.select_set(state=True)

    numOriginalFrames = endFrame - startFrame
    duration = float(numOriginalFrames - 1) * 0.0333333333333333

    print("numFrames " + str(numOriginalFrames))
    print("duration " + str(duration))

    tracks = {}
    for bone in arm_ob.data.bones:
        excluded = False
        for exclude_bone in bpy.context.scene.b_assist_props.exclude_bones:
            if bone.name == exclude_bone.bone:
                excluded = True
                print("Excluded: " + bone.name)
                break

        if excluded:
            continue
                
        tracks[bone.name] = []

    numTracks = len(tracks)
    print("numTracks " + str(numTracks))

    current_frame = 0
    for current_frame in range(numOriginalFrames + 1):
        #current_time = current_frame * 0.0333333333333333
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
        helper.write_int(file, numOriginalFrames)
        helper.write_int(file, numTracks)
        helper.write_float(file, duration)
        
        for track_name in tracks:
            print("Blender bone : " + track_name)
            helper.write_cstring(file, track_name)
            
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
    check_original_bound: BoolProperty(
        name = "Only animate same bones as original animation (do not check for custom skeletons)",
        default = False
    )
    exclude_bones: CollectionProperty(type=data.ExcludeBone)
    editing_exclude_bones: BoolProperty(default=False)
    active_exclude_bone: bpy.props.IntProperty()

# ================================

# note: uses a custom tofbx which exports to binary
# https://github.com/lmcintyre/fbx2havok/blob/master/Core/FBXCommon.cxx#L75
class BlenderAssistImport(Operator):
    bl_idname = "b_assist_props.blender_assist_import"
    bl_label = "Blender Assist Operator"

    def execute(self, context):
        scene = context.scene
        state = scene.b_assist_props

        anim_in = state.input_pap_import
        skl_in = state.input_sklb_import

        dirname = os.path.dirname(os.path.abspath(__file__))

        skip_pap = len(anim_in) == 0
        
        skl_hkx = dirname + '/tmp/import_skl.hkx'

        anim_hkx = dirname + '/tmp/import_anim.hkx'
        if skip_pap:
            anim_in = "\"\""
            anim_hkx = "\"\""

        fbx_out = dirname + '/tmp/import.fbx'

        command = dirname + '/bin/blenderassist.exe'
        print(command + " " + skl_in + " " + anim_in + " " + skl_hkx + " " + anim_hkx)
        subprocess.run([command, 'extract', skl_in, anim_in, skl_hkx, anim_hkx])

        command = dirname + '/bin/tofbx.exe'
        print(command + " " + skl_hkx + " " + anim_hkx + " " + fbx_out)

        if skip_pap:
            subprocess.run([command, '-hk_skeleton', skl_hkx, '-fbx', fbx_out])
        else:
            subprocess.run([command, '-hk_skeleton', skl_hkx, '-hk_anim', anim_hkx, '-fbx', fbx_out])

        bpy.ops.import_scene.fbx( filepath = fbx_out )

        return {'FINISHED'}

class BlenderAssistExport(Operator):
    bl_idname = "b_assist_props.blender_assist_export"
    bl_label = "Blender Assist Operator"

    def execute(self, context):
        scene = context.scene
        state = scene.b_assist_props

        output_pap = state.output_path
        anim_in = state.input_pap
        skl_in = state.input_sklb
        anim_idx = str(state.anim_idx)
        check_original_bound = "0"
        if state.check_original_bound:
            check_original_bound = "1"

        dirname = os.path.dirname(os.path.abspath(__file__))
        
        basename = os.path.basename(output_pap)
        basename, extension = os.path.splitext(basename)
        anim_bin_file = dirname + '/tmp/' + basename + '.bin'

        print("Starting exporting to bin: " + anim_bin_file)
        export(
            state.start_frame,
            state.end_frame,
            anim_bin_file
        )

        print("Finished exporting to bin")
        command = dirname + '/bin/blenderassist.exe'
        print(command + " " + str(anim_idx) + " " + anim_bin_file + " " + skl_in + " " + anim_in + " -> " + output_pap)
        subprocess.run([command, 'pack_anim', str(anim_idx), anim_bin_file, skl_in, anim_in, output_pap, check_original_bound])

        return {'FINISHED'}
        
class BlenderAssistPanelExport(bpy.types.Panel):
    bl_idname = "BA_PT_Export"
    bl_label = "Export Animation"
    bl_category = "BlenderAssist"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        state = scene.b_assist_props

        if context.object != None and context.object.type == 'ARMATURE':
            split = layout.row().split(factor=0.244)
            split.column().label(text="Target")
            split.column().label(text=context.object.name, icon='ARMATURE_DATA')

            layout.label(text='Excluded Bones')
            exclude_bones.draw_panel(layout.box())

            if not state.editing_exclude_bones:
                layout.separator()
            
                layout.label(text="Output PAP")
                col = layout.column(align=True)
                col.prop(state, "output_path", text="")

                layout.prop(state, "start_frame")
                layout.prop(state, "end_frame")     

                layout.label(text="Original Animation PAP")
                col = layout.column(align=True)
                col.prop(state, "input_pap", text="")

                layout.prop(state, "anim_idx")

                layout.prop(state, "check_original_bound")

                layout.label(text="Original Skeleton SKLB")
                col = layout.column(align=True)
                col.prop(state, "input_sklb", text="")
                
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

        layout.label(text="Animation PAP (leave blank to only import skeleton)")
        col = layout.column(align=True)
        col.prop(b_assist_props, "input_pap_import", text="")

        layout.label(text="Skeleton SKLB")
        col = layout.column(align=True)
        col.prop(b_assist_props, "input_sklb_import", text="")

        layout.operator(BlenderAssistImport.bl_idname, text="Import", icon="PLAY")    

# ================================
        
classes = (
    data.ExcludeBone,

    BlenderAssistProperties,
    BlenderAssistPanelImport,
    BlenderAssistPanelExport,
    BlenderAssistImport,
    BlenderAssistExport,

    exclude_bones.RT_UL_exclude_bones,
	exclude_bones.ApplyOperator,
	exclude_bones.EditOperator,
	exclude_bones.ClearOperator,
	exclude_bones.ListActionOperator
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
