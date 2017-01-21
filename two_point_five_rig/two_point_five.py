import maya.cmds as cmds
from functools import partial

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Return lists of components required by various steps in the workflow
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def get_geo():
    all_transforms = cmds.ls(type='transform')
    all_poly_meshes = cmds.filterExpand(all_transforms, selectionMask=12)
    return all_poly_meshes[0]


def get_def_joints():
    all_joints = cmds.ls(type='joint')
    def_joints = [joint_ for joint_ in all_joints if 'Def' in joint_]
    return def_joints


def get_bind_joints():
    if get_skin_cluster():
        bind_joints = cmds.skinCluster(get_skin_cluster(), query=True, inf=True)
        return bind_joints


def get_skin_cluster():
    found_skin_cluster = ''
    for relative in cmds.listRelatives(get_geo()):
        connections = cmds.listConnections(relative)
        skin_cluster_found = [s for s in connections if 'skinCluster' in s]

    if skin_cluster_found:
        found_skin_cluster = skin_cluster_found[0]
        found_skin_cluster = found_skin_cluster[:-3]

    return found_skin_cluster


def get_controls():
    excluded_ctrls = ['worldA_ctrl', 'worldB_ctrl', 'root_ctrl']
    all_joints = cmds.ls(type='joint')
    all_controls = [control_ for control_ in all_joints if '_ctrl' in control_ and control_ not in excluded_ctrls]
    return all_controls

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Main steps in 2.5D workflow
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def bind_actor(*args):
    cmds.select(get_def_joints())
    cmds.select(get_geo(), add=True)
    cmds.SmoothBindSkin()
    # cmds.skinCluster(maximumInfluences=2, obeyMaxInfluences=False)
    cmds.select(clear=True)


def clean_up_weights(*args):
    cmds.skinCluster(get_skin_cluster(), )


def lock_controls_2d(*args):
    for control_ in get_controls():
        world_rotate_xform = cmds.xform(control_, query=True, rotation=True, worldSpace=True)
        if 85.0 <= world_rotate_xform[0] <= 95.0:
            cmds.setAttr(control_ + '.tz', lock=True)
            cmds.setAttr(control_ + '.rx', lock=True)
            cmds.setAttr(control_ + '.rz', lock=True)
            cmds.setAttr(control_ + '.overrideEnabled', 1)
            cmds.setAttr(control_ + '.overrideColor', 6)

        else:
            cmds.setAttr(control_ + '.tz', lock=True)
            cmds.setAttr(control_ + '.rx', lock=True)
            cmds.setAttr(control_ + '.ry', lock=True)
            cmds.setAttr(control_ + '.overrideEnabled', 1)
            cmds.setAttr(control_ + '.overrideColor', 17)


def create_game_skeleton(*args):
    print '!!!!!!!!!!!!!!!!!!!!!!!!! running'
    game_joints = []

    for bound_joint in get_bind_joints():
        game_joint = cmds.duplicate(bound_joint, parentOnly=True, name='temp_name_' + bound_joint)
        cmds.parent(game_joint, world=True)
        game_joints.append(game_joint)

    for game_joint in game_joints:
        game_joint.replace('temp_name_', '')


def create_game_skeleton(game_joints):
    game_root_jnt = cmds.joint(name='game_root_jnt', p=(0, 0, 0))
    constrain_joints = zip(get_bind_joints(), game_joints)

    for x, y in constrain_joints:
        cmds.parentConstraint(x, y)
        cmds.scaleConstraint(x, y)

    for game_joint in game_joints:
        cmds.parent(game_joint, game_root_jnt)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Functions included in the GUI
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function_list = [('Lock Controls 2D', lock_controls_2d),
                 ('Bind Actor', bind_actor),
                 ('Create Game Skeleton', create_game_skeleton)
                 ]


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# 2.5D workflow GUI
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def build_gui():
    window_pos = [0, 0]
    # If window already exists, deletes all preferences and kills it
    if cmds.window("2pt5d_win", exists=True):
        window_pos = cmds.window("2pt5d_win", q=1, topLeftCorner=True)
        cmds.deleteUI("2pt5d_win")
        cmds.windowPref("2pt5d_win", removeAll=True)

    # window preferences
    win_main = cmds.window("2pt5d_win", title="2.5D", sizeable=True, width=250, height=100)

    # window layout
    cmds.frameLayout(label='rigging Workflow', collapsable=True, parent=win_main)
    cmds.rowColumnLayout(numberOfColumns=1)

    count = 0

    for label, function in function_list:
        cmds.button(label + '_button', h=60, w=250, label=label, command=partial(function))
        count += 1


    cmds.setParent("..")
    cmds.showWindow(win_main)
    cmds.window(win_main, e=1, topLeftCorner=window_pos, height=count*60, width=250)


def main():
    build_gui()

main()
