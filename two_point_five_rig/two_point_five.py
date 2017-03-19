import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import re
import os

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Return lists of components required by various steps in the workflow
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def get_geo():
    all_transforms = cmds.ls(type='transform')
    all_poly_meshes = cmds.filterExpand(all_transforms, selectionMask=12)
    return all_poly_meshes[0]


def get_actor_main_group():
    actor_main_group = cmds.listRelatives(get_geo(), parent=True)
    return actor_main_group[0]


def get_def_joints():
    all_joints = cmds.ls(type='joint')
    def_joints = [joint_ for joint_ in all_joints if 'Def' in joint_]
    return def_joints


def get_bind_joints():
    if get_skin_cluster():
        bind_joints = cmds.skinCluster(get_skin_cluster(), query=True, inf=True)
        return bind_joints


def get_game_joints():
    game_joints = cmds.listRelatives('game_root_jnt', children=True)
    return game_joints


def get_game_joints_full_path():
    game_joints = cmds.listRelatives('game_root_jnt', children=True, fullPath=True)
    return game_joints


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


def get_rig_root():
    all_transforms = cmds.ls(type='transform')
    rig_root = [transform for transform in all_transforms if 'rig' in transform]
    return rig_root[0]


def get_current_folder():
    all_paths = cmds.file(query=True, list=True)
    current_path = [path for path in all_paths if '.ma' in path]
    current_folder = os.path.dirname(current_path[0])
    return current_folder


def get_lambert():
    all_lamberts = cmds.ls(type='lambert')
    asset_lambert = [lambert for lambert in all_lamberts if '_L' in lambert]
    return asset_lambert[0]


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Main steps in 2.5D workflow
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def bind_actor(*args):
    cmds.select(get_def_joints())
    cmds.select(get_geo(), add=True)
    cmds.SmoothBindSkin()
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

    game_root_jnt = cmds.joint(name='game_root_jnt', position=(0, 0, 0))
    cmds.group(game_root_jnt, name='game_skeleton')
    cmds.parent('game_skeleton', get_actor_main_group())

    for bound_joint in get_bind_joints():
        game_joint = cmds.duplicate(bound_joint, parentOnly=True, name='game_' + bound_joint)
        cmds.parent(game_joint, game_root_jnt)


def export_skin_weights(*args):
    weight_path = os.path.join(get_current_folder(), 'weights')
    if not os.path.exists(weight_path):
        os.makedirs(weight_path)
    cmds.deformerWeights(get_geo() + '_weights.xml', path=weight_path, export=True, deformer=get_skin_cluster())


def unbind_geo(*args):
    cmds.skinCluster(get_geo(), edit=True, unbind=True)


def bind_to_game_joints(*args):
    cmds.select(get_game_joints())
    cmds.select(get_geo(), add=True)
    cmds.SmoothBindSkin()
    cmds.select(clear=True)


def import_skin_weights(*args):

    for game_joint in get_game_joints():
        stripped_game_joint = game_joint[5:]
        cmds.rename(game_joint, stripped_game_joint)

    weight_path = os.path.join(get_current_folder(), 'weights')
    cmds.deformerWeights(get_geo() + '_weights.xml', path=weight_path, im=True, deformer=get_skin_cluster())

    rename_joints = zip(get_game_joints_full_path(), get_game_joints())
    for fullpath, shortpath in rename_joints:
        cmds.rename(fullpath, 'game_' + shortpath)


def connect_game_skeleton_to_rig(*args):
    rig_joints = []
    for bind_joint in get_bind_joints():
        rig_joint = bind_joint[5:]
        rig_joints.append(rig_joint)

    constrain_joints = zip(rig_joints, get_bind_joints())
    print 'constrain_joints = ', constrain_joints

    # return None

    for x, y in constrain_joints:
        cmds.parentConstraint(x, y)
        cmds.scaleConstraint(x, y)


