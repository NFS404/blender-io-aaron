import json
import math

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector
from .hash import resolve_hash

FLAGS_OMIT = {'kBounds_Box', 'kBounds_Sphere'}


def blender_vec(vec):
    return Vector((vec['Z'] / 1000, vec['X'] / 1000, vec['Y'] / 1000))


def blender_quat(vec):
    return Quaternion((vec['W'] / 32767, vec['Z'] / 32767, vec['X'] / 32767, vec['Y'] / 32767))


def main(context, report):
    scene_data = context.scene.aaron_data

    for obj in scene_data.collection.all_objects:
        # if obj.aaron_data.object_kind != 'none':
        bpy.data.objects.remove(obj)

    with open(bpy.path.abspath(scene_data.path), 'r') as f:
        carData = json.load(f)

    scene_data.car_type_name = carData['CarTypeName']
    scene_data.base_model_name = carData['BaseModelName']
    scene_data.manufacturer_name = carData['ManufacturerName']
    scene_data.usage_type = carData['UsageType']
    scene_data.default_base_paint = resolve_hash(carData['DefaultBasePaint'])
    scene_data.skinnable = carData['Skinnable']
    scene_data.default_skin_number = carData['DefaultSkinNumber']
    if 'Spoiler' in carData:
        scene_data.spoiler_type = carData['Spoiler']['SpoilerType']
    else:
        scene_data.spoiler_type = 'undefined'

    bounds = carData['BoundsPack']['Entries']
    pointclouds = carData['BoundsPack']['PointClouds']

    seen_bounds = set()

    def create_point_cloud(id, parent, parent_pivot):
        pointcloud = pointclouds[id]
        mesh = bpy.data.meshes.new(f'PointCloud_{id}')
        bm = bmesh.new()
        for j, vert in enumerate(pointcloud['Vertices']):
            bm.verts.new((vert['Z'], vert['X'], vert['Y']))
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bmesh.ops.join_triangles(bm, faces=bm.faces,
                                 cmp_seam=False, cmp_sharp=False, cmp_uvs=False,
                                 cmp_vcols=False, cmp_materials=False,
                                 angle_face_threshold=math.radians(45), angle_shape_threshold=math.radians(45)
                                 )
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f'PointCloud_{id}', mesh)
        obj.parent = parent
        obj.matrix_world = Matrix.Translation(blender_vec(parent_pivot))
        # obj.matrix_world = Matrix.Identity(4)
        # obj.show_in_front = True
        obj.show_wire = True
        obj.color = (0, 0, 1, 0.5)
        scene_data.collection.objects.link(obj)
        return mesh

    def create_bound(bound_id, bound, parent_pivot=None, parent_obj=None, depth=1):
        # print(f"Creating bound {bound_id}")
        flags = set(bound['Flags'].split(', '))
        dimensions = bound['HalfDimensions']

        obj_name = f'Bound_{bound_id}'
        # mesh = bpy.data.meshes.new(obj_name)
        # bm = bmesh.new()
        #    if 'kBounds_Box' in flags:
        #        bmesh.ops.create_cube(bm, matrix=Matrix.Diagonal(blender_vec(dimensions)))
        #    else:
        #        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=0.5, matrix=Matrix.Diagonal(blender_vec(dimensions)))
        #    bm.to_mesh(mesh)
        #    bm.free()
        #    mesh.materials.append(bpy.data.materials['BoundMaterial'])
        obj = bpy.data.objects.new(obj_name, None)
        scale = Matrix.Diagonal(blender_vec(dimensions)).to_4x4()
        obj.aaron_data.object_kind = 'bound'
        obj.aaron_data.flags = flags - FLAGS_OMIT
        obj.aaron_data.surface = resolve_hash(bound['Surface'])
        obj.aaron_data.bound_name = resolve_hash(bound['NameHash'])
        obj.aaron_data.attribute_name = resolve_hash(bound['AttributeName'])
        obj.empty_display_size = 1
        obj.show_in_front = True
        if 'kBounds_Box' in flags:
            obj.empty_display_type = 'CUBE'
        else:
            obj.empty_display_type = 'SPHERE'
        obj.parent = parent_obj
        obj.aaron_data.pivot_pos = tuple(blender_vec(bound['Pivot']))
        if parent_obj is not None:
            obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()
        if scene_data.use_pivot:
            # print(bound_id, blender_vec(bound['Pivot']))
            obj.matrix_world = Matrix.Translation(blender_vec(bound['Pivot'])) @ blender_quat(
                bound['Orientation']).to_matrix().to_4x4() @ scale
        elif parent_pivot is not None:
            trans_vec = blender_vec(parent_pivot) + blender_vec(bound['Position'])
            obj.aaron_data.global_pos = tuple(trans_vec)
            obj.matrix_world = Matrix.Translation(trans_vec) @ blender_quat(
                bound['Orientation']).to_matrix().to_4x4() @ scale
        else:
            obj.aaron_data.global_pos = tuple(blender_vec(bound['Position']))
            obj.matrix_world = Matrix.Translation(blender_vec(bound['Position'])) @ blender_quat(
                bound['Orientation']).to_matrix().to_4x4() @ scale
        scene_data.collection.objects.link(obj)

        # pivot_marker = bpy.data.objects.new('PivotMarker', None)
        # pivot_marker.parent = obj
        # pivot_marker.matrix_parent_inverse = obj.matrix_world.inverted()
        # pivot_marker.matrix_world = Matrix.Translation(blender_vec(bound['Pivot']))
        # pivot_marker.empty_display_size = 0.1
        # scene_data.collection.objects.link(pivot_marker)

        if bound["PCloudIndex"] != 255:
            obj.aaron_data.point_cloud = create_point_cloud(bound["PCloudIndex"], parent=parent_obj,
                                                            parent_pivot=parent_pivot)

        child_idx = bound["ChildIndex"]
        if child_idx == -1:
            return
        num_children = bound["NumChildren"]

        for i in range(child_idx, child_idx + num_children):
            seen_bounds.add(i)
            print(
                f'{"-" * depth} Child bound {i} with {bounds[i]["NumChildren"]} children at {bounds[i]["ChildIndex"]}')
            create_bound(i, bounds[i], parent_pivot=bound["Pivot"], parent_obj=obj, depth=depth + 1)

    for i, bound in enumerate(bounds):
        if i in seen_bounds:
            continue
        print(f'Root bound {i} with {bound["NumChildren"]} children at {bound["ChildIndex"]}')
        create_bound(i, bound)

    report({'INFO'}, f'Imported!')


class AaronLoadOperator(bpy.types.Operator):
    bl_idname = "scene.aaron_load"
    bl_label = "Load from file"

    @classmethod
    def poll(cls, context):
        aaron_data = context.scene.aaron_data
        return aaron_data.enabled and aaron_data.path is not None and aaron_data.collection is not None

    def execute(self, context):
        main(context, self.report)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AaronLoadOperator)


def unregister():
    bpy.utils.unregister_class(AaronLoadOperator)
