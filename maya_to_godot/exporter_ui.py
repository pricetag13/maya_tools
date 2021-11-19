from PySide2 import QtCore, QtWidgets, QtUiTools
from shiboken2 import wrapInstance
import maya.OpenMayaUI as OpenMayaUI
import os
import json

import anim_utils
import anim_export
import game_skeleton
import model_fbx_export

# TODO: remove reload
import importlib
importlib.reload(anim_export)
importlib.reload(game_skeleton)
importlib.reload(model_fbx_export)


def maya_main_window():
    """
    Return the main maya window as a python object.
    """
    main_window_ptr = OpenMayaUI.MQtUtil_mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class AnimExportGUI(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(AnimExportGUI, self).__init__(parent)

        self.setWindowTitle("Export Animation for Godot")

        self.user_data = {
            # AnimationExport tab
            "GameSkeleton": "Skeleton",
            "ClipName": "Clip",
            "OutputDirectory": "",
            "StartFrame": "0",
            "EndFrame": "100",
            "FPS": "",
            "FileExtension": "tres",

            # GenerateSkeleton tab
            "RigSkeleton": "DeformationSystem",
            "RootControl": "Main",
            "GamePrefix": "Game",

            # ExportModelFBX tab
            "ExportModelFBXDirectory": "",
            "ModelName": "Nori",

            # Tab data
            "CurrentTab": 0
        }

        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.qt_form = QtCore.QFile(os.path.join(self.dir_path, "ui/anim_export.ui"))
        self.config_file = os.path.join(self.dir_path, "ui/export_config.json")

        self.ui = None
        self.init_ui()
        self.create_connections()

    def init_ui(self):
        self.qt_form.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(self.qt_form, parentWidget=self)
        self.qt_form.close()
        self.load_user_config()

    def init_animation_exporter(self):
        output_directory = self.user_data["OutputDirectory"]
        output_file = "{0}.{1}".format(os.path.join(self.user_data["OutputDirectory"], self.user_data["ClipName"]),
                                       self.user_data["FileExtension"])
        resource = self.user_data["ClipName"]
        skeleton = self.user_data["GameSkeleton"]
        anim_exporter = anim_export.AnimExport(output_directory=output_directory,
                                               output_file=output_file,
                                               resource=resource,
                                               skeleton=skeleton)
        anim_exporter.export()

    def init_skeleton_generator(self, command):
        rig_skeleton = self.user_data["RigSkeleton"]
        root_control = self.user_data["RootControl"]
        game_prefix = self.user_data["GamePrefix"]
        skeleton_generator = game_skeleton.CreateGameSkeleton(rig_skeleton=rig_skeleton,
                                                              root_control=root_control,
                                                              game_prefix=game_prefix)
        if command == "GenerateSkeleton":
            skeleton_generator.create_game_skeleton()
        elif command == "AddTrajectory":
            skeleton_generator.add_trajectory_to_rig_skeleton()
        elif command == "BindGameSkeleton":
            skeleton_generator.bind_to_game_skeleton()

    def init_model_fbx_exporter(self):
        export_directory = self.user_data["ExportModelFBXDirectory"]
        export_model = self.user_data["ModelName"]
        model_export = model_fbx_export.ModelFBXExport(export_directory=export_directory,
                                                       export_model=export_model)
        model_export.export()

    def create_connections(self):
        # AnimationExport tab
        self.ui.GetStartFrame_pushButton.clicked.connect(lambda ind:
                                                         self.set_text_field
                                                         (string=str(anim_utils.get_timeline_info()["Start"]),
                                                          field=self.ui.StartFrame_lineEdit,
                                                          key="StartFrame"))

        self.ui.GetEndFrame_pushButton.clicked.connect(lambda ind:
                                                       self.set_text_field
                                                       (string=str(anim_utils.get_timeline_info()["End"]),
                                                        field=self.ui.EndFrame_lineEdit,
                                                        key="EndFrame"))

        self.ui.GetFPS_pushButton.clicked.connect(lambda ind:
                                                  self.set_combo_box
                                                  (string=str(anim_utils.get_timeline_info()["FPS"]),
                                                   field=self.ui.FPScomboBox,
                                                   key="FPS"))

        self.ui.SetStartFrame_pushButton.clicked.connect(lambda ind:
                                                         anim_utils.set_start_or_end_frame
                                                         (position="start",
                                                          value=self.ui.StartFrame_lineEdit.text()))

        self.ui.SetEndFrame_pushButton.clicked.connect(lambda ind:
                                                       anim_utils.set_start_or_end_frame
                                                       (position="end",
                                                        value=self.ui.EndFrame_lineEdit.text()))

        self.ui.SetFPS_pushButton.clicked.connect(lambda ind:
                                                  anim_utils.set_fps(self.ui.FPScomboBox.currentText()))

        self.ui.StartFrame_lineEdit.textChanged.connect(lambda ind:
                                                        self.update_user_data
                                                        (key="StartFrame",
                                                         value=self.ui.StartFrame_lineEdit.text()))

        self.ui.EndFrame_lineEdit.textChanged.connect(lambda ind:
                                                      self.update_user_data
                                                      (key="EndFrame",
                                                       value=self.ui.EndFrame_lineEdit.text()))

        self.ui.GameSkeleton_lineEdit.textChanged.connect(lambda ind:
                                                          self.update_user_data
                                                          (key="GameSkeleton",
                                                           value=self.ui.GameSkeleton_lineEdit.text()))

        self.ui.ClipName_lineEdit.textChanged.connect(lambda ind:
                                                      self.update_user_data
                                                      (key="ClipName",
                                                       value=self.ui.ClipName_lineEdit.text()))

        self.ui.FPScomboBox.currentIndexChanged.connect(lambda ind:
                                                        self.update_user_data
                                                        (key="FPS",
                                                         value=self.ui.FPScomboBox.currentText()))

        self.ui.OutputDirectory_lineEdit.textChanged.connect(lambda ind:
                                                             self.update_user_data
                                                             (key="OutputDirectory",
                                                              value=self.ui.OutputDirectory_lineEdit.text()))

        self.ui.BrowseOutputDir_pushButton.clicked.connect(lambda ind:
                                                           self.output_file_dialog
                                                           (directory="AnimationExportDirectory"))

        self.ui.Export_pushButton.clicked.connect(self.init_animation_exporter)

        # Tab data
        self.ui.Main_tabWidget.currentChanged.connect(lambda ind:
                                                      self.update_user_data
                                                      (key="CurrentTab",
                                                       value=self.ui.Main_tabWidget.currentIndex()))

        # Generate Skeleton tab
        self.ui.RigSkeleton_lineEdit.textChanged.connect(lambda ind:
                                                         self.update_user_data
                                                         (key="RigSkeleton",
                                                          value=self.ui.RigSkeleton_lineEdit.text()))

        self.ui.RootControl_lineEdit.textChanged.connect(lambda ind:
                                                         self.update_user_data
                                                         (key="RootControl",
                                                          value=self.ui.RootControl_lineEdit.text()))

        self.ui.GamePrefix_lineEdit.textChanged.connect(lambda ind:
                                                        self.update_user_data
                                                        (key="GamePrefix",
                                                         value=self.ui.GamePrefix_lineEdit.text()))

        self.ui.GenerateSkeleton_pushButton.clicked.connect(lambda ind:
                                                            self.init_skeleton_generator
                                                            (command="GenerateSkeleton"))

        self.ui.AddTrajectory_pushButton.clicked.connect(lambda ind:
                                                         self.init_skeleton_generator
                                                         (command="AddTrajectory"))

        self.ui.BindGameSkeleton_pushButton.clicked.connect(lambda ind:
                                                            self.init_skeleton_generator
                                                            (command="BindGameSkeleton"))

        # Export Model FBX tab
        self.ui.ModelFBXExportDirectory_lineEdit.textChanged.connect(lambda ind:
                                                                     self.update_user_data
                                                                     (key="ExportModelFBXDirectory",
                                                                      value=self.ui.
                                                                      ModelFBXExportDirectory_lineEdit.text()))

        self.ui.ModelName_lineEdit.textChanged.connect(lambda ind:
                                                       self.update_user_data
                                                       (key="ModelName",
                                                        value=self.ui.ModelName_lineEdit.text()))

        self.ui.BrowseExportDir_pushButton.clicked.connect(lambda ind:
                                                           self.output_file_dialog
                                                           (directory="ExportModelFBXDirectory"))

        self.ui.ExportModelFBX_pushButton.clicked.connect(self.init_model_fbx_exporter)

    def set_text_field(self, string="", field=None, key=None):
        field.setText(string)
        self.update_user_data(key, value=string)

    def set_combo_box(self, string="", field=None, key=None):
        field.setCurrentText(string)
        self.update_user_data(key, value=string)

    def update_user_data(self, key=None, value=None):
        self.user_data[key] = value
        with open(self.config_file, "w") as out_config:
            json.dump(self.user_data, out_config, indent=4)

    def load_user_config(self):
        config_exists = os.path.isfile(self.config_file)
        if config_exists:
            with open(self.config_file, "r") as in_config:
                # ExportAnimation tab
                self.user_data = json.load(in_config)
                self.ui.GameSkeleton_lineEdit.setText(self.user_data["GameSkeleton"])
                self.ui.ClipName_lineEdit.setText(self.user_data["ClipName"])
                self.ui.OutputDirectory_lineEdit.setText(self.user_data["OutputDirectory"])
                self.ui.StartFrame_lineEdit.setText(self.user_data["StartFrame"])
                self.ui.EndFrame_lineEdit.setText(self.user_data["EndFrame"])
                self.ui.FPScomboBox.setCurrentText(self.user_data["FPS"])

                # GenerateGameSkeleton tab
                self.ui.RigSkeleton_lineEdit.setText(self.user_data["RigSkeleton"])
                self.ui.RootControl_lineEdit.setText(self.user_data["RootControl"])
                self.ui.GamePrefix_lineEdit.setText(self.user_data["GamePrefix"])

                # ExportModelFBX tab
                self.ui.ModelFBXExportDirectory_lineEdit.setText(self.user_data["ExportModelFBXDirectory"])
                self.ui.ModelName_lineEdit.setText(self.user_data["ModelName"])

                # Tab data
                self.ui.Main_tabWidget.setCurrentIndex(self.user_data["CurrentTab"])

    def output_file_dialog(self, directory):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')

        if folder_path:
            if directory == "AnimationExportDirectory":
                self.ui.OutputDirectory_lineEdit.setText(folder_path)
            elif directory == "ExportModelFBXDirectory":
                self.ui.ModelFBXExportDirectory_lineEdit.setText(folder_path)
