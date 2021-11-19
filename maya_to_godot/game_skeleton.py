import maya.cmds as cmds
from collections import OrderedDict

import anim_utils

# TODO: Remove reload
import importlib
importlib.reload(anim_utils)


class CreateGameSkeleton(object):
    """
    Creates a skeleton for getting animation from Advanced Skeleton into the Godot engine
    """

    def __init__(self, rig_skeleton=None,
                 root_control=None,
                 game_prefix=None):

        self.source_deformation_parent = rig_skeleton
        self.root_control = root_control
        self.game_skeleton_prefix = game_prefix

        self.source_joints_dict = OrderedDict()
        self.trajectory_joint = "Trajectory"
        self.root_offset_joint = "RootOffset"

        # Queries maya unit settings
        self.scene_angles = anim_utils.get_maya_unit_settings()["Angles"]
        self.scene_lengths = anim_utils.get_maya_unit_settings()["Lengths"]

    def get_source_deformation_joints(self):
        source_deformation_joints = []
        child_joints = cmds.listRelatives(self.source_deformation_parent, type="joint")
        source_deformation_joints.extend(child_joints)
        for child_joint in child_joints:
            cmds.select(clear=True)
            cmds.select(child_joint)
            cmds.SelectHierarchy()
            descendants = cmds.ls(selection=True, type="joint")
            source_deformation_joints.extend(descendants)
        return source_deformation_joints

    def add_trajectory_to_rig_skeleton(self):
        rig_skeleton_root = self.get_source_deformation_joints()[0]

        # Create "Trajectory" joint
        cmds.select(clear=True)
        trajectory_joint = cmds.joint(name=self.trajectory_joint)
        cmds.parent(trajectory_joint, self.source_deformation_parent)

        # Create "RootOffset" joint
        root_offset_joint = cmds.joint(name=self.root_offset_joint)
        cmds.matchTransform(root_offset_joint, rig_skeleton_root, position=True, rotation=True)
        cmds.parent(rig_skeleton_root, root_offset_joint)

        # Constrain "Trajectory" to root control
        cmds.parentConstraint(self.root_control, trajectory_joint, maintainOffset=True)

    def create_source_joints_dict(self):
        for source_joint in self.get_source_deformation_joints():
            game_joint = "{0}{1}".format(self.game_skeleton_prefix, source_joint)
            parent_joint = None
            game_parent_joint = None
            parent_transform = cmds.listRelatives(source_joint, parent=True)[0]
            if parent_transform:
                parent_type = cmds.nodeType(parent_transform)
                if parent_type == "joint":
                    parent_joint = parent_transform
                    game_parent_joint = "{0}{1}".format(self.game_skeleton_prefix, parent_transform)
            self.source_joints_dict[source_joint] = (parent_joint, game_joint, game_parent_joint)

    def create_game_joints(self):
        # Create each joint and match position
        for joint_, data in self.source_joints_dict.items():
            cmds.select(clear=True)
            game_joint = cmds.joint(name=data[1])
            cmds.matchTransform(game_joint, joint_, position=True, rotation=True)

        for joint_, data in self.source_joints_dict.items():
            # Create hierarchy
            game_joint = data[1]
            game_joint_parent = data[2]

            if game_joint != "{0}{1}".format(self.game_skeleton_prefix, self.trajectory_joint):
                if game_joint_parent:
                    cmds.parent(game_joint, game_joint_parent)
                else:
                    cmds.parent(game_joint, "{0}{1}".format(self.game_skeleton_prefix, self.root_offset_joint))

            # Kill joint orients
            cmds.makeIdentity(game_joint, apply=True)

            orients = cmds.getAttr("{0}.jointOrient".format(game_joint))[0]
            rotates = cmds.getAttr("{0}.rotate".format(game_joint))[0]
            result_x = orients[0] + rotates[0]
            result_y = orients[1] + rotates[1]
            result_z = orients[2] + rotates[2]

            cmds.setAttr("{0}.jointOrient".format(game_joint), 0, 0, 0)

            cmds.setAttr("{0}.rx".format(game_joint), result_x)
            cmds.setAttr("{0}.ry".format(game_joint), result_y)
            cmds.setAttr("{0}.rz".format(game_joint), result_z)

            # Save rest rotation values in preferredAngle
            cmds.setAttr("{0}.preferredAngleX".format(game_joint), result_x)
            cmds.setAttr("{0}.preferredAngleY".format(game_joint), result_y)
            cmds.setAttr("{0}.preferredAngleZ".format(game_joint), result_z)

            # Save rest translation values in custom attribute
            translates = cmds.getAttr("{0}.translate".format(game_joint))[0]

            cmds.addAttr(game_joint, longName='restTranslate',
                         numberOfChildren=3,
                         attributeType='compound',
                         keyable=True)
            cmds.addAttr(game_joint, longName='restTranslateX',
                         attributeType='double',
                         parent='restTranslate',
                         keyable=True)
            cmds.addAttr(game_joint, longName='restTranslateY',
                         attributeType='double',
                         parent='restTranslate',
                         keyable=True)
            cmds.addAttr(game_joint, longName='restTranslateZ',
                         attributeType='double',
                         parent='restTranslate',
                         keyable=True)

            cmds.setAttr("{0}.restTranslateX".format(game_joint), translates[0])
            cmds.setAttr("{0}.restTranslateY".format(game_joint), translates[1])
            cmds.setAttr("{0}.restTranslateZ".format(game_joint), translates[2])

            # Constrain game skeleton
            constrained_joint = data[1]
            cmds.parentConstraint(joint_, constrained_joint, maintainOffset=True)

    def bind_to_game_skeleton(self):
        bindable_geometry = [geo for geo in cmds.ls(type="mesh") if "ShapeOrig" not in geo]
        deformation_root = cmds.listRelatives("{0}RootOffset".format(self.game_skeleton_prefix))
        for geometry in bindable_geometry:
            game_skin_cluster = cmds.skinCluster(deformation_root, geometry, bindMethod=1)
            cmds.geomBind(game_skin_cluster, falloff=1, maxInfluences=4, geodesicVoxelParams=(256, 256))

    @staticmethod
    def set_units():
        cmds.currentUnit(angle="rad")
        cmds.currentUnit(linear="m")

    def reset_units(self):
        cmds.currentUnit(angle=self.scene_angles)
        cmds.currentUnit(linear=self.scene_lengths)

    def create_game_skeleton(self):
        self.set_units()
        self.create_source_joints_dict()
        self.create_game_joints()
        self.reset_units()
