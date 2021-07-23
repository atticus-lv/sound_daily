import bpy

from bpy.props import EnumProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty

from .preferences import get_pref
from .util import KeyController, MusicPlayer
from .util import ignored_keys, allowed_mouse_types


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
            return {"FINISHED"}

        return {"PASS_THROUGH"}

    def detect_keyboard(self, event):
        if event.value == "PRESS" and event.type not in ignored_keys:
            self.key_input.set_item_keymap(self.item, event)
            bpy.context.window_manager.sd_listening = 0


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
            path = self.key_input.get_binds_path(event)
            self.player = MusicPlayer(path)
            self.player.play()



def register():
    bpy.utils.register_class(SD_OT_SetKeymap)
    bpy.utils.register_class(SD_OT_SoundLoader)

    bpy.types.WindowManager.sd_listening = BoolProperty(default=False)
    bpy.types.WindowManager.sd_loading_sound = BoolProperty(default=False)


def unregister():
    bpy.utils.unregister_class(SD_OT_SetKeymap)
    bpy.utils.unregister_class(SD_OT_SoundLoader)

    del bpy.types.WindowManager.sd_listening
    del bpy.types.WindowManager.sd_loading_sound
