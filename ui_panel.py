import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, IntProperty

from .preferences import SD_Preference, get_pref
from .util import SD_Preview

img_preview = SD_Preview()
enum_images = img_preview.register()

friendly_names = {'LEFTMOUSE': 'Left', 'RIGHTMOUSE': 'Right', 'MIDDLEMOUSE': 'Middle',
                  'WHEELUPMOUSE': "Mouse wheel up", "WHEELDOWNMOUSE": "Mouse wheel down",
                  'ESC': 'Esc', 'RET': 'Enter', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
                  'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'ZERO': '0',
                  'COMMA': 'Comma', 'PERIOD': 'Period',
                  'NONE':'无'}


class SD_UL_SoundList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        pref = get_pref()

        row = layout.row(align=1)

        row.prop(item, 'name', text='', emboss=False)

        if pref.sound_list_index == index:
            row.label(text='编辑中', icon='EDITMODE_HLT')
        else:
            text = ''
            if item.ctrl: text += 'Ctrl+'
            if item.alt: text += 'Alt+'
            if item.shift: text += 'Shift+'
            text += friendly_names[item.key] if item.key in friendly_names else item.key
            row.label(text=text)

        row.prop(item, 'enable', text='')

    ### TODO 组属性自定义搜索，组屏蔽等功能
    ### TODO UI造型：按钮/下拉菜单？


class SD_OT_SoundListAction(bpy.types.Operator):
    """操作选中项"""
    bl_idname = 'sd.sound_list_action'
    bl_label = '添加'

    action: EnumProperty(items=[
        ('ADD', 'Add', ''),
        ('REMOVE', 'Remove', ''),
        ('UP', 'Up', ''),
        ('DOWN', 'Down', ''),
    ])

    def move_index(self, sound_index, sound_list):
        new_index = sound_index + (-1 if self.action == 'UP' else 1)
        return max(0, min(new_index, len(sound_list) - 1))

    def execute(self, context):
        pref = get_pref()
        # if len(pref.sound_list) == 0: return {"FINISHED"}

        if self.action == 'ADD':
            item = pref.sound_list.add()
            pref.sound_list_index = len(pref.sound_list) - 1
            # correct name
            if item.name in pref.sound_list:
                item.name += '(1)'

        elif self.action == 'REMOVE':
            pref.sound_list.remove(pref.sound_list_index)
            pref.sound_list_index -= 1 if len(pref.sound_list) > 0 else 0

        elif self.action in {'UP', 'DOWN'}:
            pref.sound_list_index = self.move_index(pref.sound_list_index, pref.sound_list)

        return {"FINISHED"}


class SD_PT_3DViewPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '嘉然之声'
    bl_label = '关注嘉心糖|顿顿破大防'

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        col = layout.column()

        # 照片位
        col.template_icon_view(context.scene, "sd_thumbnails", scale=pref.image_scale)
        col.separator(factor=0.5)

        # 聆听位
        row = col.row()
        if context.window_manager.sd_loading_sound:
            row.prop(context.window_manager, 'sd_loading_sound', text='聆听结束', icon='CANCEL')
        else:
            row.operator('sd.sound_loader', text='嘉然之声', icon='PLAY')

        # 设置位
        row.prop(pref, 'show_pref', icon='PREFERENCES', text='')

        if pref.show_pref:
            col.separator(factor=0.5)
            box = col.box()
            box.label(text='照片设置', icon='IMAGE_DATA')
            box.prop(pref,'image_scale',slider=1)

            box = col.box()
            box.label(text='语音设置',icon='PLAY_SOUND')
            self.draw_settings(pref, box, context)

    def draw_settings(self, pref, col, context):
        # Sound List
        #########################
        row = col.row()
        row.template_list(
            'SD_UL_SoundList', 'Sound List',
            pref, 'sound_list',
            pref, 'sound_list_index')

        col1 = row.column()
        col2 = col1.column(align=1)
        col2.operator('sd.sound_list_action', icon='ADD', text='').action = 'ADD'
        col2.operator('sd.sound_list_action', icon='REMOVE', text='').action = 'REMOVE'

        col2 = col1.column(align=1)
        col2.operator('sd.sound_list_action', icon='TRIA_UP', text='').action = 'UP'
        col2.operator('sd.sound_list_action', icon='TRIA_DOWN', text='').action = 'DOWN'

        # Current item
        #########################
        if len(pref.sound_list) == 0: return None
        item = pref.sound_list[pref.sound_list_index]

        col = col.column(align=1).box()
        col.label(icon='EDITMODE_HLT', text='当前项')
        # base info
        row = col.row()
        row.prop(item, 'name', text='名称')
        row.prop(item, 'enable', text='启用')

        row = col.row(align=1)
        row.prop(item, 'path', icon='SOUND')

        # details
        details = col.box()
        col = details.column()
        col.label(text='按键绑定', icon='KEYINGSET')

        if context.window_manager.sd_listening:
            col.prop(context.window_manager, 'sd_listening', text='按一个按键，可组合Ctrl/Shift/Alt', toggle=1)
        else:
            row = col.split(factor=0.5)
            row.operator('sd.get_event', text=friendly_names[item.key] if item.key in friendly_names else item.key)
            row1 = row.row(align=1)
            row1.prop(item, 'ctrl', toggle=1)
            row1.prop(item, 'alt', toggle=1)
            row1.prop(item, 'shift', toggle=1)


def draw_top_bar(self, context):
    layout = self.layout
    layout.separator(factor=0.5)

    if context.window_manager.sd_loading_sound:
        layout.prop(context.window_manager, 'sd_loading_sound', text='聆听结束', icon='CANCEL')
    else:
        layout.operator('sd.sound_loader', text='嘉然之声', icon='PLAY')


def register():
    bpy.types.Scene.sd_thumbnails = EnumProperty(
        items=enum_images)

    bpy.utils.register_class(SD_OT_SoundListAction)
    bpy.utils.register_class(SD_UL_SoundList)
    bpy.utils.register_class(SD_PT_3DViewPanel)

    # bpy.types.TOPBAR_MT_editor_menus.append(draw_top_bar)


def unregister():
    bpy.utils.unregister_class(SD_OT_SoundListAction)
    bpy.utils.unregister_class(SD_UL_SoundList)
    bpy.utils.unregister_class(SD_PT_3DViewPanel)

    del bpy.types.Scene.sd_thumbnails

    # bpy.types.TOPBAR_MT_editor_menus.remove(draw_top_bar)
