import bpy
import os
from bpy.props import EnumProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty, FloatProperty
from bpy.types import PropertyGroup

import webbrowser

from .util import SD_Preview
from .util import get_pref


# Sound items
####################

def update_path_name(self, context):
    if self.bind_name_to_path:
        self.name = os.path.basename(self.path) if os.path.isfile(self.path) else '文件不存在'


class SoundListItemProperty(PropertyGroup):
    name: StringProperty(name='起一个好听的名字', default='新的圣经')
    path: StringProperty(name='音频路径', description='音频路径，也可以用带有音频的MP4代替', subtype='FILE_PATH',update=update_path_name)
    enable: BoolProperty(name='启用音频', default=True)
    # event
    alt: BoolProperty(name='Alt', default=False)
    ctrl: BoolProperty(name='Ctrl', default=False)
    shift: BoolProperty(name='Shift', default=False)
    key: StringProperty(default='NONE')
    # state
    bind_name_to_path: BoolProperty(name='关联名字到路径', default=True)
    error: BoolProperty(name='文件错误')

    ### TODO 组属性以满足嘉心糖出轨需求
    ### TODO 错误提示


# Image items
####################

__tempPreview__ = {}


def clear_preview_cache():
    for preview in __tempPreview__.values():
        bpy.utils.previews.remove(preview)
    __tempPreview__.clear()


def enum_thumbnails_from_dir_items(self, context):
    pref = get_pref()
    enum_items = []
    if context is None: return enum_items

    try:
        item = pref.image_dir_list[pref.image_dir_list_index]
        directory = item.path
    except(Exception):
        directory = ""

    image_preview = __tempPreview__["sd_thumbnails"]

    if directory == image_preview.img_dir:
        return image_preview.img

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".jpg") or fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = image_preview.get(name)
            if not icon:
                thunmnail = image_preview.load(name, filepath, 'IMAGE')
            else:
                thunmnail = image_preview[name]
            enum_items.append((name, name, "", thunmnail.icon_id, i))

    image_preview.img = enum_items
    image_preview.img_dir = directory

    return image_preview.img


def update_path_name2(self, context):
    full_dir_name = os.path.dirname(self.path) if os.path.isdir(self.path) else None
    if full_dir_name is None:return None
    self.name = full_dir_name.replace('\\','/').split('/')[-1]

class ImageDirListItemProperty(PropertyGroup):
    name: StringProperty(name='分类名字')
    path: StringProperty(name='图片路径', description='图片文件夹路径', subtype='DIR_PATH',update=update_path_name2)
    thumbnails: EnumProperty(name='子文件夹', items=enum_thumbnails_from_dir_items)


class SD_OT_UrlLink(bpy.types.Operator):
    bl_idname = 'sd.url_link'
    bl_label = 'URL Link'

    url_link: StringProperty(name='引流链接')

    def execute(self, context):
        webbrowser.open(self.url_link)
        return {"FINISHED"}


# Preference
####################

class SD_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    # UI
    edit_title: BoolProperty(name='编辑标题', default=False)
    title: StringProperty(name='标题', default='关注嘉心糖，顿顿破大防')

    # sound
    sound_list: CollectionProperty(type=SoundListItemProperty)
    sound_list_index: IntProperty(default=0, min=0)

    # image
    image_dir_list: CollectionProperty(type=ImageDirListItemProperty)
    image_dir_list_index: IntProperty(default=0, min=0, name='激活项')

    def draw(self, context):
        layout = self.layout

        col = layout.column()

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
    img_preview = bpy.utils.previews.new()
    img_preview.img_dir = ""
    img_preview.img = ()
    __tempPreview__["sd_thumbnails"] = img_preview

    bpy.utils.register_class(SoundListItemProperty)
    bpy.utils.register_class(ImageDirListItemProperty)
    bpy.utils.register_class(SD_OT_UrlLink)
    bpy.utils.register_class(SD_Preference)


def unregister():
    bpy.utils.unregister_class(SoundListItemProperty)
    bpy.utils.unregister_class(ImageDirListItemProperty)
    bpy.utils.unregister_class(SD_OT_UrlLink)
    bpy.utils.unregister_class(SD_Preference)

    clear_preview_cache()
