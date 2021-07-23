import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup

from . import __folder_name__


def get_pref():
    return bpy.context.preferences.addons.get(__folder_name__).preferences


class SoundListItemProperty(PropertyGroup):
    name: StringProperty(name='起一个好听的名字', default='新的圣经')
    path: StringProperty(name='音频路径', description='音频路径，也可以用带有音频的MP4代替', subtype='FILE_PATH')
    enable: BoolProperty(name='启用音频', default=True)
    # event
    alt: BoolProperty(name='Alt', default=False)
    ctrl: BoolProperty(name='Ctrl', default=False)
    shift: BoolProperty(name='Shift', default=False)
    key: StringProperty(default='NONE')

    ### TODO 组属性以满足嘉心糖出轨需求

class SD_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    sound_list: CollectionProperty(type=SoundListItemProperty)
    sound_list_index: IntProperty(default=0, min=0)


    def draw(self, context):
        pass


classes = {
    SoundListItemProperty,
    SD_Preference,
}


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


