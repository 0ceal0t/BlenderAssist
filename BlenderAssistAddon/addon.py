import bpy
from bpy.props import (StringProperty, PointerProperty, IntProperty, CollectionProperty, BoolProperty)                    
from bpy.types import (PropertyGroup, Operator)

import os

from . import anim
from . import skl
from . import data
from . import exclude_bones

import subprocess

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
    
    # Export Anim
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
        name = "Only animate same bones as original animation",
        default = False
    )

    exclude_bones: CollectionProperty(type=data.ExcludeBone)
    editing_exclude_bones: BoolProperty(default=False)
    active_exclude_bone: bpy.props.IntProperty()

    # Export Skl
    input_sklb_skel: StringProperty(
        name = "",
        default = "/tmp/original_skeleton.sklb",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )
    output_path_sklb: StringProperty(
        name = "",
        default = "/tmp/out.sklb",
        maxlen = 1024,
        subtype = "FILE_PATH"
    )

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

# ==================================

class BlenderAssistExportAnim(Operator):
    bl_idname = "b_assist_props.blender_assist_export_anim"
    bl_label = "Blender Assist Operator Animation"

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
        basename, _ = os.path.splitext(basename)
        anim_bin_file = dirname + '/tmp/' + basename + '.bin'

        print("Starting exporting to bin: " + anim_bin_file)
        anim.export(
            state.start_frame,
            state.end_frame,
            anim_bin_file
        )

        print("Finished exporting to bin")
        command = dirname + '/bin/blenderassist.exe'
        print(command + " " + str(anim_idx) + " " + anim_bin_file + " " + skl_in + " " + anim_in + " -> " + output_pap)
        subprocess.run([command, 'pack_anim', str(anim_idx), anim_bin_file, skl_in, anim_in, output_pap, check_original_bound])

        return {'FINISHED'}
        
class BlenderAssistPanelExportAnim(bpy.types.Panel):
    bl_idname = "BA_PT_Export_Anim"
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

                layout.label(text="Skeleton SKLB")
                col = layout.column(align=True)
                col.prop(state, "input_sklb", text="")
                
                layout.operator(BlenderAssistExportAnim.bl_idname, text="Export as .pap", icon="PLAY")
        else:
            layout.label(text='No armature selected', icon='ERROR')

# ================================

class BlenderAssistExportSkel(Operator):
    bl_idname = "b_assist_props.blender_assist_export_skel"
    bl_label = "Blender Assist Operator Skeleton"

    def execute(self, context):
        scene = context.scene
        state = scene.b_assist_props

        output_sklb = state.output_path_sklb
        skl_in = state.input_sklb_skel

        dirname = os.path.dirname(os.path.abspath(__file__))
        
        basename = os.path.basename(output_sklb)
        basename, _ = os.path.splitext(basename)
        skl_bin_file = dirname + '/tmp/' + basename + '.bin'

        print("Starting exporting to bin: " + skl_bin_file)
        skl.export(
            skl_bin_file
        )

        print("Finished exporting to bin")
        command = dirname + '/bin/blenderassist.exe'
        print(command + " " + skl_bin_file + " " + skl_in + " -> " + output_sklb)
        subprocess.run([command, 'pack_skel', skl_bin_file, skl_in, output_sklb])

        return {'FINISHED'}
        
class BlenderAssistPanelExportSkel(bpy.types.Panel):
    bl_idname = "BA_PT_Export_Skel"
    bl_label = "Export Skeleton"
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
        
            layout.label(text="Output SKLB")
            col = layout.column(align=True)
            col.prop(state, "output_path_sklb", text="")

            layout.label(text="Original Skeleton SKLB")
            col = layout.column(align=True)
            col.prop(state, "input_sklb_skel", text="")
            
            layout.operator(BlenderAssistExportSkel.bl_idname, text="Export as .sklb", icon="PLAY")
        else:
            layout.label(text='No armature selected', icon='ERROR') 

# ================================
        
classes = (
    data.ExcludeBone,

    BlenderAssistProperties,

    BlenderAssistPanelImport,
    BlenderAssistImport,

    BlenderAssistPanelExportAnim,
    BlenderAssistExportAnim,

    BlenderAssistPanelExportSkel,
    BlenderAssistExportSkel,

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
