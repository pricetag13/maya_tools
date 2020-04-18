import os
import json
from functools import partial
import maya.cmds as cmds

class CardzClass(object):
    """
    This is my tool to automate the process of creating 2.5d cards
    """
    def __init__(self):
        self.cardz_config_directory = 'C:/cardz_config'

        self.cardz_config = os.path.join(self.cardz_config_directory, 'cardz_config.txt')
        self.file_path = ''
        self.card_image = ''

        # list of extra utilities used to populate buttons in GUI
        self.utility_list = [('Project UVs', self.project_uvs),
                             ('conform_normals', self.conform_normals),
                             ('combine_geo', self.combine_geo),
                             ('camera_from_geo', self.camera_from_geo)
                             ]

        self.selected_geo = ''
        # example selected_geo_shape: 'garden_wall_dispacement_cardShape'
        self.selected_geo_shape = ''
        # example shading_grp: 'garden_wall_dispacement_SG'
        self.shading_grp = ''
        # example shader: 'garden_wall_dispacement_L'
        self.shader = ''
        # example file_node: 'garden_wall_dispacement_F'
        self.file_node = ''
        # example current_file: 'D:/scene_garden_wall/Photoshop/garden_wall_dispacement.psd'
        self.current_file = ''

        self.x_width = 0
        self.y_height = 0

        self.render_aspect_ratio = 1
        self.card_cam = ''



    def set_initial_state(self):
        if not os.path.exists(self.cardz_config_directory):
            os.makedirs(self.cardz_config_directory)
            with open(self.cardz_config, 'w') as txtfile:
                json.dump(self.cardz_config_directory, txtfile)

        with open(self.cardz_config, 'r') as f:
            cardz_config_read = json.load(f)
        cmds.textField('cardz_path_field', edit=True, text=cardz_config_read)
        if cardz_config_read:
            self.refresh_scroll_list(cardz_config_read)
        else:
            cmds.warning('No image files in selected directory')

    def update_cardz_config(self, file_path):
        with open(self.cardz_config, 'w') as txtfile:
            json.dump(file_path, txtfile)
        self.refresh_scroll_list(file_path)

    def browse_to_dir(self):
        with open(self.cardz_config, 'r') as f:
            json_read = json.load(f)
        card_directory = cmds.fileDialog2(startingDirectory=json_read, dialogStyle=1, fileMode=2)
        file_path = str(card_directory[0])
        field_text = cmds.textField('cardz_path_field', edit=True, text=str(file_path))
        if field_text:
            self.update_cardz_config(file_path)
        else:
            cmds.warning('No image files in selected directory')

    def text_field_to_dir(self):
        file_path = cmds.textField('cardz_path_field', query=True, text=True)
        if file_path:
            self.update_cardz_config(file_path)
        else:
            cmds.warning('No image files in selected directory')

    def refresh_scroll_list(self, file_path):
        files_found = os.listdir(file_path)
        image_files_found = [file_ for file_ in files_found if file_.endswith(
            ('.png', '.psd', '.tif', '.jpg', '.tga', '.dds', '.bmp', '.sgi', '.exr', '.gif', '.iff', '.pic'))]
        cmds.textScrollList('cardz_scroll_list', edit=True, removeAll=True, append=image_files_found)

    def create_card(self, list_item):
        file_item = cmds.textScrollList(list_item, query=True, selectItem=True)
        image_file = str(file_item[0])
        image_list = image_file.split(".")
        image_name = image_list[0]

        # create all required nodes for cardz shading network
        file_node = cmds.shadingNode('file', asTexture=True, name=image_name + '_F')
        print 'file_node = ', file_node
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

    def project_uvs(self, *args):
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

    def combine_geo(self, *args):
        cmds.polyUnite(ch=0, mergeUVSets=1, name='actor_geo')
        actor_bounding_box = cmds.xform('actor_geo', query=True, boundingBox=True)
        center_pos = cmds.xform('actor_geo', query=True, worldSpace=True, scalePivot=True)
        cmds.xform('actor_geo', worldSpace=True, pivots=[center_pos[0], actor_bounding_box[1], center_pos[2]])
        cmds.move('actor_geo', rotatePivotRelative=True, y=0)
        cmds.makeIdentity('actor_geo', apply=True, translate=1, rotate=1, scale=1, normal=1)

    def conform_normals(self, *args):
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

    def world_align_card(self):
        cmds.setAttr("{0}.rotateX".format(self.selected_geo[0]), 90)
        temp_group = cmds.group(self.card_cam, self.selected_geo, name="{0}_grp".format(self.selected_geo))
        xform_bounding_box = cmds.xform(temp_group, query=True, boundingBox=True)
        center_pos = cmds.xform(temp_group, query=True, worldSpace=True, scalePivot=True)
        cmds.xform(temp_group, worldSpace=True, pivots=[center_pos[0], xform_bounding_box[1], 0])
        cmds.move(temp_group, rotatePivotRelative=True, y=0)
        cmds.parent(self.card_cam, world=True)
        cmds.parent(self.selected_geo, world=True)
        cmds.delete(temp_group)

    def create_render_cam(self):
        camera_distance = self.y_height * .41666
        card_cam = cmds.camera(name="{0}_camera".format(self.selected_geo), focalLength=100,
                               nearClipPlane=10, farClipPlane=camera_distance + 20, displayFilmGate=True,
                               displayGateMask=True, displayResolution=True, overscan=1.1)[0]
        cmds.setAttr("{0}.displayCameraNearClip".format(card_cam), True)
        cmds.setAttr("{0}.displayCameraFarClip".format(card_cam), True)
        cmds.setAttr("{0}.displayCameraFrustum".format(card_cam), True)
        cmds.setAttr("{0}.horizontalFilmAperture".format(card_cam),
                     cmds.getAttr("{0}.verticalFilmAperture".format(card_cam)) * self.render_aspect_ratio)
        cmds.setAttr("{0}.tz".format(card_cam), camera_distance)
        cmds.lookThru(card_cam)
        self.card_cam = card_cam

    def camera_from_geo(self, *args):
        self.set_file_info_from_geo()
        self.create_render_cam()
        self.world_align_card()

    def set_file_info_from_geo(self):
        selected_geo = cmds.ls(selection=True)
        selected_geo_shape = cmds.ls(selection=True, shapes=True, dag=True)
        shading_grp = cmds.listConnections(selected_geo_shape, type='shadingEngine')
        shader = cmds.ls(cmds.listConnections(shading_grp), materials=True)[0]
        file_node = cmds.listConnections("{0}.color".format(shader), type='file')[0]
        current_file = cmds.getAttr("{0}.fileTextureName".format(file_node))
        x_width = cmds.getAttr("{0}.outSizeX".format(file_node))
        y_height = cmds.getAttr("{0}.outSizeY".format(file_node))
        cmds.setAttr("defaultResolution.width", x_width)
        cmds.setAttr("defaultResolution.height", y_height)
        render_aspect_ratio = x_width / y_height

        self.selected_geo = selected_geo
        self.selected_geo_shape = selected_geo_shape
        self.shading_grp = shading_grp
        self.shader = shader
        self.file_node = file_node
        self.current_file = current_file
        self.x_width = x_width
        self.y_height = y_height
        self.render_aspect_ratio = render_aspect_ratio

    def build_gui(self):
        # If window already exists, deletes all preferences and kills it
        if cmds.window("cardz_win", exists=True):
            self.close_window()

        # window preferences
        win_main = cmds.window("cardz_win", title="Cardz", sizeable=True)

        # window layout
        cmds.frameLayout(label='Source Image Directory', collapsable=True, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.textField('cardz_path_field', width=470, alwaysInvokeEnterCommandOnReturn=True,
                       enterCommand=lambda maya_false: self.text_field_to_dir())
        cmds.button('cardz_browse_button', label='...', width=30, command=lambda maya_false: self.browse_to_dir())
        cmds.frameLayout(label='Image Files', collapsable=False, parent=win_main)

        list_item = cmds.textScrollList('cardz_scroll_list', numberOfRows=20, allowMultiSelection=True, height=500,
                                        doubleClickCommand=lambda: self.create_card(list_item))

        cmds.frameLayout(label='Utilities', collapsable=True, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        for label, function in self.utility_list:
            cmds.button(label + '_button', h=40, w=250, label=label, command=partial(function))

        cmds.setParent("..")
        cmds.showWindow(win_main)

    def close_window(self):
        cmds.deleteUI("cardz_win")
        cmds.windowPref("cardz_win", removeAll=True)

    def run_cardz(self):
        self.build_gui()
        self.set_initial_state()
