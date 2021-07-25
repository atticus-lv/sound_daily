import bpy

from ..util import KeyController, MusicPlayer
from ..util import ignored_keys, get_pref


class SD_OT_SoundLoader(bpy.types.Operator):
    """播放一段绑定的音频"""
    bl_idname = "sd.sound_loader"
    bl_label = "Sound Loader"

    key_input = None
    player = None

    def _runtime(self, context):
        return context.window_manager.sd_loading_sound

    def append_handle(self, context):
        context.window_manager.modal_handler_add(self)
        context.window_manager.sd_loading_sound = 1

    def invoke(self, context, event):
        if len(get_pref().sound_list) == 0: return {'FINISHED'}

        self.key_input = KeyController()
        self.append_handle(context)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if self._runtime(context) is False: return {"FINISHED"}

        self.detect_keyboard_and_play(event)

        return {"PASS_THROUGH"}

    def detect_keyboard_and_play(self, event):
        if event.value == "PRESS" and event.type not in ignored_keys:
            item = self.key_input.get_binds_item(event)
            if not item: return None

            self.player = MusicPlayer(item.path)
            self.player.play()


def register():
    bpy.utils.register_class(SD_OT_SoundLoader)


def unregister():
    bpy.utils.unregister_class(SD_OT_SoundLoader)
