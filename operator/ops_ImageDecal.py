import bpy
import os
import math

from bpy.props import StringProperty
from bpy_extras import view3d_utils
from mathutils import Vector
from ..util import SD_DrawMessage, viewlayer_fix_291


def draw_move_object_callback_px(self, context):
    msg = SD_DrawMessage(font_id=0)
    x_align, y_align = SD_DrawMessage.get_region_size(0.5, 0.03)

    title = '♥ 图 片 贴 花 ♥'
    tips1 = 'R旋转 S缩放 G移动'
    tips2 = "左键确认 | 右键取消"

    offset = 0.5 * msg.get_text_length(title)
    offset1 = 0.5 * msg.get_text_length(tips1)

    msg.draw_title(x=x_align - offset, y=y_align + 150, text=title)
    msg.draw_info(x=x_align - offset1, y=y_align + 125, text=tips1)
    msg.draw_info(x=x_align - offset1, y=y_align + 100, text=tips2)


class SD_OT_ImageDecal(bpy.types.Operator):
    """Move Object"""
    bl_idname = "sd.image_decal"
    bl_label = "贴 花"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'}

    # Image
    image_name: StringProperty()
    image_dir_path: StringProperty()

    # state
    scale_mode = False
    rotate_mode = False

    # rayCast
    object = None  # image object
    view_point = None
    view_vector = None
    world_loc = None  # RayCast world loc
    rc_target_pos = None  # RayCast location on target object
    rc_target_normal = None  # RayCast normal on target object

    up = Vector((0, 0, 1))

    @classmethod
    def poll(self, context):
        return context.area.type == 'VIEW_3D'  # in 3dView

    def append_handle(self, context):
        """draw_handler_add / modal add"""
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_move_object_callback_px, args, 'WINDOW',
                                                              'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

    def add_image_mesh(self, context):
        bpy.ops.import_image.to_plane(
            files=[{"name": self.image_name}],
            directory=self.image_dir_path,
            relative=False)

        self.image_mesh = context.object
        self.image_mesh.hide_viewport = 1

    def invoke(self, context, event):
        if not os.path.isfile(os.path.join(self.image_dir_path, self.image_name)): return {"CANCELLED"}

        # TODO 参考图/贴花切换选项（或者其他方式）

        # image Mesh
        self.add_image_mesh(context)
        image_size = self.image_mesh.dimensions.x

        # use empty object to prevent rayCast ans shading problem
        bpy.ops.object.load_reference_image(filepath=os.path.join(self.image_dir_path, self.image_name))
        self.object = context.object
        self.object.empty_display_size = 1  # restore size
        self.object.scale = (image_size, image_size, image_size)

        # rotate
        self.mouse_pos = [0, 0]
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y

        self.append_handle(context)

        return {'RUNNING_MODAL'}

    def restore_mouse(self, event):
        # reset
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y

    def modal(self, context, event):
        context.area.tag_redraw()  # redraw

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"} or event.alt:
            return {'PASS_THROUGH'}

        # core event
        elif event.type in {"MOUSEMOVE", "R", "S","G"}:

            # set rotate mode
            ##########################
            if event.value == 'PRESS' and event.type in {'R', 'S', 'G'}:
                # restore when first active
                self.restore_mouse(event)

                if event.type == 'R':
                    self.scale_mode = False  # set scale False
                    if self.rotate_mode is False:
                        self.rotate_mode = True
                        context.window.cursor_modal_set('MOVE_X')
                    else:
                        self.rotate_mode = False
                        context.window.cursor_modal_restore()

                elif event.type == 'S':
                    self.rotate_mode = False  # set rotate False
                    if self.scale_mode is False:
                        self.scale_mode = True
                        context.window.cursor_modal_set('MOVE_X')
                    else:
                        self.scale_mode = False
                        context.window.cursor_modal_restore()

                elif event.type == 'G':
                    self.rotate_mode = False
                    self.scale_mode = False

            # rotate mode
            if self.rotate_mode or self.scale_mode:
                self.mouseDX = self.mouseDX - event.mouse_x
                self.mouseDY = self.mouseDY - event.mouse_y

                multiplier = 0.01 if event.shift else 0.2  # accurate rotate

                if self.rotate_mode:
                    self.object.rotation_euler.rotate_axis("Z", math.radians(self.mouseDX * multiplier))
                if self.scale_mode:
                    offset = self.mouseDX * multiplier * -0.1
                    scale = self.object.scale
                    self.object.scale = (scale.x + offset, scale.y + offset, scale.z + offset)

                self.restore_mouse(event)
            # Move Mode
            else:
                self.rc_target_normal = self.up
                result, target_obj = self.ray_cast(context, event)

                if result:
                    world_mat_inv = target_obj.matrix_world.inverted()
                    # Calculates the ray direction in the target space
                    rc_origin = world_mat_inv @ self.view_point
                    rc_destination = world_mat_inv @ self.world_loc
                    rc_direction = (rc_destination - rc_origin).normalized()
                    # second hit to get the matrix normal
                    hit, loc, norm, index = target_obj.ray_cast(origin=rc_origin, direction=rc_direction)
                    self.loc_on_target_obj = loc

                    norm.rotate(target_obj.matrix_world.to_euler('XYZ'))
                    self.rc_target_normal = norm.normalized()
                    self.world_loc = (target_obj.matrix_world @ loc) + self.rc_target_normal * 0.05

                self.object.location = self.world_loc
                self.object.rotation_euler = self.up.rotation_difference(self.rc_target_normal).to_euler()

        # TODO 连续贴花选项
        # elif event.type in {"C"} and event.value == "PRESS":
        #     new_data = self.object.data.copy()
        #     new_object = bpy.data.objects.new(self.object.name, new_data)
        #     new_object.location = self.object.location
        #     new_object.rotation_euler = self.object.rotation_euler
        #     bpy.context.collection.objects.link(new_object)

        # cancel event
        elif event.type in {'ESC', "RIGHTMOUSE"}:
            bpy.data.objects.remove(self.object)
            # remove draw_handler_add
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.window.cursor_modal_restore()
            self.report({'INFO'}, "嘉心糖屁用没有！")
            return {'CANCELLED'}

        # confirm event
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # transfer empty to mesh
            self.image_mesh.hide_viewport = 0
            self.image_mesh.rotation_euler = self.object.rotation_euler
            self.image_mesh.scale = self.object.scale
            bpy.data.objects.remove(self.object)

            context.view_layer.objects.active = self.image_mesh
            self.image_mesh.select_set(True)
            # set location
            self.image_mesh.location = self.world_loc
            # remove
            context.window.cursor_modal_restore()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.report({'INFO'}, "贴贴！")
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def ray_cast(self, context, event, start_point=None):
        self.mouse_pos = event.mouse_region_x, event.mouse_region_y
        # base rayCast info
        scene = context.scene
        region = context.region
        region3D = context.space_data.region_3d
        viewlayer = viewlayer_fix_291(self, context)

        # The direction indicated by the mouse position from the current view / The view point of the user
        self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
        self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
        # The 3D location in this direction
        self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)
        # first hit to get target obj
        if not start_point: start_point = self.view_point
        result, location, normal, index, target_obj, matrix = scene.ray_cast(viewlayer, start_point,
                                                                             self.view_vector)
        return result, target_obj


def register():
    bpy.utils.register_class(SD_OT_ImageDecal)


def unregister():
    bpy.utils.unregister_class(SD_OT_ImageDecal)
