import importlib

from . import data
from . import load
from . import save

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


def register():
    data.register()
    load.register()
    save.register()


def unregister():
    data.unregister()
    load.unregister()
    save.unregister()
