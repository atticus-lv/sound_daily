import bpy
import os
import random

from ..util import get_pref


class SD_OT_ImagePlayer(bpy.types.Operator):
    bl_idname = 'sd.image_player'
    bl_label = '图片轮替'

    _timer = None
    name_list = None

    @classmethod
    def poll(cls, context):
        return len(get_pref().image_dir_list) != 0  # only show when image list is not empty

    def _runtime(self, context):
        return context.window_manager.sd_looping_image

    def append_handle(self, context):
        context.window_manager.sd_looping_image = 1
        self._timer = context.window_manager.event_timer_add(time_step=context.scene.sd_image_interval,
                                                             window=context.window)
        context.window_manager.modal_handler_add(self)

    def remove_handle(self,context):
        context.window_manager.event_timer_remove(self._timer)

    def invoke(self, context, event):
        pref = get_pref()
        curr_item = pref.image_dir_list[pref.image_dir_list_index]

        self.name_list = [file_name for file_name in os.listdir(curr_item.path) if  # get name of all the items
                          os.path.isfile(os.path.join(curr_item.path, file_name))]

        self.append_handle(context)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            self.next_image(context)

            if self._runtime(context) is False:
                self.remove_handle(context)
                return {"FINISHED"}

        return {"PASS_THROUGH"}

    def next_image(self, context):
        pref = get_pref()
        curr_item = pref.image_dir_list[pref.image_dir_list_index]
        curr_img = curr_item.thumbnails  # get image thumbnails

        try:
            curr_index = self.name_list.index(curr_img)
        except Exception:  # include len is 0
            return None

        # loop index and set image
        if not pref.rand_image:
            curr_item.thumbnails = self.name_list[curr_index + 1] if curr_index < len(self.name_list) - 1 else self.name_list[0]
        else:
            i = random.randint(0,len(self.name_list) - 1)
            curr_item.thumbnails = self.name_list[i]
        # redraw for smooth performance
        context.area.tag_redraw()


def register():
    bpy.utils.register_class(SD_OT_ImagePlayer)


def unregister():
    bpy.utils.unregister_class(SD_OT_ImagePlayer)
