import os
import json
from functools import partial
import maya.cmds as cmds

class CenterStage(object):
    """
    Tool for setting up scenes for WebToons.
    """
    def __init__(self):
        self.center_stage_root_directory = r'C:\dev\maya_tools\center_stage'
        self.scale_scene = os.path.join(self.center_stage_root_directory, 'porchai_scale.ma')

        self.center_stage_config = os.path.join(self.center_stage_root_directory, 'center_stage_config.txt')
        self.render_width = 0.0
        self.render_height = 0.0
        self.aspect_ratio = 1.0

        self.target_object_list = []

        # list of extra utilities used to populate buttons in GUI
        self.utility_list = [('Face Forward', self.face_forward),
                             ('Min Y', self.min_y),
                             ('Set Render Size',self.set_render_size),
                             ('Reference Scale Scene', self.reference_scale_scene),
                             ('Remove Reference Scale Scene', self.remove_reference_scale_scene)
                             ]

    def set_initial_state(self):
        open(self.center_stage_config, 'w')
        with open(self.center_stage_config, 'w') as text_file:
            text_file.write('Some text')
            # json.dump(self.center_stage_config_directory, txtfile)

        # with open(self.center_stage_config, 'r') as f:
        #     center_stage_config_read = json.load(f)
        # cmds.textField('center_stage_path_field', edit=True, text=center_stage_config_read)
        # if center_stage_config_read:
        #     self.refresh_scroll_list(center_stage_config_read)
        # else:
        #     cmds.warning('No image files in selected directory')

    def update_center_stage_config(self): #, file_path):
        print 'YYYOOOO'
        # with open(self.center_stage_config, 'w') as txtfile:
        #     json.dump(file_path, txtfile)

    @staticmethod
    def create_camera():
        print ''

    def face_forward(self, *args):
        self.target_object_list = cmds.ls(selection=True)
        for target_object in self.target_object_list:
            cmds.setAttr("{0}.rotateX".format(target_object), 90)

    def min_y(self, *args):
        self.target_object_list = cmds.ls(selection=True)
        for target_object in self.target_object_list:
            target_bounding_box = cmds.xform(target_object, query=True, worldSpace=True, boundingBox=True)
            cmds.xform(worldSpace=True, preserve=True, centerPivots=True)
            target_center = cmds.xform(target_object, query=True, scalePivot=True)
            cmds.xform(target_object, worldSpace=True,
                       pivots=[target_center[0], target_bounding_box[1], target_center[2]])
            cmds.move(y=0, rotatePivotRelative=True)

    def set_render_size(self, *args):
        self.render_width = cmds.getAttr('panel_ratio_calculator.render_width')
        self.render_height = cmds.getAttr('panel_ratio_calculator.render_height')
        self.aspect_ratio = cmds.getAttr('panel_ratio_calculator.aspect_ratio')
        cmds.setAttr('defaultResolution.width', self.render_width)
        cmds.setAttr('defaultResolution.height', self.render_height)

        cmds.setAttr('defaultResolution.pixelAspect', 1)
        cmds.setAttr('defaultResolution.deviceAspectRatio', self.aspect_ratio)
        print 'pooooooooooooo'

    def reference_scale_scene(self, *args):
        cmds.file(self.scale_scene, reference=True)

    def remove_reference_scale_scene(self, *args):
        cmds.file(self.scale_scene, removeReference=True)

    def build_gui(self):
        # If window already exists, deletes all preferences and kills it
        if cmds.window("center_stage_win", exists=True):
            self.close_window()

        # window preferences
        win_main = cmds.window("center_stage_win", title="Centre Stage", sizeable=True)

        # window layout
        cmds.frameLayout(label='Panel Width', collapsable=True, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField('panel_width_field', width=470, alwaysInvokeEnterCommandOnReturn=True,
                       enterCommand=lambda maya_false: self.update_center_stage_config())

        cmds.frameLayout(label='Utilities', collapsable=True, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        for label, function in self.utility_list:
            cmds.button(label + '_button', h=40, w=250, label=label, command=partial(function))

        cmds.setParent("..")
        cmds.showWindow(win_main)

    @staticmethod
    def close_window():
        cmds.deleteUI("center_stage_win")
        cmds.windowPref("center_stage_win", removeAll=True)

    def run_center_stage(self):
        self.build_gui()
        self.set_initial_state()