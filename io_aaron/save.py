import json

import bpy
from mathutils import Vector
from .hash import string_to_hash


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


def mesh_to_pointcloud(mesh: bpy.types.Mesh) -> dict:
    verts = []
    for vert in mesh.vertices:
        x, y, z = vert.co
        verts.append({
            'X': y,
            'Y': z,
            'Z': x,
            'W': 0
        })
    return {
        'Vertices': verts
    }


def main(context, report):
    scene_data = context.scene.aaron_data

    carData = {
        'CarTypeName': scene_data.car_type_name,
        'BaseModelName': scene_data.base_model_name,
        'ManufacturerName': scene_data.manufacturer_name,
        'UsageType': scene_data.usage_type,
        'DefaultBasePaint': string_to_hash(scene_data.default_base_paint),
        'Skinnable': scene_data.skinnable,
        'DefaultSkinNumber': scene_data.default_skin_number
    }

    out_bounds = []
    point_clouds = []

    bound_queue = []

    def add_bound(object, parent_pos=None):
        pos, rot, scale = object.matrix_world.decompose()
        flags = object.aaron_data.flags | {'kBounds_Box' if object.empty_display_type == 'CUBE' else 'kBounds_Sphere'}
        children = [x for x in object.children if x.aaron_data.object_kind == 'bound']
        our_pos = Vector()
        if parent_pos is not None:
            our_pos = pos - parent_pos

        pcloud_idx = 255
        point_cloud = object.aaron_data.point_cloud
        if point_cloud is not None:
            pcloud_idx = len(point_clouds)
            point_clouds.append(mesh_to_pointcloud(point_cloud))

        out_bounds.append({
            'Orientation': aaron_quat(rot),
            'Position': aaron_vec(our_pos),
            'Flags': ', '.join(flags),
            'HalfDimensions': aaron_vec(scale),
            'NumChildren': len(children),
            'PCloudIndex': pcloud_idx,
            'Pivot': aaron_vec(pos),
            'ChildIndex': -1,
            'AttributeName': string_to_hash(object.aaron_data.attribute_name),
            'Surface': string_to_hash(object.aaron_data.surface),
            'NameHash': string_to_hash(object.aaron_data.bound_name)
        })

        children.sort(key=lambda x: int(x.name[6:]))

        for child in children:
            # (parent index, Blender node, parent position)
            bound_queue.append((len(out_bounds)-1, child, pos))

    for object in scene_data.collection.objects:
        if object.aaron_data.object_kind == 'bound' and object.parent is None:
            # (parent index, Blender node, parent position)
            bound_queue.append((None, object, None))

    for bound in bound_queue:
        parent_idx, node, parent_pos = bound
        print(f"Saving {node.name}, parent={parent_idx}")
        add_bound(node, parent_pos)
        if parent_idx is not None and out_bounds[parent_idx]['ChildIndex'] == -1:
            out_bounds[parent_idx]['ChildIndex'] = len(out_bounds)-1

    if len(out_bounds) > 0:
        carData['BoundsPack'] = {
            'Entries': out_bounds,
            'PointClouds': point_clouds
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
