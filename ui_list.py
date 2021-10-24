import bpy
import random

from bpy.props import EnumProperty, StringProperty, BoolProperty, IntProperty, FloatProperty

from .util import get_pref, friendly_names

preset_link = {
    '关注嘉然': 'https://space.bilibili.com/672328094',
    '猫中毒': 'https://www.bilibili.com/video/BV1FX4y1g7u8',
    '超级敏感': 'https://www.bilibili.com/video/BV1vQ4y1Z7C2',
}


class SD_OT_UrlListAction(bpy.types.Operator):
    bl_idname = 'sd.url_list_action'
    bl_label = '添嘉/删除/上移/下移/清空'
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(items=[
        ('ADD', 'Add', ''),
        ('REMOVE', 'Remove', ''),
    ])

    index: IntProperty(name='Input Index')

    def execute(self, context):
        pref = get_pref()

        if self.action == 'ADD':
            item = pref.url_list.add()
            key = random.choice(list(preset_link))
            item.name = key
            item.url = preset_link[key]
        elif self.action == 'REMOVE':
            pref.url_list.remove(self.index)

        return {"FINISHED"}


class SD_UL_ImageList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        pref = get_pref()
        row = layout.split(factor=0.3, align=1)

        # name
        row.prop(item, 'name', text='', emboss=False,
                 icon='EDITMODE_HLT' if pref.image_dir_list_index == index else 'DOT')
        # middle msg
        row.prop(item, 'path', text='', emboss=False, )


class SD_OT_ImageListAction(bpy.types.Operator):
    """操作选中项"""
    bl_idname = 'sd.image_list_action'
    bl_label = '列表操作'
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(items=[
        ('ADD', 'Add', ''),
        ('REMOVE', 'Remove', ''),
        ('UP', 'Up', ''),
        ('DOWN', 'Down', ''),
        ('CLEAR', 'Clear All', ''),
    ])
    # add action
    name: StringProperty(default='')
    path: StringProperty(default='')

    def move_index(self, sound_index, sound_list):
        new_index = sound_index + (-1 if self.action == 'UP' else 1)
        return max(0, min(new_index, len(sound_list) - 1))

    def execute(self, context):
        pref = get_pref()
        # if len(pref.sound_list) == 0: return {"FINISHED"}

        if self.action == 'ADD':
            item = pref.image_dir_list.add()
            pref.image_dir_list_index = len(pref.image_dir_list) - 1
            # import
            if self.name != '':
                item.name = self.name
            if self.path != '':
                item.path = self.path

        elif self.action == 'REMOVE':
            pref.image_dir_list.remove(pref.image_dir_list_index)
            pref.image_dir_list_index -= 1 if len(pref.image_dir_list) > 0 else 0

        elif self.action in {'UP', 'DOWN'}:
            neighbor = pref.sound_list_index + (-1 if self.action == 'UP' else 1)
            pref.image_dir_list.move(neighbor, pref.image_dir_list_index)
            pref.image_dir_list_index = self.move_index(pref.image_dir_list_index, pref.image_dir_list)

        elif self.action == 'CLEAR':
            pref.image_dir_list.clear()

        return {"FINISHED"}

    def draw(self, context):
        self.layout.label(text="确认全部清空？此操作不可撤回")

    def invoke(self, context, event):
        if self.action == 'CLEAR':
            return context.window_manager.invoke_props_dialog(self, width=300)

        return self.execute(context)


class SD_UL_SoundList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        pref = get_pref()
        row = layout.row(align=1)

        # name
        row.prop(item, 'name', text='', emboss=False)

        # middle msg
        if pref.sound_list_index == index:
            row.label(text='编辑中', icon='EDITMODE_HLT')
        else:
            text = ''
            if item.ctrl: text += 'Ctrl+'
            if item.alt: text += 'Alt+'
            if item.shift: text += 'Shift+'
            text += friendly_names[item.key] if item.key in friendly_names else item.key
            row.label(text=text)
        # use
        row.prop(item, 'enable', text='')

    ### TODO 组属性自定义搜索，组屏蔽等功能
    ### TODO UI造型：按钮/下拉菜单？
    ### TODO 错误提示


class SD_OT_SoundListAction(bpy.types.Operator):
    """操作选中项"""
    bl_idname = 'sd.sound_list_action'
    bl_label = '列表操作'
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(items=[
        ('ADD', 'Add', ''),
        ('REMOVE', 'Remove', ''),
        ('UP', 'Up', ''),
        ('DOWN', 'Down', ''),
        ('CLEAR', 'Clear All', ''),
    ])
    confirm: BoolProperty(default=False)
    # add action
    name: StringProperty(default='')
    path: StringProperty(default='')

    def move_index(self, sound_index, sound_list):
        new_index = sound_index + (-1 if self.action == 'UP' else 1)
        return max(0, min(new_index, len(sound_list) - 1))

    def execute(self, context):
        pref = get_pref()
        # if len(pref.sound_list) == 0: return {"FINISHED"}

        if self.action == 'ADD':
            item = pref.sound_list.add()
            pref.sound_list_index = len(pref.sound_list) - 1
            # import
            if self.name != '':
                item.name = self.name
            if self.path != '':
                item.path = self.path

        elif self.action == 'REMOVE':
            pref.sound_list.remove(pref.sound_list_index)
            pref.sound_list_index -= 1 if len(pref.sound_list) > 0 else 0

        elif self.action in {'UP', 'DOWN'}:
            neighbor = pref.sound_list_index + (-1 if self.action == 'UP' else 1)
            pref.sound_list.move(neighbor, pref.sound_list_index)
            pref.sound_list_index = self.move_index(pref.sound_list_index, pref.sound_list)

        elif self.action == 'CLEAR':
            pref.sound_list.clear()

        return {"FINISHED"}

    def draw(self, context):
        self.layout.label(text="确认全部清空？此操作不可撤回")

    def invoke(self, context, event):
        if self.action == 'CLEAR':
            return context.window_manager.invoke_props_dialog(self, width=300)

        return self.execute(context)


def register():
    bpy.utils.register_class(SD_OT_UrlListAction)
    bpy.utils.register_class(SD_OT_SoundListAction)
    bpy.utils.register_class(SD_UL_SoundList)
    bpy.utils.register_class(SD_OT_ImageListAction)
    bpy.utils.register_class(SD_UL_ImageList)


def unregister():
    bpy.utils.unregister_class(SD_OT_UrlListAction)
    bpy.utils.unregister_class(SD_OT_SoundListAction)
    bpy.utils.unregister_class(SD_UL_SoundList)
    bpy.utils.unregister_class(SD_OT_ImageListAction)
    bpy.utils.unregister_class(SD_UL_ImageList)
