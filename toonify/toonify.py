import os
import json
import maya.cmds as cmds

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
        self.toon_shader = ''

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

    def import_shader(self, list_item):
        file_item = cmds.textScrollList(list_item, query=True, selectItem=True)
        self.toon_shader_file = file_item[0]
        self.toon_shader = self.toon_shader_file[:-3]
        full_shader_path = os.path.join(self.shader_directory, self.toon_shader_file)
        cmds.file(full_shader_path, i=True)
        shader_container = '{0}_0_container'.format(self.toon_shader)
        container_tokenized_list = shader_container.split('_')
        toonify_type = container_tokenized_list[1]
        shader_network = [shader_container] + cmds.listConnections('{0}.connected_nodes'.format(shader_container))

        shader_containers_of_type = [network for network in cmds.ls(type='transform') if toonify_type in network]

        increment_list = []
        for shader_container in shader_containers_of_type:
            integer_list = [int(character) for character in shader_container if character.isdigit()]
            increment_list.append(integer_list[0])

        highest_increment_of_type = max(increment_list)
        new_increment = highest_increment_of_type + 1

        for node in shader_network:
            new_name = node.replace('0', str(new_increment))
            cmds.rename(node, new_name)

        self.assign_shader()

    def assign_shader(self):
        self.assigned_geometry = cmds.ls(selection=True)
        print self.assigned_geometry

    @staticmethod
    def populate_imported_shaders():
        print ''

    @staticmethod
    def create_message_network():
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
                                             doubleClickCommand=lambda maya_false: self.import_shader(base_list_item))

        imported_list_item = cmds.textScrollList('toonify_imported_list', numberOfRows=10, allowMultiSelection=False,
                                                 height=200,
                                                 doubleClickCommand=lambda maya_false:
                                                 self.import_shader(base_list_item))

        cmds.frameLayout(label='Utilities', collapsable=True, parent=win_main)
        cmds.rowColumnLayout(numberOfColumns=2)
        for label, function in self.utility_list:
            cmds.button(label + '_button', h=40, w=250, label=label, command=lambda maya_false:function)

        cmds.setParent("..")
        cmds.showWindow(win_main)

    @staticmethod
    def close_window():
        cmds.deleteUI("toonify_win")
        cmds.windowPref("toonify_win", removeAll=True)

    def run_toonify(self):
        self.build_gui()
        self.set_initial_state()