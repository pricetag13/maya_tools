import os
import json
from maya import cmds


class AssembleLookAt(object):
    def __init__(self):
        # Get paths
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.lookat_prefab = "{0}/{1}".format(self.root_path, "prefabs/lookat.ma")
        self.set_up_lookat_config = r"{0}/gui/setup_lookat_config.txt".format(self.root_path)

        self.fk_placement_root = "au_eyes_ctl_parent_grp"

        self.root_control = ""
        self.head_transform = ""
        self.left_eye_transform = ""
        self.right_eye_transform = ""

        self.au_61_min = 0
        self.au_61_max = 40
        self.au_62_min = 0
        self.au_62_max = -40
        self.au_63_min = 0
        self.au_63_max = -30
        self.au_64_min = 0
        self.au_64_max = 30

        self.horizontal_axis = ""
        self.vertical_axis = ""

        self.read_values_from_json_config()

    def run_assembly(self):
        self.import_lookat_prefab()
        self.create_lookat_placement_guides()
        self.place_lookat_rig()
        self.create_eye_control_heirarchy()
        self.connect_sightlines()
        self.connect_lookat_rig()
        self.delete_lookat_placement_guides()
        self.place_au_eyes_controls()
        self.constrain_plot_to_lookat()

    def read_values_from_json_config(self):
        with open(self.set_up_lookat_config, 'r') as file_to_read:
            lookat_setup_config_read = json.load(file_to_read)
            self.left_eye_transform = (lookat_setup_config_read['LeftEyeRoot'])
            self.right_eye_transform = (lookat_setup_config_read['RightEyeRoot'])
            self.head_transform = (lookat_setup_config_read['HeadControl'])
            self.root_control = (lookat_setup_config_read['RootControl'])
            self.au_61_max = int((lookat_setup_config_read['OuterRange']))
            self.au_62_max = int((lookat_setup_config_read['InnerRange']))
            self.au_63_max = int((lookat_setup_config_read['UpperRange']))
            self.au_64_max = int((lookat_setup_config_read['LowerRange']))
            self.horizontal_axis = (lookat_setup_config_read['HorizontalAxis'])
            self.vertical_axis = (lookat_setup_config_read['VerticalAxis'])

    @staticmethod
    def snap_objects(objects=None):
        # Snaps lists of objects via parent constraint.
        # Useful for getting center position of two or more objects.
        objects = objects or []
        snap_constraint = cmds.parentConstraint(objects)
        cmds.delete(snap_constraint)

    def import_lookat_prefab(self):
        # Import maya ASCII file that contains all working components for the eye aim rig.
        if not cmds.objExists("grp_control_eyes"):
            cmds.file(self.lookat_prefab, i=True, ignoreVersion=True)
        else:
            print "lookat prefab found in scene."

    def create_lookat_placement_guides(self):
        # Create null guide objects, used to place and orient the eye aim system.
        main_lookat_rig_orient_guide = cmds.group(name='main_lookat_orientGuide', empty=True)
        left_lookat_rig_orient_guide = cmds.group(name='left_lookat_orientGuide', empty=True)
        right_lookat_rig_orient_guide = cmds.group(name='right_lookat_orientGuide', empty=True)
        self.snap_objects([self.left_eye_transform, self.right_eye_transform, main_lookat_rig_orient_guide])
        self.snap_objects([self.left_eye_transform, left_lookat_rig_orient_guide])
        self.snap_objects([self.right_eye_transform, right_lookat_rig_orient_guide])

    @staticmethod
    def delete_lookat_placement_guides():
        # Delete null guide objects, used to place and orient the eye aim system.
        cmds.delete(['main_lookat_orientGuide', 'left_lookat_orientGuide', 'right_lookat_orientGuide'])

    def place_lookat_rig(self):
        # Place the eye aim rig in 3D space according to null guide objects.
        self.snap_objects(['main_lookat_orientGuide', 'lookat_system_orient'])
        self.snap_objects(['main_lookat_orientGuide', 'lookat_system_orient'])
        self.snap_objects(['left_lookat_orientGuide', 'L_lookat_system_orient'])
        self.snap_objects(['left_lookat_orientGuide', 'L_lookat_system_orient'])
        self.snap_objects(['right_lookat_orientGuide', 'R_lookat_system_orient'])
        self.snap_objects(['right_lookat_orientGuide', 'R_lookat_system_orient'])

        # Re-orient "system_orient" groups, to work with control orientation.
        groups_to_orient = ['lookat_system_orient', 'L_lookat_system_orient', 'R_lookat_system_orient']
        for group_ in groups_to_orient:
            axis_values = []
            rotates = ['rx', 'ry', 'rz']
            for axis in rotates:
                axis_value = cmds.getAttr(group_ + '.' + axis)
                axis_values.append(axis_value)
            cmds.setAttr(group_ + '.rx', - axis_values[1])
            cmds.setAttr(group_ + '.ry', 0)
            cmds.setAttr(group_ + '.rz', 0)

    def create_eye_control_heirarchy(self):
        # Place control and rig groups correctly in the scene hierarchy.
        cmds.parent('L_lookat_system_orient', 'lookat_ctl')
        cmds.parent('R_lookat_system_orient', 'lookat_ctl')
        cmds.parent('L_lookat_loc_grp', 'lookat_rig_grp')
        cmds.parent('R_lookat_loc_grp', 'lookat_rig_grp')
        cmds.parent('L_Eye_upVec_grp', 'lookat_rig_grp')
        cmds.parent('R_Eye_upVec_grp', 'lookat_rig_grp')
        cmds.parent('EyeCenter_loc_grp', 'lookat_rig_grp')
        cmds.parent('EyeCenter_upVec_grp', 'lookat_rig_grp')

        cmds.parent('LocalSpace_parent_loc_placement', 'lookat_rig_grp')
        cmds.parent('grp_control_eyes', self.root_control)

    def connect_sightlines(self):
        cmds.parentConstraint('EyeCenter_loc', 'eyes_distance_start')
        cmds.parentConstraint(self.left_eye_transform, 'left_eye_distance_start')
        cmds.parentConstraint(self.right_eye_transform, 'right_eye_distance_start')

    def get_final_connection_list(self):
        final_connection_list = []
        horizontal_axis_tuple = ()
        vertical_axis_tuple = ()
        if self.au_61_max >= 0:
            horizontal_axis_tuple = (self.horizontal_axis, "pos")
        elif self.au_61_max <= 0:
            horizontal_axis_tuple = (self.horizontal_axis, "neg")

        if self.au_64_max >= 0:
            vertical_axis_tuple = (self.vertical_axis, "pos")
        elif self.au_64_max <= 0:
            vertical_axis_tuple = (self.vertical_axis, "neg")
        final_connection_list.append(horizontal_axis_tuple)
        final_connection_list.append(vertical_axis_tuple)
        return final_connection_list

    def connect_lookat_rig(self):
        # Connects custom ranges
        cmds.setAttr('lookat_custom_range_plug.NL_61_Min', self.au_61_min)
        cmds.setAttr('lookat_custom_range_plug.NL_61_Max', self.au_61_max)
        cmds.setAttr('lookat_custom_range_plug.NL_62_Min', self.au_62_min)
        cmds.setAttr('lookat_custom_range_plug.NL_62_Max', self.au_62_max)
        cmds.setAttr('lookat_custom_range_plug.NL_63_Min', self.au_63_min)
        cmds.setAttr('lookat_custom_range_plug.NL_63_Max', self.au_63_max)
        cmds.setAttr('lookat_custom_range_plug.NL_64_Min', self.au_64_min)
        cmds.setAttr('lookat_custom_range_plug.NL_64_Max', self.au_64_max)

        cmds.setAttr('lookat_custom_range_plug.NR_61_Min', self.au_61_min)
        cmds.setAttr('lookat_custom_range_plug.NR_61_Max', self.au_61_max)
        cmds.setAttr('lookat_custom_range_plug.NR_62_Min', self.au_62_min)
        cmds.setAttr('lookat_custom_range_plug.NR_62_Max', self.au_62_max)
        cmds.setAttr('lookat_custom_range_plug.NR_63_Min', self.au_63_min)
        cmds.setAttr('lookat_custom_range_plug.NR_63_Max', self.au_63_max)
        cmds.setAttr('lookat_custom_range_plug.NR_64_Min', self.au_64_min)
        cmds.setAttr('lookat_custom_range_plug.NR_64_Max', self.au_64_max)

        check_final_connection_list = self.get_final_connection_list()
        horizontal_polarity = check_final_connection_list[0][1]
        vertical_polarity = check_final_connection_list[1][1]

        if horizontal_polarity == "pos":
            cmds.connectAttr('final_rotation_output.NL_61_62', "{0}.r{1}".format(self.left_eye_transform,
                                                                                 self.horizontal_axis), force=True)
        elif horizontal_polarity == "neg":
            cmds.connectAttr('final_rotation_output_neg.NL_61_62', "{0}.r{1}".format(self.left_eye_transform,
                                                                                     self.horizontal_axis), force=True)
        if vertical_polarity == "pos":
            cmds.connectAttr('final_rotation_output.NL_63_64', "{0}.r{1}".format(self.left_eye_transform,
                                                                                 self.vertical_axis), force=True)
        if vertical_polarity == "neg":
            cmds.connectAttr('final_rotation_output_neg.NL_63_64', "{0}.r{1}".format(self.left_eye_transform,
                                                                                     self.vertical_axis), force=True)
        if horizontal_polarity == "pos":
            cmds.connectAttr('final_rotation_output.NR_61_62', "{0}.r{1}".format(self.right_eye_transform,
                                                                                 self.horizontal_axis), force=True)
        elif horizontal_polarity == "neg":
            cmds.connectAttr('final_rotation_output_neg.NR_61_62', "{0}.r{1}".format(self.right_eye_transform,
                                                                                     self.horizontal_axis), force=True)
        if vertical_polarity == "pos":
            cmds.connectAttr('final_rotation_output.NR_63_64', "{0}.r{1}".format(self.right_eye_transform,
                                                                                 self.vertical_axis), force=True)
        elif vertical_polarity == "neg":
            cmds.connectAttr('final_rotation_output_neg.NR_63_64', "{0}.r{1}".format(self.right_eye_transform,
                                                                                     self.vertical_axis), force=True)

        # Connect enable lookAt to main visibility control
        cmds.addAttr(self.head_transform, longName="enable_lookat", attributeType='double', min=0, max=1,
                     defaultValue=0, keyable=True)
        cmds.connectAttr('{0}.enable_lookat'.format(self.head_transform), 'au_eyes_ctl.look_at_enabled')
        cmds.connectAttr('{0}.enable_lookat'.format(self.head_transform), 'lookat_enabled_reverse.inputX')

        # Parent constrain the master eye aim group to the "Head" transform
        cmds.parentConstraint(self.head_transform, 'lookat_rig_grp', maintainOffset=True)

        # Aim constrain the local and world eye aim controls to always point toward the "EyeCenter_loc".
        cmds.aimConstraint('EyeCenter_loc', 'lookat_ctl', maintainOffset=True, aimVector=[0, 0, -1],
                           upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0],
                           worldUpObject='EyeCenter_loc')

        # Adds two aim constraints required for the sight line extension feature.
        cmds.aimConstraint(self.left_eye_transform, 'L_sightline_extend_grp', aimVector=[0, 0, -1], upVector=[0, 1, 0],
                           worldUpType="object", worldUpObject='L_sightline_extend_up_vector')
        cmds.aimConstraint(self.right_eye_transform, 'R_sightline_extend_grp', aimVector=[0, 0, -1], upVector=[0, 1, 0],
                           worldUpType="object", worldUpObject='R_sightline_extend_up_vector')

        # Locks rotation on eye aim control
        cmds.setAttr("lookat_ctl.r", lock=True)

    def place_au_eyes_controls(self):
        control_placement_list = [self.left_eye_transform, self.right_eye_transform, self.fk_placement_root]
        self.snap_objects(control_placement_list)
        cmds.setAttr('au_eyes_ctl_placement_offset.tz', 6)
        cmds.parentConstraint(self.head_transform, 'au_eyes_ctl_placement_grp', maintainOffset=True)

    def constrain_plot_to_lookat(self):
        cmds.parentConstraint(self.head_transform, 'C_absolute_direction_constrained_grp', maintainOffset=True)
        cmds.parentConstraint(self.head_transform, 'L_absolute_direction_constrained_grp', maintainOffset=True)
        cmds.parentConstraint(self.head_transform, 'R_absolute_direction_constrained_grp', maintainOffset=True)

        cmds.parentConstraint(self.head_transform, 'convergence_constrained_grp', maintainOffset=True)
