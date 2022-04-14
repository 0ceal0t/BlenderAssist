bl_info = {
	"name" : "BlenderAssist",
	"author" : "ocealot",
	"description" : "Export custom animations for FFXIV",
	"version": (1, 2, 0),
	"blender" : (2, 80, 0),
	"location" : "3D View > Tools (Right Side) > BlenderAssist",
	"warning" : "",
	"category" : "Animation",
	"wiki_url": 'https://github.com/0ceal0t/BlenderAssist',
    "tracker_url": 'https://github.com/0ceal0t/BlenderAssist/issues',
}

from . import addon

def register():
	addon.register()

def unregister():
    addon.unregister()