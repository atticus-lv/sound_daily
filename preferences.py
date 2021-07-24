import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty, FloatProperty
from bpy.types import PropertyGroup

import webbrowser
import os

from . import __folder_name__


def get_pref():
    return bpy.context.preferences.addons.get(__folder_name__).preferences

def update_path_name(self,context):
    if self.bind_name_to_path:
        self.name = os.path.basename(self.path) if os.path.isfile(self.path) else '文件不存在'

class SoundListItemProperty(PropertyGroup):
    name: StringProperty(name='起一个好听的名字', default='新的圣经',update=update_path_name)
    path: StringProperty(name='音频路径', description='音频路径，也可以用带有音频的MP4代替', subtype='FILE_PATH')
    enable: BoolProperty(name='启用音频', default=True)
    # event
    alt: BoolProperty(name='Alt', default=False)
    ctrl: BoolProperty(name='Ctrl', default=False)
    shift: BoolProperty(name='Shift', default=False)
    key: StringProperty(default='NONE')
    # state
    bind_name_to_path: BoolProperty(name = '关联名字到路径',default=True)
    error: BoolProperty(name='文件错误')

    ### TODO 组属性以满足嘉心糖出轨需求
    ### TODO 错误提示


class SD_OT_UrlLink(bpy.types.Operator):
    bl_idname = 'sd.url_link'
    bl_label = 'URL Link'

    url_link: StringProperty(name='引流链接')

    def execute(self, context):
        webbrowser.open(self.url_link)
        return {"FINISHED"}


class SD_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    sound_list: CollectionProperty(type=SoundListItemProperty)
    sound_list_index: IntProperty(default=0, min=0)

    # UI
    edit_title: BoolProperty(name='编辑标题', default=False)
    title: StringProperty(name='标题', default='关注嘉心糖，顿顿破大防')

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.5

        layout.operator('sd.url_link', text='关注嘉然',
                        icon='URL').url_link = 'https://space.bilibili.com/672328094'
        layout.operator('sd.url_link', text='猫中毒',
                        icon='URL').url_link = 'https://www.bilibili.com/video/BV1FX4y1g7u8'
        layout.operator('sd.url_link', text='超级敏感',
                        icon='URL').url_link = 'https://www.bilibili.com/video/BV1vQ4y1Z7C2'
        # layout.label(text='')
        # layout.operator('sd.url_link', text='和嘉然比划',
        #                 icon='URL').url_link = 'https://www.bilibili.com/video/BV1kq4y1W7hW'


def register():
    bpy.utils.register_class(SoundListItemProperty)
    bpy.utils.register_class(SD_OT_UrlLink)
    bpy.utils.register_class(SD_Preference)


def unregister():
    bpy.utils.unregister_class(SoundListItemProperty)
    bpy.utils.unregister_class(SD_OT_UrlLink)
    bpy.utils.unregister_class(SD_Preference)
