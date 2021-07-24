import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, IntProperty, FloatProperty

from .preferences import get_pref
from .util import SD_Preview

img_preview = SD_Preview()
img_enums = img_preview.register()

friendly_names = {'LEFTMOUSE': 'Left', 'RIGHTMOUSE': 'Right', 'MIDDLEMOUSE': 'Middle',
                  'WHEELUPMOUSE': "Mouse wheel up", "WHEELDOWNMOUSE": "Mouse wheel down",
                  'ESC': 'Esc', 'RET': 'Enter', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
                  'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'ZERO': '0',
                  'COMMA': 'Comma', 'PERIOD': 'Period',
                  'NONE': '无'}


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
    bl_label = '添加'

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


class SD_PT_3DViewPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '嘉然之声'
    bl_label = ''
    bl_options = {'HEADER_LAYOUT_EXPAND'} # "DRAW_BOX"

    def draw_header(self, context):
        layout = self.layout
        pref = get_pref()

        layout.prop(pref, 'title', text='', emboss=True if context.window_manager.sd_show_pref else False)
        layout.prop(context.window_manager, 'sd_show_pref', icon='PREFERENCES', text='', emboss=False)
        layout.separator(factor=0.5)

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        col = layout.column()

        # 观想位
        col.template_icon_view(context.scene, "sd_thumbnails", scale=context.scene.sd_image_scale)
        col.separator(factor=0.5)

        # 启动/停止
        row = col.row()
        row.scale_y = 1.5
        if context.window_manager.sd_loading_sound:
            row.prop(context.window_manager, 'sd_loading_sound', text='停止聆听', icon='CANCEL')
        else:
            row.operator('sd.sound_loader', text='嘉然之声', icon='PLAY')

        if not context.window_manager.sd_looping_image:
            row.operator('sd.image_player', text='观想嘉然', icon='PLAY')
        else:
            row.prop(context.window_manager, 'sd_looping_image', text='停止观想', icon='CANCEL')

        # 设置
        ##################

        if context.window_manager.sd_show_pref:
            col.separator(factor=0.5)

            box = col.box()
            row = box.split(factor=0.6)
            row.label(text='观想设置', icon='IMAGE_DATA')
            row.operator('sd.open_folder',text='文件夹',emboss=False,icon='FILEBROWSER')
            row = box.row()
            row.prop(context.scene, 'sd_image_scale', slider=1)
            row.prop(context.scene, 'sd_image_interval')

            box = col.box()
            row = box.split(factor=0.6)
            row.label(text='聆听设置', icon='PLAY_SOUND')
            row.operator('sd.batch_import', text='批量导入',emboss=False,icon='FILEBROWSER')
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

        col3 = col1.column(align=1)
        col3.operator('sd.sound_list_action', icon='TRASH', text='').action = 'CLEAR'

        # Current item
        #########################
        if len(pref.sound_list) == 0: return None
        item = pref.sound_list[pref.sound_list_index]

        col = col.column(align=1).box()
        col.use_property_split = 1
        col.use_property_decorate = 0
        col.label(icon='EDITMODE_HLT', text='编辑项')

        # base info
        col.prop(item, 'enable', text='启用音频')
        col.prop(item, 'name', text='名称')
        col.prop(item, 'path', icon='SOUND', text='音频路径')

        # details
        details = col.box()
        col = details.column()
        col.use_property_decorate = True
        col.use_property_split = False

        col.label(text='按键绑定', icon='KEYINGSET')

        if context.window_manager.sd_listening:
            col.prop(context.window_manager, 'sd_listening', text='按一个按键，可组合Ctrl/Shift/Alt', toggle=1)
        else:
            row = col.split(factor=0.6)
            row.operator('sd.get_event', text=friendly_names[item.key] if item.key in friendly_names else item.key)
            row1 = row.row(align=1)
            row1.scale_x = 1.25
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
        items=img_enums)

    bpy.types.Scene.sd_image_scale = FloatProperty(name='照片缩放', default=8, min=3, soft_min=5, soft_max=11)
    bpy.types.Scene.sd_image_interval = FloatProperty(name='时间间隔', default=1, min=0.01, soft_min=0.1, soft_max=3)
    bpy.types.WindowManager.sd_show_pref = BoolProperty(name='设置', default=False)

    bpy.utils.register_class(SD_OT_SoundListAction)
    bpy.utils.register_class(SD_UL_SoundList)
    bpy.utils.register_class(SD_PT_3DViewPanel)

    # bpy.types.TOPBAR_MT_editor_menus.append(draw_top_bar)


def unregister():
    img_preview.unregister()
    del bpy.types.Scene.sd_thumbnails

    bpy.utils.unregister_class(SD_OT_SoundListAction)
    bpy.utils.unregister_class(SD_UL_SoundList)
    bpy.utils.unregister_class(SD_PT_3DViewPanel)

    # bpy.types.TOPBAR_MT_editor_menus.remove(draw_top_bar)