def export_game_asset_fbx(*args):

    cmds.parent(get_rig_root(), world=True)
    cmds.select(get_actor_main_group())

    out_color = (get_lambert() + '.outColor')
    out_color_connection = cmds.listConnections(out_color)
    cmds.disconnectAttr(out_color, out_color_connection[0] + '.surfaceShader')

    reset_export = 'FBXResetExport'
    mel.eval(reset_export)
    fbx_export_properties = ('FBXExportInAscii -v true;'
                             'FBXExportConstraints -v false;'
                             'FBXExportEmbeddedTextures -v false;'
                             'FBXExportFileVersion -v "FBX201400";'
                             'FBXExportInputConnections -v false;'
                             'FBXExportShapes -v true;'
                             'FBXExportSkins -v true;'
                             'FBXExportSmoothingGroups -v true;'
                             'FBXProperty "Export|AdvOptGrp|UI|ShowWarningsManager" -v false;'
                             )
    mel.eval(fbx_export_properties)

    filepath = os.path.join(get_current_folder(), get_actor_main_group() + '.fbx')

    with open(filepath, 'w'):
        cmds.file(filepath, force=True, exportSelected=True, type='FBX', ignoreVersion=True)

    cmds.connectAttr(out_color, out_color_connection[0] + '.surfaceShader')

    cmds.parent(get_rig_root(), get_actor_main_group())


def project_actor_uvs(*args):
    selected_items = cmds.ls(selection=True)
    last_in_list = selected_items[-1]
    plane_shader = cmds.listConnections(cmds.listHistory(last_in_list, f=1), type='shadingEngine')
    cmds.sets(edit=True, forceElement=plane_shader[0])

    display_layer = cmds.listConnections(last_in_list, type='displayLayer')
    bounding_box = cmds.xform(last_in_list, query=True, boundingBox=True)
    width_length = (bounding_box[-1]) * 2
    temp_xform_null = cmds.group(empty=True, name='temp_xform_null')

    cmds.select(selected_items)

    for item in selected_items[:-1]:
        cmds.polyNormalPerVertex(xyz=(0.0, 1.0, 0.0))
        projection = cmds.polyProjection(item + '.f[0:9999]', type='Planar', mapDirection='y')
        cmds.setAttr(projection[0] + '.projectionCenter', 0, 0, 0)
        cmds.setAttr(projection[0] + '.projectionWidth', width_length)
        cmds.setAttr(projection[0] + '.projectionHeight', width_length)
        cmds.parent(item, temp_xform_null)

        cmds.delete(constructionHistory=True)

    xform_bounding_box = cmds.xform(temp_xform_null, query=True, boundingBox=True)

    cmds.setAttr(temp_xform_null + '.rotateX', 90)

    xform_bounding_box = cmds.xform(temp_xform_null, query=True, boundingBox=True)
    center_pos = cmds.xform(temp_xform_null, query=True, worldSpace=True, scalePivot=True)
    cmds.xform(temp_xform_null, worldSpace=True, pivots=[center_pos[0], xform_bounding_box[1], center_pos[2]])
    cmds.move(temp_xform_null, rotatePivotRelative=True, y=0)

    for item in selected_items[:-1]:
        cmds.parent(item, world=True)
        item_center = cmds.objectCenter(item, l=True)
        cmds.xform(item, worldSpace=True, pivots=item_center)
        cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=1)


    cmds.delete(temp_xform_null)
    cmds.delete(last_in_list)
    cmds.delete(display_layer)


def combine_actor(*args):
    cmds.polyUnite(ch=0, mergeUVSets=1, name='actor_geo')
    actor_bounding_box = cmds.xform('actor_geo', query=True, boundingBox=True)
    center_pos = cmds.xform('actor_geo', query=True, worldSpace=True, scalePivot=True)
    cmds.xform('actor_geo', worldSpace=True, pivots=[center_pos[0], actor_bounding_box[1], center_pos[2]])
    cmds.move('actor_geo', rotatePivotRelative=True, y=0)
    cmds.makeIdentity('actor_geo', apply=True, translate=1, rotate=1, scale=1, normal=1)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Functions included in the GUI
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function_list = [('Lock Controls 2D', lock_controls_2d),
                 ('Bind Actor', bind_actor),
                 ('Create Game Skeleton', create_game_skeleton),
                 ('export_skin_weights', export_skin_weights),
                 ('unbind_geo', unbind_geo),
                 ('bind_to_game_joints', bind_to_game_joints),
                 ('import_skin_weights', import_skin_weights),
                 ('connect_game_skeleton_to_rig', connect_game_skeleton_to_rig),
                 ('export_game_asset_fbx', export_game_asset_fbx),
                 ('Project Actor UVs', project_actor_uvs),
                 ('combine_actor', combine_actor)
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
