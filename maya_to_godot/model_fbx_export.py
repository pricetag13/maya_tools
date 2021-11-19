import os.path
import maya.cmds as cmds

import anim_utils


class ModelFBXExport(object):
    """
    Export model fbx to be used in Godot
    """
    def __init__(self, export_directory=None, export_model=None):

        # Supplied from UI
        self.export_directory = export_directory
        self.export_model = export_model

    def export(self):
        current_selection = anim_utils.get_current_selection()
        cmds.select(self.export_model)
        export_file = os.path.join(self.export_directory, self.export_model)
        cmds.file(export_file, options="v=0", type="FBX export", preserveReferences=True, exportSelected=True)
        if current_selection:
            cmds.select(current_selection)
        print("Exported Successfully")
