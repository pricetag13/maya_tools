from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import os
import json

from lookat_assembly import AssembleLookAt


class SetUpLookAtWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SetUpLookAtWidget, self).__init__(parent=parent)

        # Get paths
        root_path = os.path.dirname(os.path.abspath(__file__))
        self.set_up_lookat_config = r"{0}\setup_lookat_config.txt".format(root_path)

        # Create widgets.
        self.left_eye_root_line_edit = QtWidgets.QLineEdit()
        self.left_eye_root_line_edit.setMinimumWidth(240)
        self.right_eye_root_line_edit = QtWidgets.QLineEdit()
        self.head_control_line_edit = QtWidgets.QLineEdit()
        self.root_control_line_edit = QtWidgets.QLineEdit()

        self.upper_range_line_edit = QtWidgets.QLineEdit()
        self.upper_range_line_edit.setMaxLength(4)
        self.upper_range_line_edit.setFixedWidth(30)
        self.upper_range_line_edit.setValidator(QtGui.QIntValidator())

        self.lower_range_line_edit = QtWidgets.QLineEdit()
        self.lower_range_line_edit.setMaxLength(4)
        self.lower_range_line_edit.setFixedWidth(30)
        self.lower_range_line_edit.setValidator(QtGui.QIntValidator())

        self.inner_range_line_edit = QtWidgets.QLineEdit()
        self.inner_range_line_edit.setMaxLength(4)
        self.inner_range_line_edit.setFixedWidth(30)
        self.inner_range_line_edit.setValidator(QtGui.QIntValidator())

        self.outer_range_line_edit = QtWidgets.QLineEdit()
        self.outer_range_line_edit.setMaxLength(4)
        self.outer_range_line_edit.setFixedWidth(30)
        self.outer_range_line_edit.setValidator(QtGui.QIntValidator())

        self.horizontal_axis_combo_box = QtWidgets.QComboBox()
        self.horizontal_axis_combo_box.setMaximumWidth(40)
        self.horizontal_axis_combo_box.addItem("x")
        self.horizontal_axis_combo_box.addItem("y")
        self.horizontal_axis_combo_box.addItem("z")

        self.vertical_axis_combo_box = QtWidgets.QComboBox()
        self.vertical_axis_combo_box.setMaximumWidth(40)
        self.vertical_axis_combo_box.addItem("x")
        self.vertical_axis_combo_box.addItem("y")
        self.vertical_axis_combo_box.addItem("z")

        self.eye_icon_button = QtWidgets.QPushButton()
        self.eye_icon_button.setFixedSize(60, 60)
        eye_range_graphic = r"{0}\icons\graphic_eye.png".format(root_path)
        eye_range_icon = QtGui.QPixmap(eye_range_graphic)
        self.eye_icon_button.setIcon(eye_range_icon)
        self.eye_icon_button.setIconSize(QtCore.QSize(60, 60))

        self.max_range_label = QtWidgets.QLabel("Max Ranges:")

        self.set_up_button = QtWidgets.QPushButton("Add Lookat")
        self.set_up_button.setMinimumWidth(80)
        self.set_up_button.setMinimumHeight(45)

        # Create layouts.
        required_scene_component_form_layout = QtWidgets.QFormLayout()
        required_scene_component_form_layout.addRow("Left Eye Root:", self.left_eye_root_line_edit)
        required_scene_component_form_layout.addRow("Right Eye Root:", self.right_eye_root_line_edit)
        required_scene_component_form_layout.addRow("Head Control:", self.head_control_line_edit)
        required_scene_component_form_layout.addRow("Root Control:", self.root_control_line_edit)

        eye_range_grid_layout = QtWidgets.QGridLayout()
        eye_range_grid_layout.addWidget(self.max_range_label, 0, 0)
        eye_range_grid_layout.addWidget(self.eye_icon_button, 1, 1)

        eye_range_grid_layout.addWidget(self.upper_range_line_edit, 0, 1, QtCore.Qt.AlignCenter)
        eye_range_grid_layout.addWidget(self.outer_range_line_edit, 1, 0, QtCore.Qt.AlignRight)
        eye_range_grid_layout.addWidget(self.inner_range_line_edit, 1, 2)
        eye_range_grid_layout.addWidget(self.lower_range_line_edit, 2, 1, QtCore.Qt.AlignCenter)

        eye_range_grid_layout.addWidget(self.horizontal_axis_combo_box, 1, 3)
        eye_range_grid_layout.addWidget(self.vertical_axis_combo_box, 3, 1, QtCore.Qt.AlignCenter)

        top_variable_input_layout = QtWidgets.QHBoxLayout()
        top_variable_input_layout.addLayout(required_scene_component_form_layout)
        top_variable_input_layout.addLayout(eye_range_grid_layout)

        run_set_up_layout = QtWidgets.QHBoxLayout()
        run_set_up_layout.addStretch()
        run_set_up_layout.addWidget(self.set_up_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_variable_input_layout)
        main_layout.addLayout(run_set_up_layout)

        self.create_connections()
        self.read_values_from_json_config()

    def create_connections(self):
        """set up all the ui signals and slots"""
        self.left_eye_root_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.right_eye_root_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.head_control_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.root_control_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.upper_range_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.lower_range_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.inner_range_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.outer_range_line_edit.textChanged.connect(self.write_user_values_to_json_config)
        self.horizontal_axis_combo_box.currentIndexChanged.connect(self.write_user_values_to_json_config)
        self.vertical_axis_combo_box.currentIndexChanged.connect(self.write_user_values_to_json_config)

        self.set_up_button.clicked.connect(self.run_lookat_set_up)

    def collect_user_input_data(self):
        user_input_dictionary = {'LeftEyeRoot': self.left_eye_root_line_edit.text(),
                                 'RightEyeRoot': self.right_eye_root_line_edit.text(),
                                 'HeadControl': self.head_control_line_edit.text(),
                                 'RootControl': self.root_control_line_edit.text(),
                                 'UpperRange': self.upper_range_line_edit.text(),
                                 'LowerRange': self.lower_range_line_edit.text(),
                                 'InnerRange': self.inner_range_line_edit.text(),
                                 'OuterRange': self.outer_range_line_edit.text(),
                                 'HorizontalAxis': self.horizontal_axis_combo_box.currentText(),
                                 'VerticalAxis': self.vertical_axis_combo_box.currentText()
                                 }
        return user_input_dictionary

    def write_user_values_to_json_config(self):
        with open(self.set_up_lookat_config, 'w') as file_for_write:
            json.dump(self.collect_user_input_data(), file_for_write)

    def read_values_from_json_config(self):
        with open(self.set_up_lookat_config, 'r') as file_to_read:
            lookat_setup_config_read = json.load(file_to_read)
            self.left_eye_root_line_edit.setText(lookat_setup_config_read['LeftEyeRoot'])
            self.right_eye_root_line_edit.setText(lookat_setup_config_read['RightEyeRoot'])
            self.head_control_line_edit.setText(lookat_setup_config_read['HeadControl'])
            self.root_control_line_edit.setText(lookat_setup_config_read['RootControl'])
            self.upper_range_line_edit.setText(lookat_setup_config_read['UpperRange'])
            self.lower_range_line_edit.setText(lookat_setup_config_read['LowerRange'])
            self.inner_range_line_edit.setText(lookat_setup_config_read['InnerRange'])
            self.outer_range_line_edit.setText(lookat_setup_config_read['OuterRange'])
            self.horizontal_axis_combo_box.setCurrentText(lookat_setup_config_read['HorizontalAxis'])
            self.vertical_axis_combo_box.setCurrentText(lookat_setup_config_read['VerticalAxis'])

    @staticmethod
    def run_lookat_set_up():
        lookat_assembly = AssembleLookAt()
        lookat_assembly.run_assembly()

