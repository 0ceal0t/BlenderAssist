from struct import pack
import bpy
from mathutils import Quaternion, Vector

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

def detect_armature():
    if bpy.context.object != None and bpy.context.object.type == 'ARMATURE':
        return bpy.context.object
    return None