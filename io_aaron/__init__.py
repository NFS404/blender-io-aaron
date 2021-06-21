import importlib

import bpy

from . import hash

from . import data
from . import load
from . import save

importlib.reload(hash)

importlib.reload(data)
importlib.reload(load)
importlib.reload(save)

bl_info = {
    "name": "Aaron Car Data",
    "description": "",
    "author": "redbluescreen",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Scene > Aaron",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "TESTING",
    "category": "Scene",
}


def strings_file_updated(self, context):
    print("Hash cache reset")
    hash.reset_hash_cache()


class AaronAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    strings_file: bpy.props.StringProperty(name='Strings File',
                                           description='Path to strings.json file located in the Aaron project folder',
                                           subtype='FILE_PATH', update=strings_file_updated)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'strings_file')


def register():
    bpy.utils.register_class(AaronAddonPreferences)
    data.register()
    load.register()
    save.register()


def unregister():
    bpy.utils.unregister_class(AaronAddonPreferences)
    data.unregister()
    load.unregister()
    save.unregister()
