import bpy
import aud
from .preferences import get_pref

# some setting keys from https://github.com/jayanam/shortcut_VUr
###################################################

ignored_keys = {'LEFT_SHIFT', 'RIGHT_SHIFT', 'LEFT_ALT',
                'RIGHT_ALT', 'LEFT_CTRL', 'RIGHT_CTRL', 'TIMER',
                'MOUSEMOVE', 'EVT_TWEAK_L', 'INBETWEEN_MOUSEMOVE', 'TIMER_REPORT', 'TIMER1',
                'TIMERREGION', 'WINDOW_DEACTIVATE', 'NONE',
                'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE'}  # remove mouse type

clear_events = {'WINDOW_DEACTIVATE', 'TIMER1', 'TIMER_REPORT'}

allowed_mouse_types = {'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE'}


class KeyController():
    def get_event_type(self, event):
        return event.type

    def set_item_keymap(self, item, event):
        item.ctrl = event.ctrl
        item.shift = event.shift
        item.alt = event.alt
        item.key = self.get_event_type(event)

    def get_result(self, event):
        key = self.get_event_type(event)
        return event.ctrl, event.shift, event.alt, key

    def get_binds_item(self, event):
        is_ctrl, is_alt, is_shift, key = self.get_result(event)
        pref = get_pref()
        for item in pref.sound_list:
            if not item.enable: continue
            if item.ctrl == is_ctrl and item.shift == is_shift and item.alt == is_alt and item.key == key:
                return item


class MusicPlayer():
    def __init__(self, music_path):
        self.device = aud.Device()
        self.sound = self.get_music(music_path)

    def get_music(self, path):
        return aud.Sound(path)

    def play(self):
        try:
            self.device.play(self.sound)
            return True
        except Exception:
            return None


# code from another plugin of mine "https://atticus-lv.github.io/RenderStackNode/#/"
import bpy.utils.previews
import os

img_dir = os.path.join(os.path.dirname(__file__), 'res', 'img')
extensions = ('.png', '.jpg', '.jpeg')


class SD_Preview():
    def __init__(self):
        self.preview_collections = {}
        self.enum_items = []

    def register(self):
        pcoll = bpy.utils.previews.new()
        self.preview_collections["sd_icon"] = pcoll

        # Generate the thumbnails
        for i, image_name in enumerate(os.listdir(img_dir)):
            if image_name.endswith(extensions):
                filepath = os.path.join(img_dir, image_name)
                thumb = pcoll.load(image_name, filepath, 'IMAGE')  # name, image_path, type
                self.enum_items.append((image_name, image_name, "", thumb.icon_id, i))

        return self.enum_items

    def unregister(self):
        for pcoll in self.preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        self.preview_collections.clear()

    def get_thumb_image(self, image_name):
        return self.preview_collections["sd_icon"][image_name]

    def get_thumb_image_icon_id(self, image_name):
        thumb = self.get_image(image_name)
        return thumb.icon_id
