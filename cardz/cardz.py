"""
This is my tool to automate the process of creating 2.5d cards
"""

import os
import json
from functools import partial
import maya.cmds as cmds

ROOT_DIR = "C:/dev/maya_tools/cardz/"


def set_initial_state():
    with open(ROOT_DIR + 'cardz_config.txt', 'r') as f:
        cardz_config_read = json.load(f)
    cmds.textField('cardz_path_field', edit=True, text=cardz_config_read)
    if cardz_config_read:
        refresh_scroll_list(cardz_config_read)
    else:
        cmds.warning('No image files in selected directory')


def update_cardz_config(file_path):
    with open(ROOT_DIR + 'cardz_config.txt', 'w') as txtfile:
        json.dump(file_path, txtfile)
    refresh_scroll_list(file_path)


def browse_to_dir():
    with open(ROOT_DIR + 'cardz_config.txt', 'r') as f:
        json_read = json.load(f)
    card_directory = cmds.fileDialog2(startingDirectory=json_read, dialogStyle=1, fileMode=2)
    file_path = str(card_directory[0])
    field_text = cmds.textField('cardz_path_field', edit=True, text=str(file_path))
    if field_text:
        update_cardz_config(file_path)
    else:
        cmds.warning('No image files in selected directory')


def text_field_to_dir():
    file_path = cmds.textField('cardz_path_field', query=True, text=True)
    if file_path:
        update_cardz_config(file_path)
    else:
        cmds.warning('No image files in selected directory')


def refresh_scroll_list(file_path):
    files_found = os.listdir(file_path)
    image_files_found = [file_ for file_ in files_found if file_.endswith(
        ('.png', '.psd', '.tif', '.jpg', '.tga', '.dds', '.bmp', '.sgi', '.exr', '.gif', '.iff', '.pic'))]
    cmds.textScrollList('cardz_scroll_list', edit=True, removeAll=True, append=image_files_found)


def create_card(list_item):
    file_item = cmds.textScrollList(list_item, query=True, selectItem=True)
    image_file = str(file_item[0])
    image_list = image_file.split(".")
    image_name = image_list[0]

    # create all required nodes for cardz shading network
    file_node = cmds.shadingNode('file', asTexture=True, name=image_name + '_F')
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=image_name + '_SG')
    cardz_shader = cmds.shadingNode('lambert', asShader=True, name=image_name + '_L')

    file_path = cmds.textField('cardz_path_field', query=True, text=True)

    # connect shader to shading group
    cmds.setAttr(file_node + '.fileTextureName', file_path + '/' + image_file, type="string")
    cmds.connectAttr(cardz_shader + '.outColor', shading_group + '.surfaceShader')

    # connect file node to shader
    cmds.connectAttr(file_node + '.outColor', cardz_shader + '.color')
    cmds.connectAttr(file_node + '.outColor',  cardz_shader + '.incandescence')
    cmds.connectAttr(file_node + '.outTransparency', cardz_shader + '.transparency')

    # Get image dimensions and scale them down by 500
    x_source_width = cmds.getAttr(file_node+".outSizeX")
    x_width = x_source_width/10
    y_source_height = cmds.getAttr(file_node+".outSizeY")
    y_height = y_source_height/10

    # Create card
    card = cmds.polyPlane(w=x_width, h=y_height, sx=1, sy=1, ax=[0, 1, 0], cuv=1, ch=0,
                                 name=image_name+"_card")
    # Assign shader to card
    cmds.sets(card, edit=True, forceElement=shading_group)


def project_uvs(*args):
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


def combine_geo(*args):
    cmds.polyUnite(ch=0, mergeUVSets=1, name='actor_geo')
    actor_bounding_box = cmds.xform('actor_geo', query=True, boundingBox=True)
    center_pos = cmds.xform('actor_geo', query=True, worldSpace=True, scalePivot=True)
    cmds.xform('actor_geo', worldSpace=True, pivots=[center_pos[0], actor_bounding_box[1], center_pos[2]])
    cmds.move('actor_geo', rotatePivotRelative=True, y=0)
    cmds.makeIdentity('actor_geo', apply=True, translate=1, rotate=1, scale=1, normal=1)


def conform_normals(*args):
    geometry_list = cmds.ls(selection=True, exactType='transform')
    cmds.polyNormal(geometry_list, nm=2)
    for geometry in geometry_list:
        face = cmds.polyInfo(geometry + '.f[0]', faceNormals=True)
        split_face = face[0].split(":")
        vector = split_face[1][10]
        if '-' in vector:
            cmds.polyNormal(geometry, nm=0)
        else:
            return None

# list of extra utilities used to populate buttons in GUI
utility_list = [('Project UVs', project_uvs),
                ('conform_normals', conform_normals),
                ('combine_geo', combine_geo)
                ]


def build_gui():
    # If window already exists, deletes all preferences and kills it
    if cmds.window("cardz_win", exists=True):
        close_window()

    # window preferences
    win_main = cmds.window("cardz_win", title="Cardz", sizeable=True)

    # window layout
    cmds.frameLayout(label='Source Image Directory', collapsable=True, parent=win_main)
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.textField('cardz_path_field', width=470, alwaysInvokeEnterCommandOnReturn=True,
                   enterCommand=lambda maya_false: text_field_to_dir())
    cmds.button('cardz_browse_button', label='...', width=30, command=lambda maya_false: browse_to_dir())
    cmds.frameLayout(label='Image Files', collapsable=False, parent=win_main)

    list_item = cmds.textScrollList('cardz_scroll_list', numberOfRows=20, allowMultiSelection=True, height=500,
                                    doubleClickCommand=lambda: create_card(list_item))

    cmds.frameLayout(label='Utilities', collapsable=True, parent=win_main)
    cmds.rowColumnLayout(numberOfColumns=2)
    for label, function in utility_list:
        cmds.button(label + '_button', h=40, w=250, label=label, command=partial(function))

    cmds.setParent("..")
    cmds.showWindow(win_main)


def close_window():
    cmds.deleteUI("cardz_win")
    cmds.windowPref("cardz_win", removeAll=True)


def main():
    build_gui()
    set_initial_state()

main()

