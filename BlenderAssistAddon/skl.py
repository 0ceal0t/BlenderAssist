import bpy

from . import helper

def export(out_bin_file):
    arm_ob = helper.detect_armature()
    bpy.context.view_layer.objects.active = arm_ob
    bpy.context.active_object.select_set(state=True)

    bone_names = []
    ref_poses = {}
    bone_parent = {}

    for bone in arm_ob.data.bones:
        bone_names.append(bone.name)

        if bone.parent:
            bone_parent[bone.name] = bone.parent.name
            m = bone.parent.matrix_local.inverted() @ bone.matrix_local
        else:
            bone_parent[bone.name] = None
            m = bone.matrix_local
            
        location, rotation, scale = m.decompose()
        t = helper.Transform()
        t.translation = location
        t.rotation = rotation
        t.scale = scale
        ref_poses[bone.name] = t

    if not ("n_root" in bone_names):
        for name in bone_parent:
            if bone_parent[name] == None:
                bone_parent[name] = "n_root"

        bone_names.insert(0, "n_root")
        bone_parent["n_root"] = None
        ref_poses["n_root"] = helper.Transform()

    with open(out_bin_file, 'wb') as file:
        helper.write_int(file, len(bone_names))
        for name in bone_names:
            # Name
            helper.write_cstring(file, name)

            # Parent
            parent = bone_parent[name]
            if parent == None:
                helper.write_cstring(file, "None")
            else:
                helper.write_cstring(file, parent)

            # Ref Pose
            ref_poses[name].write(file)
