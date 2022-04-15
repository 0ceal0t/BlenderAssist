from struct import pack
import bpy

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