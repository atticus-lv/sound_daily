import bpy
from bpy.props import BoolProperty


def register():
    bpy.types.WindowManager.sd_listening = BoolProperty(default=False)  # keymap state
    bpy.types.WindowManager.sd_loading_sound = BoolProperty(default=False)  # sound state
    bpy.types.WindowManager.sd_looping_image = BoolProperty(default=False)  # image state


def unregister():
    del bpy.types.WindowManager.sd_listening
    del bpy.types.WindowManager.sd_loading_sound
    del bpy.types.WindowManager.sd_looping_image
