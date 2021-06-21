import bpy
from bpy.types import PropertyGroup

car_usage_types = [
    ('Racing', 'Racing', '', 0),
    ('Cop', 'Cop', '', 1),
    ('Traffic', 'Traffic', '', 2),
    ('Wheels', 'Wheels', '', 3),
    ('Universal', 'Universal', '', 4),
]

spoiler_types = [
    ('undefined', 'Undefined', '', 0),
    ('None', 'None', '', 1),
    ('Small', 'Small', '', 2),
    ('Large', 'Large', '', 3),
    ('Hatch', 'Hatch', '', 4)
]

kinds = [
    ('none', 'None', '', 0),
    ('bound', 'Collision Bound', '', 1),
]

flags = [
    ('kBounds_Disabled', 'Disabled', '', 0x1),
    ('kBounds_PrimVsWorld', 'PrimVsWorld', '', 0x2),
    ('kBounds_PrimVsObjects', 'PrimVsObjects', '', 0x4),
    ('kBounds_PrimVsGround', 'PrimVsGround', '', 0x8),
    ('kBounds_MeshVsGround', 'MeshVsGround', '', 0x10),
    ('kBounds_Internal', 'Internal', '', 0x20),
    # ('kBounds_Box', 'Box', '', 0x40),
    # ('kBounds_Sphere', 'Sphere', '', 0x80),
    ('kBounds_Constraint_Conical', 'Constraint_Conical', '', 0x100),
    ('kBounds_Constraint_Prismatic', 'Constraint_Prismatic', '', 0x200),
    ('kBounds_Joint_Female', 'Joint_Female', '', 0x400),
    ('kBounds_Joint_Male', 'Joint_Male', '', 0x800),
    ('kBounds_Male_Post', 'Male_Post', '', 0x1000),
    ('kBounds_Joint_Invert', 'Joint_Invert', '', 0x2000),
    ('kBounds_PrimVsOwnParts', 'PrimVsOwnParts', '', 0x4000)
]


class SceneAaronPanel(bpy.types.Panel):
    bl_idname = "SCENE_PT_aaron"
    bl_label = "Aaron"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.aaron_data, "enabled", text='')

    def draw(self, context):
        layout = self.layout
        data = context.scene.aaron_data
        layout.enabled = data.enabled
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(context.scene.aaron_data, "path")
        layout.prop(context.scene.aaron_data, "collection")
        layout.prop(context.scene.aaron_data, "use_pivot")
        row = layout.row()
        row.operator('scene.aaron_load', icon='IMPORT')
        row.operator('scene.aaron_save', icon='EXPORT')
        layout.separator_spacer()
        layout.prop(context.scene.aaron_data, "car_type_name")
        layout.prop(context.scene.aaron_data, "base_model_name")
        layout.prop(context.scene.aaron_data, "manufacturer_name")
        layout.prop(context.scene.aaron_data, "usage_type")
        layout.prop(context.scene.aaron_data, "default_base_paint")
        layout.prop(context.scene.aaron_data, "skinnable")
        layout.prop(context.scene.aaron_data, "default_skin_number")
        layout.prop(context.scene.aaron_data, "spoiler_type")


class ObjectAaronPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_aaron"
    bl_label = "Aaron"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'EMPTY' and context.scene.aaron_data.enabled

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(context.object.aaron_data, "object_kind")
        if context.object.aaron_data.object_kind == 'bound':
            layout.prop(context.object.aaron_data, "surface")
            layout.prop(context.object.aaron_data, "bound_name")
            layout.prop(context.object.aaron_data, "attribute_name")
            layout.column().prop(context.object.aaron_data, "flags")
            layout.prop(context.object.aaron_data, "point_cloud")
            if 'kBounds_MeshVsGround' in context.object.aaron_data.flags and context.object.aaron_data.point_cloud is None:
                layout.label(text='Point Cloud is required for MeshVsGround', icon='ERROR')

            # col.prop(context.object.aaron_data, "pivot_pos")
            # col.prop(context.object.aaron_data, "global_pos")


class AaronSceneProperties(PropertyGroup):
    enabled: bpy.props.BoolProperty(name='Enabled')
    path: bpy.props.StringProperty(name='File Path', subtype='FILE_PATH')
    collection: bpy.props.PointerProperty(type=bpy.types.Collection, name='Collection')
    use_pivot: bpy.props.BoolProperty(name='Use Pivot', default=True)

    car_type_name: bpy.props.StringProperty(name='Car Type Name')
    base_model_name: bpy.props.StringProperty(name='Base Model Name')
    manufacturer_name: bpy.props.StringProperty(name='Manufacturer Name')
    usage_type: bpy.props.EnumProperty(name='Usage Type', items=car_usage_types)
    default_base_paint: bpy.props.StringProperty(name='Default Base Paint')
    skinnable: bpy.props.BoolProperty(name='Skinnable')
    default_skin_number: bpy.props.IntProperty(name='Default Skin Number', min=0, max=255)
    spoiler_type: bpy.props.EnumProperty(name='Spoiler Type', items=spoiler_types)


class AaronObjectProperties(PropertyGroup):
    object_kind: bpy.props.EnumProperty(name='Kind', items=kinds, default='none')
    flags: bpy.props.EnumProperty(name='Flags', items=flags, options={'ENUM_FLAG'})
    surface: bpy.props.StringProperty(name='Surface')
    bound_name: bpy.props.StringProperty(name='Bound Name')
    attribute_name: bpy.props.StringProperty(name='Attribute Name')
    point_cloud: bpy.props.PointerProperty(name='Point Cloud', type=bpy.types.Mesh)
    pivot_pos: bpy.props.FloatVectorProperty(precision=3)
    global_pos: bpy.props.FloatVectorProperty(precision=3)


def register():
    bpy.utils.register_class(AaronObjectProperties)
    bpy.utils.register_class(AaronSceneProperties)
    bpy.types.Scene.aaron_data = bpy.props.PointerProperty(type=AaronSceneProperties)
    bpy.types.Object.aaron_data = bpy.props.PointerProperty(type=AaronObjectProperties)
    bpy.utils.register_class(SceneAaronPanel)
    bpy.utils.register_class(ObjectAaronPanel)


def unregister():
    del bpy.types.Scene.aaron_data
    del bpy.types.Object.aaron_data
    bpy.utils.unregister_class(AaronObjectProperties)
    bpy.utils.unregister_class(AaronSceneProperties)
    bpy.utils.unregister_class(SceneAaronPanel)
    bpy.utils.unregister_class(ObjectAaronPanel)
