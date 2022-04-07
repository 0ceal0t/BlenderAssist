import os
import bpy
from math import radians
from mathutils import Euler, Matrix, Quaternion, Vector
from struct import pack, unpack

out_file = 'D:\\FFXIV\\TOOLS\\AnimationModding\\animout.bin'
skel_dump = 'D:\\FFXIV\\TOOLS\\AnimationModding\\lala_skeldump.txt'
endFrame = 616
startFrame = 500

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

def get_matrixes(obj):
    out_local_matrix = {}

    def rec(pbone, parent_matrix):
        matrix = pbone.matrix
        m = None
        if pbone.parent:
            out_matrix = pbone.bone.convert_local_to_pose(
                matrix,
                pbone.bone.matrix_local, # relative to armature
                parent_matrix=parent_matrix,
                parent_matrix_local=pbone.parent.bone.matrix_local,
                invert=True
            )

            m = pbone.bone.parent.matrix_local.inverted() @ pbone.bone.matrix_local
            m = m @ out_matrix
        else:
            out_matrix = pbone.bone.convert_local_to_pose(
                matrix,
                pbone.bone.matrix_local,
                invert=True
            )

            m = pbone.bone.matrix_local @ out_matrix

        out_local_matrix[pbone.name] = m

        # Compute the updated pose matrix from local and new parent matrix
        new_parent_matrix = None
        if pbone.parent:
            new_parent_matrix = pbone.bone.convert_local_to_pose(
                pbone.matrix_basis,
                pbone.bone.matrix_local,
                parent_matrix=parent_matrix,
                parent_matrix_local=pbone.parent.bone.matrix_local,
            )
        else:
            new_parent_matrix = pbone.bone.convert_local_to_pose(
                pbone.matrix_basis,
                pbone.bone.matrix_local,
            )

        if "n_hara" in pbone.name:
            print(pbone.matrix_basis)
            print(matrix)
            print(out_local_matrix[pbone.name])
            print("--------------")

        # Recursively process children, passing the new matrix through
        for child in pbone.children:
            rec(child, new_parent_matrix)

    # Scan all bone trees from their roots
    for pbone in obj.pose.bones:
        if not pbone.parent:
            rec(pbone, None)

    return out_local_matrix

# ================================

valid_bones = []
skel_file = open(skel_dump, 'r')
lines = skel_file.readlines()
for line in lines:
    line = line.strip()
    if len(line) > 0:
        valid_bones.append(line)
skel_file.close()

arm_ob = detect_armature()
bpy.context.view_layer.objects.active = arm_ob
bpy.context.active_object.select_set(state=True)

numOriginalFrames = endFrame - startFrame
duration = float(numOriginalFrames - 1) * 0.0333333333333333

print("numFrames " + str(numOriginalFrames))
print("duration " + str(duration))

tracks = {}
for bone in arm_ob.data.bones:
    if bone.name not in valid_bones:
        continue
    tracks[bone.name] = []

numTracks = len(tracks)
print("numTracks " + str(numTracks))

# ==================================

current_frame = 0
for current_frame in range(numOriginalFrames + 1):
    current_time = current_frame * 0.0333333333333333
    bpy.context.scene.frame_set(current_frame + startFrame)

    for pose_bone in arm_ob.pose.bones:
        if pose_bone.name not in tracks:
            continue
        bone = pose_bone.bone

        #if bone.parent:
        #    m = bone.parent.matrix_local.inverted() @ bone.matrix_local
        #    m = m @ pose_bone.matrix_basis
        #else:
        #    m = bone.matrix_local @ pose_bone.matrix_basis

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

# =====================================

with open(out_file, 'wb') as file:
    write_int(file, numOriginalFrames)
    write_int(file, numTracks)
    write_float(file, duration)

    for track_name in tracks:
        print("Bone: " + track_name)
        write_cstring(file, track_name)
        for current_frame in range(numOriginalFrames + 1):
            transform = tracks[track_name][current_frame]
            transform.write(file)