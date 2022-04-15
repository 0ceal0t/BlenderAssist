import bpy

from . import helper

def draw_panel(layout):
    if helper.detect_armature() == None:
        layout.row()
        return

    state = bpy.context.scene.b_assist_props
    n = len(state.exclude_bones)

    if not state.editing_exclude_bones:
        if n == 0:
            row = layout.row()
            row.label(text='No Excluded Bones', icon='INFO')
            row.operator('b_assist_exclude_bones.edit', text='Create', icon='PRESET_NEW')
        else:
            row = layout.row()
            row.label(text=str(n) + ' Excluded Bones', icon='GROUP_BONE')
            row.operator('b_assist_exclude_bones.edit', text='Edit', icon='TOOL_SETTINGS')
            row.operator('b_assist_exclude_bones.clear', text='', icon='X')
    else:
        layout.label(text='Edit Excluded Bones (%i):' % n, icon='TOOL_SETTINGS')

        row = layout.row()
        row.template_list('RT_UL_exclude_bones', '', state, 'exclude_bones', state, 'active_exclude_bone')
        col = row.column(align=True)
        col.operator('b_assist_exclude_bones.list_action', icon='ADD', text='').action = 'ADD'
        col.operator('b_assist_exclude_bones.list_action', icon='REMOVE', text='').action = 'REMOVE'
        layout.operator('b_assist_exclude_bones.apply', text='Done')

class RT_UL_exclude_bones(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        arm = helper.detect_armature()
        if arm == None:
            return
        layout.prop_search(item, 'bone', arm.data, 'bones', text='', icon='BONE_DATA')

    def draw_filter(self, context, layout):
        pass

    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_neworder = []

        return flt_flags, flt_neworder

# =========================

class EditOperator(bpy.types.Operator):
    bl_idname = 'b_assist_exclude_bones.edit'
    bl_label = 'Create'

    def execute(self, context):
        bpy.context.scene.b_assist_props.editing_exclude_bones = True
        return {'FINISHED'}

class ApplyOperator(bpy.types.Operator):
    bl_idname = 'b_assist_exclude_bones.apply'
    bl_label = 'Apply'

    def execute(self, context):
        bpy.context.scene.b_assist_props.editing_exclude_bones = False
        return {'FINISHED'}

class ListActionOperator(bpy.types.Operator):
    bl_idname = 'b_assist_exclude_bones.list_action'
    bl_label = 'Apply'
    action: bpy.props.StringProperty()

    def execute(self, context):
        state = bpy.context.scene.b_assist_props

        if self.action == 'ADD':
            exclude_bones = state.exclude_bones.add()
            state.active_exclude_bone = len(state.exclude_bones) - 1
        elif self.action == 'REMOVE':
            if len(state.exclude_bones) > 0:
                state.exclude_bones.remove(state.active_exclude_bone)
                state.active_exclude_bone =  min(state.active_exclude_bone, len(state.exclude_bones) - 1)


        return {'FINISHED'}

class ClearOperator(bpy.types.Operator):
    bl_idname = 'b_assist_exclude_bones.clear'
    bl_label = 'Reset Excluded Bones'
    bl_options = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        state = bpy.context.scene.b_assist_props
        state.exclude_bones.clear()
        return {'FINISHED'}