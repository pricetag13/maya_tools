import maya.cmds as cmds

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


def get_controls():
    excluded_ctrls = ['worldA_ctrl', 'worldB_ctrl', 'root_ctrl']

    all_joints = cmds.ls(type='joint')

    my_controls = [control for control in all_joints if '_ctrl' in control and control not in excluded_ctrls]
    print 'my_controls = ', my_controls

    controls = []

    for _joint in all_joints:
        if '_ctrl' in _joint:
            controls.append(_joint)


create_game_joints()
parent_game_joints()


def build_gui():
    return None


def main():
    build_gui()

main()
