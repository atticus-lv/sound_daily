import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, IntProperty, FloatProperty

from .util import get_pref

friendly_names = {'LEFTMOUSE': 'Left', 'RIGHTMOUSE': 'Right', 'MIDDLEMOUSE': 'Middle',
                  'WHEELUPMOUSE': "Mouse wheel up", "WHEELDOWNMOUSE": "Mouse wheel down",
                  'ESC': 'Esc', 'RET': 'Enter', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
                  'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9', 'ZERO': '0',
                  'COMMA': 'Comma', 'PERIOD': 'Period',
                  'NONE': '无'}


class SD_OT_ImageDirSelector(bpy.types.Operator):
    bl_idname = "sd.image_dir_selector"
    bl_label = 'Select'
    bl_options = {'REGISTER', 'UNDO'}

    dir_name: StringProperty()

    def execute(self, context):
        pref = get_pref()
        i = 0

        for item in pref.image_dir_list:
            if item.name == self.dir_name:
                pref.image_dir_list_index = i
                break
            else:
                i += 1

        return {'FINISHED'}


class SD_MT_ImageFolderSwitcher(bpy.types.Menu):
    bl_label = "Select a camera to enter"
    bl_idname = "SD_MT_ImageFolderSwitcher"

    @classmethod
    def poll(cls, context):
        return len(get_pref().image_dir_list) > 0

    def draw(self, context):
        layout = self.layout
        pref = get_pref()

        for item in pref.image_dir_list:
            switch = layout.operator("sd.image_dir_selector", text=item.name)
            switch.dir_name = item.name


class SD_PT_MainViewPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '嘉然之声'
    bl_label = ''
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw_header(self, context):
        layout = self.layout
        pref = get_pref()

        layout.prop(pref, 'title', text='', emboss=True if context.window_manager.sd_show_pref else False)
        layout.prop(context.window_manager,'sd_show_pref',icon = 'PREFERENCES',emboss=False,text='')
        layout.separator(factor=0.5)

    def draw(self, context):
        layout = self.layout
        pref = get_pref()
        col = layout.column()

        # 观想位
        item = pref.image_dir_list[pref.image_dir_list_index] if len(pref.image_dir_list) != 0 else None
        if item:
            col.template_icon_view(item, "thumbnails", scale=context.scene.sd_image_scale)
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
            # row.menu("SD_MT_ImageFolderSwitcher", text="", icon='COLLAPSEMENU') # 弹出列表选择
        else:
            row.prop(context.window_manager, 'sd_looping_image', text='停止观想', icon='CANCEL')

        # 贴花
        decal = col.operator('sd.image_decal')
        curr_dir_item = pref.image_dir_list[pref.image_dir_list_index]
        decal.image_name = curr_dir_item.thumbnails
        decal.image_dir_path = curr_dir_item.path

class SD_PT_ImageSettingPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '嘉然之声'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_label = '观想设置'
    bl_icon = 'IMAGE_DATA'

    @classmethod
    def poll(self, context):
        return context.window_manager.sd_show_pref

    def draw(self, context):
        pref = get_pref()
        col = self.layout.column()
        # Image setting
        row = col.box().row()
        row.prop(context.scene, 'sd_image_scale', slider=1)
        row.prop(context.scene, 'sd_image_interval', slider=1)
        col.separator(factor=0.5)
        # Image List
        #########################
        row = col.split(factor=0.75)
        row.label(text='文件夹列表',icon='FILE_FOLDER')
        # row.operator('sd.batch_import',).add_type = 'IMG' # TODO 等待修复

        row = col.row()
        row.template_list(
            'SD_UL_ImageList', 'Image List',
            pref, 'image_dir_list',
            pref, 'image_dir_list_index')

        col1 = row.column()
        col2 = col1.column(align=1)
        col2.operator('sd.image_list_action', icon='ADD', text='').action = 'ADD'
        col2.operator('sd.image_list_action', icon='REMOVE', text='').action = 'REMOVE'

        col2 = col1.column(align=1)
        col2.operator('sd.image_list_action', icon='TRIA_UP', text='').action = 'UP'
        col2.operator('sd.image_list_action', icon='TRIA_DOWN', text='').action = 'DOWN'

        col3 = col1.column(align=1)
        col3.operator('sd.image_list_action', icon='TRASH', text='').action = 'CLEAR'


class SD_PT_SoundSettingPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '嘉然之声'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_label = '聆听设置'
    bl_icon = 'PLAY_SOUND'

    @classmethod
    def poll(self,context):
        return context.window_manager.sd_show_pref

    def draw(self, context):
        pref = get_pref()
        col = self.layout.column()
        # Sound List
        #########################
        row = col.split(factor=0.75)
        row.label(text='文件列表',icon='FILE')
        row.operator('sd.batch_import').add_type = 'SOUND'

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

        col = col.box().split().column(align=1)
        col.use_property_split = 1
        col.use_property_decorate = 0
        col.label(icon='EDITMODE_HLT', text='编辑项')

        # base info
        col.prop(item, 'enable', text='启用音频')
        col.prop(item, 'bind_name_to_path')
        col.prop(item, 'name', text='名称')
        col.prop(item, 'path', icon='SOUND', text='音频路径')

        col.separator(factor=0.5)

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


def register():
    bpy.types.Scene.sd_image_scale = FloatProperty(name='照片缩放', default=8, min=3, soft_min=5, soft_max=11)
    bpy.types.Scene.sd_image_interval = FloatProperty(name='时间间隔', default=0.5, min=0.01, soft_min=0.01, soft_max=3)
    bpy.types.WindowManager.sd_show_pref = BoolProperty(name='设置', default=False)

    bpy.utils.register_class(SD_OT_ImageDirSelector)
    bpy.utils.register_class(SD_MT_ImageFolderSwitcher)
    bpy.utils.register_class(SD_PT_MainViewPanel)
    bpy.utils.register_class(SD_PT_ImageSettingPanel)
    bpy.utils.register_class(SD_PT_SoundSettingPanel)

    # bpy.types.TOPBAR_MT_editor_menus.append(draw_top_bar)


def unregister():
    bpy.utils.unregister_class(SD_OT_ImageDirSelector)
    bpy.utils.unregister_class(SD_MT_ImageFolderSwitcher)
    bpy.utils.unregister_class(SD_PT_MainViewPanel)
    bpy.utils.unregister_class(SD_PT_ImageSettingPanel)
    bpy.utils.unregister_class(SD_PT_SoundSettingPanel)

    # bpy.types.TOPBAR_MT_editor_menus.remove(draw_top_bar)
