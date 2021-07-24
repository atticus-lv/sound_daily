import bpy
import os

from bpy_extras.io_utils import ExportHelper
from bpy.props import EnumProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty, FloatProperty

from .preferences import get_pref, SD_Preference
from .util import KeyController, MusicPlayer
from .util import ignored_keys, allowed_mouse_types

from . import __folder_name__


class SD_OT_SetKeymap(bpy.types.Operator):
    """按下以设置绑定键"""
    bl_idname = "sd.get_event"
    bl_label = "Get event"

    item = None
    key_input = None

    def append_handle(self):
        bpy.context.window_manager.modal_handler_add(self)

    def remove_handle(self):
        pass

    def invoke(self, context, event):
        pref = get_pref()
        if len(pref.sound_list) == 0: return {'FINISHED'}

        self.key_input = KeyController()
        # start listening
        context.window_manager.sd_listening = 1
        self.append_handle()
        self.item = pref.sound_list[pref.sound_list_index]

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.detect_keyboard(event)

        if context.window_manager.sd_listening == 0:
            context.area.tag_redraw()
            return {"FINISHED"}

        return {"PASS_THROUGH"}

    def detect_keyboard(self, event):
        if event.value == "PRESS" and event.type not in ignored_keys:
            self.key_input.set_item_keymap(self.item, event)
            bpy.context.window_manager.sd_listening = 0
            bpy.context.area.tag_redraw()


class SD_OT_SoundLoader(bpy.types.Operator):
    """"""
    bl_idname = "sd.sound_loader"
    bl_label = "Sound Loader"

    key_input = None
    player = None

    def append_handle(self):
        bpy.context.window_manager.modal_handler_add(self)

    def remove_handle(self):
        pass

    def invoke(self, context, event):
        pref = get_pref()
        if len(pref.sound_list) == 0: return {'FINISHED'}

        self.key_input = KeyController()

        # start listening
        context.window_manager.sd_loading_sound = 1
        self.append_handle()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.detect_keyboard_and_play(event)

        if context.window_manager.sd_loading_sound == 0:
            return {"FINISHED"}

        return {"PASS_THROUGH"}

    def detect_keyboard_and_play(self, event):
        if event.value == "PRESS" and event.type not in ignored_keys:
            item = self.key_input.get_binds_item(event)
            if not item: return None
            if item.ctrl == event.ctrl and item.shift == event.shift and item.alt == event.alt:
                self.player = MusicPlayer(item.path)
                self.player.play()



class SD_OT_BatchImport(bpy.types.Operator, ExportHelper):
    """批量导入音频"""
    bl_idname = 'sd.batch_import'
    bl_label = '批量导入'

    # build-in
    filename_ext = ''

    files: CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement)

    directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        self.add_sound()
        context.area.tag_redraw()
        return {'FINISHED'}

    def add_image(self):
        pass

    def add_sound(self):
        for file_elem in self.files:
            filepath = os.path.join(self.directory, file_elem.name)
            bpy.ops.sd.sound_list_action(action='ADD',
                                         path=filepath,
                                         name=file_elem.name, )


class SD_OT_ImagePlayer(bpy.types.Operator):
    bl_idname = 'sd.image_player'
    bl_label = '图片轮替'

    name_list = None
    _timer = None

    def append_handle(self):
        self._timer = bpy.context.window_manager.event_timer_add(bpy.context.scene.sd_image_interval,
                                                                 window=bpy.context.window)
        bpy.context.window_manager.modal_handler_add(self)

    def remove_handle(self):
        bpy.context.window_manager.event_timer_remove(self._timer)

    def invoke(self, context, event):
        from .ui_panel import img_enums
        self.name_list = [item[0] for item in img_enums]  # name,path,icon_id
        # start listening
        context.window_manager.sd_looping_image = 1
        self.append_handle()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            self.next_image(context)
            context.area.tag_redraw()

            if context.window_manager.sd_looping_image == 0:
                self.remove_handle()
                return {"FINISHED"}

        return {"PASS_THROUGH"}

    def next_image(self, context):
        curr_img = context.scene.sd_thumbnails

        try:
            curr_index = self.name_list.index(curr_img)
        except Exception as e:  # include len is 0
            curr_index = None
        if curr_index is None: return None

        # loop
        if curr_index < len(self.name_list) - 1:
            context.scene.sd_thumbnails = self.name_list[curr_index + 1]
        elif curr_index == len(self.name_list) - 1:
            context.scene.sd_thumbnails = self.name_list[0]


class SD_OT_OpenFolder(bpy.types.Operator):
    """打开文件夹"""
    bl_idname = 'sd.open_folder'
    bl_label = 'Open Folder'

    def execute(self, context):
        addon_folder = os.path.join(bpy.utils.user_resource('SCRIPTS'), "addons", __folder_name__)
        os.startfile(os.path.join(addon_folder, 'res', 'img'))
        return {"FINISHED"}


def close_settings_panel(self, context):
    context.window_manager.sd_show_pref = False


def register():
    bpy.utils.register_class(SD_OT_SetKeymap)
    bpy.utils.register_class(SD_OT_SoundLoader)
    bpy.utils.register_class(SD_OT_BatchImport)
    bpy.utils.register_class(SD_OT_ImagePlayer)
    bpy.utils.register_class(SD_OT_OpenFolder)

    bpy.types.WindowManager.sd_listening = BoolProperty(default=False)
    bpy.types.WindowManager.sd_loading_sound = BoolProperty(default=False)
    bpy.types.WindowManager.sd_looping_image = BoolProperty(default=False)


def unregister():
    bpy.utils.unregister_class(SD_OT_SetKeymap)
    bpy.utils.unregister_class(SD_OT_SoundLoader)
    bpy.utils.unregister_class(SD_OT_BatchImport)
    bpy.utils.unregister_class(SD_OT_ImagePlayer)
    bpy.utils.unregister_class(SD_OT_OpenFolder)

    del bpy.types.WindowManager.sd_listening
    del bpy.types.WindowManager.sd_loading_sound
    del bpy.types.WindowManager.sd_looping_image
