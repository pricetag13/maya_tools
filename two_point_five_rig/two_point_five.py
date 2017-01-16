import maya.cmds as cmds


def print_stuff():
    print 'printing some stuff'

# ////////////////////////////////////////////////////////////////

game_joints = []


def create_game_joints():
    skinned_geo = cmds.ls(selection=True)
    geo_relatives = cmds.listRelatives(skinned_geo)
    for relative in geo_relatives:
        my_connections = cmds.listConnections(relative)
        skin_cluster_found = [s for s in my_connections if 'skinCluster' in s]

    if skin_cluster_found:
        found_skin_cluster = skin_cluster_found[0]
        found_skin_cluster = found_skin_cluster[:-3]

    bind_joints = cmds.skinCluster(found_skin_cluster, query=True, inf=True)

    for bound_joint in bind_joints:
        game_joint = cmds.duplicate(bound_joint, parentOnly=True, name='game_' + bound_joint)
        cmds.parent(game_joint, world=True)
        game_joints.append(game_joint)
    cmds.select(clear=True)
    constrain_gamejoints(bind_joints)


def parent_game_joints():
    cmds.joint(name='game_root_jnt', p=(0, 0, 0))
    for game_joint in game_joints:
        cmds.parent(game_joint, 'game_root_jnt')


def constrain_gamejoints(bind_joints):
    constrain_joints = zip(bind_joints, game_joints)
    for x, y in constrain_joints:
        cmds.parentConstraint(x, y)
        cmds.scaleConstraint(x, y)

# create_game_joints()
# parent_game_joints()

# ////////////////////////////


def get_geo():
    all_geometry = cmds.ls(geometry=True)
    all_poly_meshes = cmds.filterExpand(all_geometry, selectionMask=12)
    return all_poly_meshes


def get_def_joints():
    all_joints = cmds.ls(type='joint')
    def_joints = [joint_ for joint_ in all_joints if 'Def' in joint_]
    return def_joints


def get_controls():
    excluded_ctrls = ['worldA_ctrl', 'worldB_ctrl', 'root_ctrl']
    all_joints = cmds.ls(type='joint')
    all_controls = [control_ for control_ in all_joints if '_ctrl' in control_ and control_ not in excluded_ctrls]
    return all_controls


def bind_actor():
    cmds.select(get_def_joints())
    cmds.select(get_geo(), add=True)
    cmds.SmoothBindSkin()
    cmds.select(clear=True)


# ////////////////////////////////////////


def lock_controls_2d():
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
        

#/////////////////////////////////////////////////////////

function_list = [('Print Stuff', print_stuff),
                 ('Lock Controls 2D', lock_controls_2d),
                 ('Bind Actor', bind_actor)
                 ]
#//////////////////////////////////////////////////////////////


def build_gui():
    window_pos = [0, 0]

    # If window already exists, deletes all preferences and kills it
    if cmds.window("2pt5d_win", exists=True):
        window_pos = cmds.window("2pt5d_win", q=1, topLeftCorner=True)
        cmds.deleteUI("2pt5d_win")
        cmds.windowPref("2pt5d_win", removeAll=True)

    # window preferences
    win_main = cmds.window("2pt5d_win", title="two_point_five_rig", sizeable=True, width=250, height=100)

    # window layout
    cmds.frameLayout(label='2.5D rigging Workflow', collapsable=True, parent=win_main)
    cmds.rowColumnLayout(numberOfColumns=1)

    for function in function_list:
        print 'function = ', function
        cmds.button(function[0], label=function[0], width=250, height=60, command=lambda maya_false: function[1]())

    cmds.setParent("..")
    cmds.showWindow(win_main)
    cmds.window(win_main, e=1, topLeftCorner=window_pos, height=300, width=250)


def main():
    build_gui()

main()
