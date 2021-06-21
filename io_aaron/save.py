import json

import bpy
from mathutils import Vector


def aaron_vec(vec):
    return {
        "X": round(vec.y * 1000),
        "Y": round(vec.z * 1000),
        "Z": round(vec.x * 1000),
    }


def aaron_quat(quat):
    return {
        "X": round(quat.y * 32767),
        "Y": round(quat.z * 32767),
        "Z": round(quat.x * 32767),
        "W": round(quat.w * 32767)
    }


def main(context, report):
    scene_data = context.scene.aaron_data

    carData = {
        'CarTypeName': scene_data.car_type_name,
        'BaseModelName': scene_data.base_model_name,
        'ManufacturerName': scene_data.manufacturer_name,
        'UsageType': scene_data.usage_type,
        'DefaultBasePaint': scene_data.default_base_paint & 0xFFFFFFFF,
        'Skinnable': scene_data.skinnable,
        'DefaultSkinNumber': scene_data.default_skin_number
    }

    out_bounds = []

    def add_bound(object, parent_pos=None):
        pos, rot, scale = object.matrix_world.decompose()
        flags = object.aaron_data.flags | {'kBounds_Box' if object.empty_display_type == 'CUBE' else 'kBounds_Sphere'}
        children = [x for x in object.children if x.aaron_data.object_kind == 'bound']
        our_pos = Vector()
        if parent_pos is not None:
            our_pos = pos - parent_pos
        out_bounds.append({
            'Orientation': aaron_quat(rot),
            'Position': aaron_vec(our_pos),
            'Flags': ', '.join(flags),
            'HalfDimensions': aaron_vec(scale),
            'NumChildren': len(children),
            'PCloudIndex': 255,
            'Pivot': aaron_vec(pos),
            'ChildIndex': len(out_bounds) + 1 if len(children) > 0 else -1,
            'AttributeName': 0,
            'Surface': object.aaron_data.surface_hash & 0xFFFFFFFF,
            'NameHash': 0
        })

        for child in children:
            add_bound(child, parent_pos=pos)

    for object in scene_data.collection.objects:
        if object.aaron_data.object_kind == 'bound' and object.parent is None:
            add_bound(object)

    if len(out_bounds) > 0:
        carData['BoundsPack'] = {
            'Entries': out_bounds,
            'PointClouds': []
        }

    if scene_data.spoiler_type != 'undefined':
        carData['Spoiler'] = {
            'SpoilerType': scene_data.spoiler_type
        }

    with open(bpy.path.abspath(scene_data.path) + '_saved.json', 'w') as f:
        json.dump(carData, f, indent=2)

    report({'INFO'}, f'Saved!')


class AaronSaveOperator(bpy.types.Operator):
    bl_idname = "scene.aaron_save"
    bl_label = "Save to file"

    @classmethod
    def poll(cls, context):
        aaron_data = context.scene.aaron_data
        return aaron_data.enabled and aaron_data.path is not None and aaron_data.collection is not None

    def execute(self, context):
        main(context, self.report)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AaronSaveOperator)


def unregister():
    bpy.utils.unregister_class(AaronSaveOperator)
