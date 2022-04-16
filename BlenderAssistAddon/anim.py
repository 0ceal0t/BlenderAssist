import bpy

from . import helper

def export(startFrame, endFrame, out_bin_file):
    arm_ob = helper.detect_armature()
    bpy.context.view_layer.objects.active = arm_ob
    bpy.context.active_object.select_set(state=True)

    numOriginalFrames = endFrame - startFrame
    duration = float(numOriginalFrames - 1) * 0.0333333333333333

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

    need_to_add_n_root = "n_root" not in tracks
    tracks["n_root"] = []

    numTracks = len(tracks)

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
            t = helper.Transform()
            t.translation = location
            t.rotation = rotation
            t.scale = scale
            tracks[pose_bone.name].append(t)

        if need_to_add_n_root:
            tracks["n_root"].append(helper.Transform())

    with open(out_bin_file, 'wb') as file:
        helper.write_int(file, numOriginalFrames)
        helper.write_int(file, numTracks)
        helper.write_float(file, duration)
        
        for track_name in tracks:
            helper.write_cstring(file, track_name)
            
        for current_frame in range(numOriginalFrames + 1):
            for track_name in tracks:
                transform = tracks[track_name][current_frame]
                transform.write(file)