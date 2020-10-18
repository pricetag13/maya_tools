import os
import json
from functools import partial
import maya.cmds as cmds
import mtoa.aovs as aovs


class Toonify(object):
    """
    Tool for assigning Arnold Toon Shaders.
    """
    def __init__(self):
        self.toonify_root_directory = r'C:\dev\maya_tools\toonify'
        self.shader_directory = os.path.join(self.toonify_root_directory, 'shaders')

        self.toonify_config = os.path.join(self.toonify_root_directory, 'toonify_config.txt')

        self.file_path = ''
        self.toon_shader_file = ''
        self.toon_shader_object = ''
        self.toon_shader = ''

        self.toon_shading_engine = ''

        self.assigned_geometry = []

        self.base_color = [0, 0, 0]
        self.shadow_color = [0, 0, 0]

        self.directional_light = ''

        # list of extra utilities used to populate buttons in GUI
        self.utility_list = [('Set Render Preferences', self.set_render_preferences),
                             ('Create Message Network', self.create_message_network)
                             ]

    @staticmethod
    def set_render_preferences():
        print ''

    def list_geometry(self):
        self.assigned_geometry = cmds.ls(selection=True)

    def import_shader(self, list_item):
        # Get object from scroll list
        file_item = cmds.textScrollList(list_item, query=True, selectItem=True)
        self.toon_shader_file = file_item[0]
        self.toon_shader_object = self.toon_shader_file[:-3]
        full_shader_path = os.path.join(self.shader_directory, self.toon_shader_file)
        # Perform the import
        cmds.file(full_shader_path, i=True)
        # Get all parts of the shading network
        all_transforms = cmds.ls(type='transform')
        shader_container = [transform for transform in all_transforms if '_0_container' in transform][0]
        # shader_container = '{0}_0_container'.format(self.toon_shader_object)
        container_tokenized_list = shader_container.split('_')
        toonify_type = container_tokenized_list[1]
        default_shader_network = [shader_container] + \
                                 cmds.listConnections('{0}.connected_nodes'.format(shader_container))
        renamed_shader_network = []
        shader_containers_of_type = [network for network in cmds.ls(type='transform') if toonify_type in network]
        increment_list = []

        for shader_container in shader_containers_of_type:
            integer_list = [int(character) for character in shader_container if character.isdigit()]
            increment_list.append(integer_list[0])

        highest_increment_of_type = max(increment_list)
        new_increment = highest_increment_of_type + 1

        for node in default_shader_network:
            new_name = node.replace('0', str(new_increment))
            renamed_node = cmds.rename(node, new_name)
            renamed_shader_network.append(renamed_node)

        self.toon_shader = "{0}_{1}_{2}".format(container_tokenized_list[0], container_tokenized_list[1], new_increment)
        self.toon_shading_engine = [node for node in renamed_shader_network if 'final_SG' in node][0]

        self.connect_aovs()
        self.get_toonify_shaders_in_scene()

    @staticmethod
    def assign_shader(imported_list_item):
        file_item = cmds.textScrollList(imported_list_item, query=True, selectItem=True)[0]
        selected_geometry = cmds.ls(selection=True)
        for geometry in selected_geometry:
            cmds.sets(geometry, edit=True, forceElement=file_item)

    def connect_aovs(self):
        existing_aovs = cmds.ls(type='aiAOV')
        required_aovs = self.get_required_aov_list_from_shading_group(self.toon_shading_engine)
        print required_aovs, 'Required'
        for required_aov in required_aovs:
            if required_aov[2] not in existing_aovs:
                new_aov = cmds.createNode('aiAOV', name=required_aov[2])
                cmds.setAttr(new_aov + '.name', required_aov[1], type='string')
                cmds.connectAttr(new_aov + '.message', 'defaultArnoldRenderOptions.aovList', nextAvailable=True)
                cmds.connectAttr('defaultArnoldDriver.message', new_aov + '.outputs[0].driver')
                cmds.connectAttr('defaultArnoldFilter.message', new_aov + '.outputs[0].filter')

    @staticmethod
    def get_required_aov_list_from_shading_group(shading_group):
        shading_group_container = shading_group.replace('final_SG', 'container')
        shader_network = [shading_group_container] +\
                         cmds.listConnections('{0}.connected_nodes'.format(shading_group_container))
        aov_plug_list = [node for node in shader_network if '_aov' in node]
        required_aov_list = []
        for aov_plug in aov_plug_list:
            aov_tokenized_list = aov_plug.split('_')
            aov_token = aov_tokenized_list[-1]
            aov_name = aov_token[3:]
            aov = 'aiAOV_{0}'.format(aov_name)
            required_aov_list.append((aov_plug, aov_name, aov))
        return required_aov_list


    @staticmethod
    def get_toonify_shaders_in_scene():
        all_scene_shaders = cmds.ls(type='shadingEngine')
        all_toonify_shaders = [shader for shader in all_scene_shaders if 'toonify' in shader]
        cmds.textScrollList('toonify_imported_list', edit=True, removeAll=True)
        for shader in all_toonify_shaders:
            cmds.textScrollList('toonify_imported_list', edit=True, append=shader)

    @staticmethod
    def create_message_network(*args):
        connected_nodes = cmds.ls(selection=True)
        container_null = cmds.group(name='rename_me', empty=True)

        cmds.addAttr(container_null, longName='connected_nodes', attributeType='message')
        for node in connected_nodes:
            cmds.addAttr(node, longName='{0}_message'.format(node), attributeType='message')
            cmds.connectAttr('{0}.connected_nodes'.format(container_null), '{0}.{1}_message'.format(node, node))

    def query_color(self):
        print 'Setting Color'
        print self.base_color
        print self.shadow_color

    def set_color(self):
        print self.base_color
        # setAttr
        # "toonify_basic_base_tonemap_ramp.colorEntryList[0].color" - type
        # double3
        # 0.0657895
        # 0.0657895
        # 0.0657895;

    def create_directional_light(self):
        print self.directional_light

    def browse_to_dir(self):
        with open(self.toonify_config, 'r') as f:
            json_read = json.load(f)
        card_directory = cmds.fileDialog2(startingDirectory=json_read, dialogStyle=1, fileMode=2)
        file_path = str(card_directory[0])
        field_text = cmds.textField('toonify_path_field', edit=True, text=str(file_path))
        if field_text:
            self.update_toonify_config(file_path)
        else:
            cmds.warning('No image files in selected directory')

    def text_field_to_dir(self):
        file_path = cmds.textField('toonify_path_field', query=True, text=True)
        if file_path:
            self.update_toonify_config(file_path)
        else:
            cmds.warning('No image files in selected directory')

    @staticmethod
    def refresh_scroll_list(file_path):
        files_found = os.listdir(file_path)
        shaders_found = [file_ for file_ in files_found if file_.endswith(('.ma', '.mb'))]
        cmds.textScrollList('toonify_base_list', edit=True, removeAll=True, append=shaders_found)

    def set_initial_state(self):
        open(self.toonify_config, 'w')
        with open(self.toonify_config, 'w') as text_file:
            json.dump(self.shader_directory, text_file)

        with open(self.toonify_config, 'r') as f:
            toonify_config_read = json.load(f)
        cmds.textField('toonify_path_field', edit=True, text=toonify_config_read)
        if toonify_config_read:
            self.refresh_scroll_list(toonify_config_read)
        else:
            cmds.warning('No image files in selected directory')

    def update_toonify_config(self, file_path):
        with open(self.toonify_config, 'w') as text_file:
            json.dump(file_path, text_file)
        self.refresh_scroll_list(file_path)

    def build_gui(self):
        # If window already exists, deletes all preferences and kills it
        if cmds.window("toonify_win", exists=True):
            self.close_window()

        # window preferences
        win_main = cmds.window("toonify_win", title="Toonify", resizeToFitChildren=True, sizeable=False)

        # window layout
        cmds.frameLayout(label='Source Shader Directory', height=60, collapsable=False, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        # Source directory layout
        cmds.textField('toonify_path_field', width=470, alwaysInvokeEnterCommandOnReturn=True,
                       enterCommand=lambda maya_false: self.text_field_to_dir())
        cmds.button('toonify_browse_button', label='...', width=30, command=lambda maya_false: self.browse_to_dir())
        # Palette layout
        cmds.frameLayout(label='Toon Palette', height=200, collapsable=False, parent=win_main)
        cmds.palettePort('palette', height=160, dim=(12, 3))
        cmds.button('save_palette_button', label='Save Palette', height=40, width=120,
                    command=lambda maya_false: self.browse_to_dir())
        cmds.frameLayout(label='Toon Shaders', collapsable=False, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        base_list_item = cmds.textScrollList('toonify_base_list', numberOfRows=10, allowMultiSelection=False,
                                             height=200,
                                             doubleClickCommand=lambda: self.import_shader(base_list_item))

        imported_list_item = cmds.textScrollList('toonify_imported_list', numberOfRows=10, allowMultiSelection=False,
                                                 height=200,
                                                 doubleClickCommand=lambda: self.assign_shader(imported_list_item))

        cmds.frameLayout(label='Utilities', collapsable=True, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        for label, function in self.utility_list:
            cmds.button(label + '_button', h=40, w=250, label=label, command=partial(function))

        cmds.setParent("..")
        cmds.showWindow(win_main)

    @staticmethod
    def close_window():
        cmds.deleteUI("toonify_win")
        cmds.windowPref("toonify_win", removeAll=True)

    def run_toonify(self):
        self.build_gui()
        self.set_initial_state()
        self.get_toonify_shaders_in_scene()