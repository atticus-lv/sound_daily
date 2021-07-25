import bpy
import os

from bpy.props import EnumProperty, StringProperty, BoolProperty, CollectionProperty, IntProperty, FloatProperty

from ..util import KeyController, MusicPlayer
from ..util import ignored_keys, allowed_mouse_types, get_pref


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
            self.player = MusicPlayer(item.path)
            self.player.play()


class SD_OT_ImagePlayer(bpy.types.Operator):
    bl_idname = 'sd.image_player'
    bl_label = '图片轮替'

    _timer = None
    name_list = None

    @classmethod
    def poll(cls, context):
        return len(get_pref().image_dir_list) != 0  # only show when image list is not empty

    def invoke(self, context, event):
        pref = get_pref()
        curr_item = pref.image_dir_list[pref.image_dir_list_index]
        # get name of all the items
        self.name_list = [file_name for file_name in os.listdir(curr_item.path) if
                          os.path.isfile(os.path.join(curr_item.path, file_name))]
        # set state and add modal handle
        context.window_manager.sd_looping_image = 1
        self._timer = context.window_manager.event_timer_add(time_step=context.scene.sd_image_interval,
                                                             window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            self.next_image(context)
            context.area.tag_redraw()  # redraw for smooth performance

            if context.window_manager.sd_looping_image == 0:  # stop when user change the state value
                context.window_manager.event_timer_remove(self._timer)
                return {"FINISHED"}

        return {"PASS_THROUGH"}

    def next_image(self, context):
        pref = get_pref()
        curr_dir_item = pref.image_dir_list[pref.image_dir_list_index]
        curr_img = curr_dir_item.thumbnails  # get image thumbnails

        try:
            curr_index = self.name_list.index(curr_img)
        except Exception as e:  # include len is 0
            curr_index = None
        if curr_index is None: return None

        # loop index and set image
        if curr_index < len(self.name_list) - 1:
            curr_dir_item.thumbnails = self.name_list[curr_index + 1]
        elif curr_index == len(self.name_list) - 1:
            curr_dir_item.thumbnails = self.name_list[0]


def close_settings_panel(self, context):
    context.window_manager.sd_show_pref = False


def register():
    bpy.utils.register_class(SD_OT_SoundLoader)
    bpy.utils.register_class(SD_OT_ImagePlayer)

    # global state
    #######################
    bpy.types.WindowManager.sd_listening = BoolProperty(default=False)  # keymap state
    bpy.types.WindowManager.sd_loading_sound = BoolProperty(default=False)  # sound state
    bpy.types.WindowManager.sd_looping_image = BoolProperty(default=False)  # image state


def unregister():
    bpy.utils.unregister_class(SD_OT_SoundLoader)
    bpy.utils.unregister_class(SD_OT_ImagePlayer)

    del bpy.types.WindowManager.sd_listening
    del bpy.types.WindowManager.sd_loading_sound
    del bpy.types.WindowManager.sd_looping_image
