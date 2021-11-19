from PySide2 import QtWidgets
import os

from maya import cmds

import plotting_utilities


class PlottingWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PlottingWidget, self).__init__(parent=parent)

        # Get paths
        root_path = os.path.dirname(os.path.abspath(__file__))
        self.set_up_lookat_config = r"{0}\setup_lookat_config.txt".format(root_path)
        self.namespace = ""

        # Namespace widgets.
        namespace_label = QtWidgets.QLabel("Namespace:")
        self.namespace_combo_box = QtWidgets.QComboBox()
        self.namespace_combo_box.setMinimumWidth(360)
        self.refresh_namespace_button = QtWidgets.QPushButton("Refresh")

        # Namespace layout.
        namespace_layout = QtWidgets.QHBoxLayout()
        namespace_layout.addWidget(namespace_label)
        namespace_layout.addWidget(self.namespace_combo_box)
        namespace_layout.addWidget(self.refresh_namespace_button)

        # Title widgets.
        title_label = QtWidgets.QLabel("Plot Animation")
        title_line = QtWidgets.QFrame()
        title_line.setMinimumWidth(475)
        title_line.setFrameShape(QtWidgets.QFrame.HLine)
        title_line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Title layout.
        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(title_line)

        # Timeline widgets.
        start_frame_label = QtWidgets.QLabel("Start Frame")
        self.start_frame_spin_box = QtWidgets.QSpinBox()
        self.start_frame_spin_box.setMinimumWidth(80)
        self.start_frame_spin_box.setMinimum(-99999)
        self.start_frame_spin_box.setMaximum(99999)
        end_frame_label = QtWidgets.QLabel("End Frame")
        self.end_frame_spin_box = QtWidgets.QSpinBox()
        self.end_frame_spin_box.setMinimumWidth(80)
        self.end_frame_spin_box.setMinimum(-99999)
        self.end_frame_spin_box.setMaximum(99999)
        self.update_from_timeline_button = QtWidgets.QPushButton("Update")

        # Timeline layout.
        timeline_layout = QtWidgets.QHBoxLayout()
        timeline_layout.addWidget(start_frame_label)
        timeline_layout.addWidget(self.start_frame_spin_box)
        timeline_layout.addStretch()
        timeline_layout.addWidget(end_frame_label)
        timeline_layout.addWidget(self.end_frame_spin_box)
        timeline_layout.addWidget(self.update_from_timeline_button)

        # Set lookat widgets.
        self.maintain_distance_radio_button = QtWidgets.QRadioButton("Maintain Lookat Distance")
        self.use_set_distance_radio_button = QtWidgets.QRadioButton("Use Set Lookat Distance")
        self.use_set_distance_radio_button.setChecked(True)
        self.lookat_distance_button_group = QtWidgets.QButtonGroup()
        self.lookat_distance_button_group.addButton(self.maintain_distance_radio_button)
        self.lookat_distance_button_group.addButton(self.use_set_distance_radio_button)
        self.use_set_distance_spin_box = QtWidgets.QSpinBox()
        self.use_set_distance_spin_box.setMinimumWidth(80)
        self.use_set_distance_spin_box.setMinimum(5)
        self.use_set_distance_spin_box.setMaximum(9999)
        self.use_set_distance_spin_box.setProperty("value", 40)
        self.align_lookat_button = QtWidgets.QPushButton("Align")

        # Set lookat layout.
        set_lookat_layout = QtWidgets.QHBoxLayout()
        set_lookat_layout.addWidget(self.maintain_distance_radio_button)
        set_lookat_layout.addStretch()
        set_lookat_layout.addWidget(self.use_set_distance_radio_button)
        set_lookat_layout.addWidget(self.use_set_distance_spin_box)
        set_lookat_layout.addWidget(self.align_lookat_button)

        # Run plot widgets.
        self.world_space_radio_button = QtWidgets.QRadioButton("World")
        self.world_space_radio_button.setChecked(True)
        self.local_space_radio_button = QtWidgets.QRadioButton("Local")
        self.au_space_radio_button = QtWidgets.QRadioButton("AUEyes")
        self.lookat_set_space_button_group = QtWidgets.QButtonGroup()
        self.lookat_set_space_button_group.addButton(self.world_space_radio_button)
        self.lookat_set_space_button_group.addButton(self.local_space_radio_button)
        self.lookat_set_space_button_group.addButton(self.au_space_radio_button)
        self.smart_bake_check_box = QtWidgets.QCheckBox("Smart Bake")
        self.run_plot_button = QtWidgets.QPushButton("Plot")
        self.run_plot_button.setMinimumHeight(45)
        self.run_plot_button.setMinimumWidth(120)

        # Run plot layout.
        run_plot_layout = QtWidgets.QHBoxLayout()
        run_plot_layout.addWidget(self.world_space_radio_button)
        run_plot_layout.addWidget(self.local_space_radio_button)
        run_plot_layout.addWidget(self.au_space_radio_button)
        run_plot_layout.addStretch()
        run_plot_layout.addWidget(self.smart_bake_check_box)
        run_plot_layout.addWidget(self.run_plot_button)

        # Create main layout.
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(namespace_layout)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(timeline_layout)
        main_layout.addLayout(set_lookat_layout)
        main_layout.addLayout(run_plot_layout)

        # Initialize rig components.

        self.look_at_main_control_curve = 'lookat_ctl'
        self.look_at_left_control_curve = 'L_lookat_ctl'
        self.look_at_right_control_curve = 'R_lookat_ctl'

        self.au_eyes_main_control_curve = 'au_eyes_ctl'
        self.au_eyes_left_control_curve = 'L_au_eyes_ctl'
        self.au_eyes_right_control_curve = 'R_au_eyes_ctl'

        self.main_lookat_final_translation = 'C_absolute_position_loc'
        self.left_lookat_final_translation = 'L_absolute_position_loc'
        self.right_lookat_final_translation = 'R_absolute_position_loc'

        self.eyes_combined_values = 'eyes_combined_values'
        self.plot_to_au_values = 'plot_to_au_values'
        self.user_defined_distance_loc = 'user_defined_distance_loc'

        # self.control_vis = ""

        self.controls = {"LookAt": "lookat_ctl",
                         "AUEyes": "au_eyes_ctl"}

        self.control_transform_dict = {}
        self.control_curve_tuple_list = []
        self.combined_keys_to_plot = []

        # Initialize default values and connections.
        self.__initialize_default_values()
        self.__connections()

    def __initialize_default_values(self):
        """ sets default values in the ui """
        self.refresh_namespaces()
        self.time_from_timeline()

    def __connections(self):
        """set up all the ui signals and slots"""
        self.refresh_namespace_button.clicked.connect(self.refresh_namespaces)
        self.namespace_combo_box.activated.connect(self.set_namespace)
        self.update_from_timeline_button.clicked.connect(self.time_from_timeline)
        self.align_lookat_button.clicked.connect(self.align_lookat_position)
        self.run_plot_button.clicked.connect(self.plot_animation_switch)

    def refresh_namespaces(self):
        """queries scene for existing namespaces then updates the combo box. if the user has
        something selected, it will set the namespace in the ui to the namespace of selection"""
        namespaces = plotting_utilities.get_namespaces()
        self.namespace_combo_box.clear()
        self.namespace_combo_box.addItems(namespaces)

        # selection = cmds.ls(sl=True) or list()
        # if selection:
        #     namespace = OpenMaya.MNamespace.getNamespaceFromName(selection[0]) or ":"
        #     index = self.namespace_combo_box.findText(namespace)
        #     if index >= 0:
        #         self.namespace_combo_box.setCurrentIndex(index)

    def set_namespace(self):
        self.namespace = self.namespace_combo_box.currentText()

    def time_from_timeline(self):
        """ gets the start and end frame from the timeline """
        min_frame, max_frame = plotting_utilities.get_timeline_range()

        self.start_frame_spin_box.setValue(min_frame)
        self.end_frame_spin_box.setValue(max_frame)

    def get_timerange(self):
        """returns the values stored in the UI spin boxes"""
        return int(self.start_frame_spin_box.value()), int(self.end_frame_spin_box.value())

    def get_visibility_control(self):
        enable_lookat_control = ''
        all_transforms = cmds.ls(type='transform')
        for transform in all_transforms:
            enable_lookat_attribute_exists = cmds.attributeQuery("enable_lookat", node=transform, exists=True)
            if enable_lookat_attribute_exists:
                enable_lookat_control = '{0}{1}'.format(self.namespace, transform)
        return enable_lookat_control

    def get_active_eye_controls(self):
        active_control = ''
        if cmds.getAttr('{0}{1}.enable_lookat'.format(self.namespace, self.get_visibility_control())) == 0:
            active_control = 'au_eyes'
        elif cmds.getAttr('{0}{1}.enable_lookat'.format(self.namespace, self.get_visibility_control())) == 1 \
                and cmds.getAttr('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace)) == 0:
            active_control = 'lookat_world'
        elif cmds.getAttr('{0}:{1}.enable_lookat'.format(self.namespace, self.get_visibility_control())) == 1 \
                and cmds.getAttr('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace)) == 1:
            active_control = 'lookat_local'
        return active_control

    def align_lookat_position(self):
        """Initializes Position of the LookAt control"""
        user_defined_distance = self.use_set_distance_spin_box.value()

        cmds.setAttr('{0}:{1}.tz'.format(self.namespace, self.user_defined_distance_loc), user_defined_distance)
        cmds.matchTransform('{0}:{1}'.format(self.namespace, self.look_at_main_control_curve),
                            '{0}:{1}'.format(self.namespace, self.user_defined_distance_loc))

    @plotting_utilities.undo_able
    @plotting_utilities.disable_viewport
    def plot_animation_switch(self):
        """queries the ui for the namespace and control to plot animation to."""
        self.set_namespace()
        current_frame = plotting_utilities.get_current_frame()

        aim_ctl = "{0}:{1}".format(self.namespace, self.controls.get("LookAt"))

        # Check if the animation can be plotted
        if not cmds.objExists(aim_ctl):
            raise RuntimeError("The selected namespace doesn't appear to have a LookAt Control")

        source_ctl = self.get_active_eye_controls()
        target_ctl = ''

        if self.world_space_radio_button.isChecked():
            target_ctl = 'lookat_world'
        elif self.local_space_radio_button.isChecked():
            target_ctl = 'lookat_local'
        elif self.au_space_radio_button.isChecked():
            target_ctl = 'au_eyes'

        if source_ctl == 'au_eyes' and target_ctl == 'lookat_local':
            self.plot_au_to_local()
        if source_ctl == 'au_eyes' and target_ctl == 'lookat_world':
            self.plot_au_to_world()
        if source_ctl == 'lookat_local' and target_ctl == 'lookat_local':
            self.plot_local_to_local()
        if source_ctl == 'lookat_local' and target_ctl == 'lookat_world':
            self.plot_local_to_world()
        if source_ctl == 'lookat_local' and target_ctl == 'au_eyes':
            self.plot_local_to_au()
        if source_ctl == 'lookat_world' and target_ctl == 'lookat_local':
            self.plot_world_to_local()
        if source_ctl == 'lookat_world' and target_ctl == 'lookat_world':
            self.plot_world_to_world()
        if source_ctl == 'lookat_world' and target_ctl == 'au_eyes':
            self.plot_world_to_au()

        cmds.currentTime(current_frame)

    def plot_au_to_local(self):
        if self.use_set_distance_radio_button.isChecked():
            self.reset_lookat()
            cmds.cutKey('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace))
            cmds.setAttr("{0}:lookat_ctl.SpaceWorldHead".format(self.namespace), 1)
            self.align_lookat_position()
            self.capture_plot_frames_for_lookat()
            self.write_plot_frames_to_lookat()

        if self.maintain_distance_radio_button.isChecked():
            cmds.cutKey('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace))
            cmds.setAttr("{0}:lookat_ctl.SpaceWorldHead".format(self.namespace), 1)
            self.capture_plot_frames_for_lookat()
            self.write_plot_frames_to_lookat()

        cmds.setAttr('{0}:{1}.enable_lookat'.format(self.namespace, self.get_visibility_control()), 1)
        cmds.select('{0}:{1}'.format(self.namespace, self.look_at_main_control_curve))

    def plot_au_to_world(self):
        if self.use_set_distance_radio_button.isChecked():
            self.reset_lookat()
            cmds.cutKey('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace))
            cmds.setAttr("{0}:lookat_ctl.SpaceWorldHead".format(self.namespace), 0)
            self.align_lookat_position()
            self.capture_plot_frames_for_lookat()
            self.write_plot_frames_to_lookat()

        if self.maintain_distance_radio_button.isChecked():
            cmds.cutKey('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace))
            cmds.setAttr("{0}:lookat_ctl.SpaceWorldHead".format(self.namespace), 0)
            self.capture_plot_frames_for_lookat()
            self.write_plot_frames_to_lookat()

        cmds.setAttr('{0}{1}.enable_lookat'.format(self.namespace, self.get_visibility_control()), 1)
        cmds.select('{0}{1}'.format(self.namespace, self.look_at_main_control_curve))

    def plot_local_to_local(self):
        self.plot_local_to_au()
        self.plot_au_to_local()

    def plot_local_to_world(self):
        if self.use_set_distance_radio_button.isChecked():
            self.plot_local_to_au()
            self.plot_au_to_world()
        if self.maintain_distance_radio_button.isChecked():
            self.capture_plot_frames_for_space_swap()
            self.reset_lookat()
            cmds.cutKey('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace))
            cmds.setAttr("{0}:lookat_ctl.SpaceWorldHead".format(self.namespace), 0)
            self.write_plot_frames_for_space_swap()

    def plot_local_to_au(self):
        self.capture_plot_frames_for_au_eyes()
        self.write_plot_frames_to_au_eyes()
        cmds.setAttr('{0}:{1}.enable_lookat'.format(self.namespace, self.get_visibility_control()), 0)
        cmds.select('{0}:{1}'.format(self.namespace, self.au_eyes_main_control_curve))

    def plot_world_to_world(self):
        self.plot_world_to_au()
        self.plot_au_to_world()

    def plot_world_to_local(self):
        if self.use_set_distance_radio_button.isChecked():
            self.plot_local_to_au()
            self.plot_au_to_local()
        if self.maintain_distance_radio_button.isChecked():
            self.capture_plot_frames_for_space_swap()
            self.reset_lookat()
            cmds.cutKey('{0}:lookat_ctl.SpaceWorldHead'.format(self.namespace))
            cmds.setAttr("{0}:lookat_ctl.SpaceWorldHead".format(self.namespace), 1)
            self.write_plot_frames_for_space_swap()

    def plot_world_to_au(self):
        self.capture_plot_frames_for_au_eyes()
        self.write_plot_frames_to_au_eyes()
        cmds.setAttr('{0}:{1}.enable_lookat'.format(self.namespace, self.get_visibility_control()), 0)
        cmds.select('{0}:{1}'.format(self.namespace, self.au_eyes_main_control_curve))

    def capture_plot_frames_for_space_swap(self):
        smart_bake = self.smart_bake_check_box.isChecked()
        startframe, endframe = self.get_timerange()

        control_curve_tuple_list = [
            ('{0}:{1}'.format(self.namespace, self.look_at_main_control_curve),
             '{0}:{1}'.format(self.namespace, self.main_lookat_final_translation)),

            ('{0}:{1}'.format(self.namespace, self.look_at_left_control_curve),
             '{0}:{1}'.format(self.namespace, self.left_lookat_final_translation)),

            ('{0}:{1}'.format(self.namespace, self.look_at_right_control_curve),
             '{0}:{1}'.format(self.namespace, self.right_lookat_final_translation))
        ]

        combined_keys_to_plot = []
        if not smart_bake:
            combined_keys_to_plot = range(startframe, endframe + 1)
        else:
            for control_curve_tuple in control_curve_tuple_list:
                # Unpack control_curve_tuples
                source_control = control_curve_tuple[0]
                keys_to_plot = self.get_sparse_bake_index(source_control)
                # Combine control keys into a single list.
                for key in keys_to_plot:
                    if key not in combined_keys_to_plot:
                        combined_keys_to_plot.append(key)

        # Record final position of "lookAt" controls
        control_transform_dict = {}
        for key in combined_keys_to_plot:
            key_list = []
            cmds.currentTime(key)
            for control_curve_tuple in control_curve_tuple_list:
                target_control = control_curve_tuple[0]
                final_translation = control_curve_tuple[0]
                transform_list = cmds.xform(final_translation, query=True, worldSpace=True, rotatePivot=True)
                key_list.append((target_control, transform_list))
            control_transform_dict[key] = key_list

        # Flatten animation curves that we will be replacing
        flatten_curve_list = [
            '{0}:lookat_ctl.tx'.format(self.namespace),
            '{0}:lookat_ctl.ty'.format(self.namespace),
            '{0}:lookat_ctl.tz'.format(self.namespace),
            '{0}:L_lookat_ctl.tx'.format(self.namespace),
            '{0}:L_lookat_ctl.ty'.format(self.namespace),
            '{0}:L_lookat_ctl.tz'.format(self.namespace),
            '{0}:R_lookat_ctl.tx'.format(self.namespace),
            '{0}:R_lookat_ctl.ty'.format(self.namespace),
            '{0}:R_lookat_ctl.tz'.format(self.namespace)
        ]
        plotting_utilities.flatten_anim_curve(flatten_curve_list, startframe, endframe)
        self.control_transform_dict = control_transform_dict

    def write_plot_frames_for_space_swap(self):
        for key, value in self.control_transform_dict.iteritems():

            keyframe = key

            main_ctl_tupple = value[0]
            main_ctl = main_ctl_tupple[0]
            main_ctl_xform = main_ctl_tupple[1]

            left_ctl_tupple = value[1]
            left_ctl = left_ctl_tupple[0]
            left_ctl_xform = left_ctl_tupple[1]

            right_ctl_tupple = value[2]
            right_ctl = right_ctl_tupple[0]
            right_ctl_xform = right_ctl_tupple[1]

            cmds.currentTime(key)

            cmds.xform(main_ctl, translation=main_ctl_xform, worldSpace=True)
            cmds.xform(left_ctl, translation=left_ctl_xform, worldSpace=True)
            cmds.xform(right_ctl, translation=right_ctl_xform, worldSpace=True)

            cmds.setKeyframe(main_ctl, attribute='tx', time=[keyframe, keyframe])
            cmds.setKeyframe(main_ctl, attribute='ty', time=[keyframe, keyframe])
            cmds.setKeyframe(main_ctl, attribute='tz', time=[keyframe, keyframe])

            cmds.setKeyframe(left_ctl, attribute='tx', time=[keyframe, keyframe])
            cmds.setKeyframe(left_ctl, attribute='ty', time=[keyframe, keyframe])
            cmds.setKeyframe(left_ctl, attribute='tz', time=[keyframe, keyframe])

            cmds.setKeyframe(right_ctl, attribute='tx', time=[keyframe, keyframe])
            cmds.setKeyframe(right_ctl, attribute='ty', time=[keyframe, keyframe])
            cmds.setKeyframe(right_ctl, attribute='tz', time=[keyframe, keyframe])

    def capture_plot_frames_for_lookat(self):
        smart_bake = self.smart_bake_check_box.isChecked()
        startframe, endframe = self.get_timerange()

        control_curve_tuple_list = [
            ('{0}:{1}'.format(self.namespace, self.au_eyes_main_control_curve),
             '{0}:{1}'.format(self.namespace, self.look_at_main_control_curve),
             '{0}:{1}'.format(self.namespace, self.main_lookat_final_translation)),

            ('{0}:{1}'.format(self.namespace, self.au_eyes_left_control_curve),
             '{0}:{1}'.format(self.namespace, self.look_at_left_control_curve),
             '{0}:{1}'.format(self.namespace, self.left_lookat_final_translation)),

            ('{0}:{1}'.format(self.namespace, self.au_eyes_right_control_curve),
             '{0}:{1}'.format(self.namespace, self.look_at_right_control_curve),
             '{0}:{1}'.format(self.namespace, self.right_lookat_final_translation))
        ]

        # Get list of keys for all of the "eyes_au" controls
        combined_keys_to_plot = []
        if not smart_bake:
            combined_keys_to_plot = range(startframe, endframe + 1)
        else:
            for control_curve_tuple in control_curve_tuple_list:
                # Unpack control_curve_tuples
                source_control = control_curve_tuple[0]
                keys_to_plot = self.get_sparse_bake_index(source_control)
                # Combine control keys into a single list.
                for key in keys_to_plot:
                    if key not in combined_keys_to_plot:
                        combined_keys_to_plot.append(key)

        # Record final position of "lookAt" controls
        control_transform_dict = {}
        for key in combined_keys_to_plot:
            cmds.currentTime(key)
            if self.use_set_distance_radio_button.isChecked():
                self.align_lookat_position()
            for control_curve_tuple in control_curve_tuple_list:
                target_control = control_curve_tuple[1]
                final_translation = control_curve_tuple[2]
                cmds.matchTransform(target_control, final_translation,
                                    position=True, rotation=False)
                transform_list = cmds.xform(target_control, query=True, translation=True)

                key_control_tuple = (key, target_control)
                control_transform_dict[key_control_tuple] = transform_list

        # Flatten animation curves that we will be replacing
        flatten_curve_list = [
            '{0}:lookat_ctl.tx'.format(self.namespace),
            '{0}:lookat_ctl.ty'.format(self.namespace),
            '{0}:lookat_ctl.tz'.format(self.namespace),
            '{0}:L_lookat_ctl.tx'.format(self.namespace),
            '{0}:L_lookat_ctl.ty'.format(self.namespace),
            '{0}:L_lookat_ctl.tz'.format(self.namespace),
            '{0}:R_lookat_ctl.tx'.format(self.namespace),
            '{0}:R_lookat_ctl.ty'.format(self.namespace),
            '{0}:R_lookat_ctl.tz'.format(self.namespace)
        ]
        plotting_utilities.flatten_anim_curve(flatten_curve_list, startframe, endframe)
        self.control_transform_dict = control_transform_dict

    def write_plot_frames_to_lookat(self):
        for key, value in self.control_transform_dict.iteritems():
            keyframe = key[0]
            target_control = key[1]
            x_val = value[0]
            y_val = value[1]
            z_val = value[2]

            cmds.setKeyframe(target_control, value=x_val, attribute='tx', time=[keyframe, keyframe])
            cmds.setKeyframe(target_control, value=y_val, attribute='ty', time=[keyframe, keyframe])
            cmds.setKeyframe(target_control, value=z_val, attribute='tz', time=[keyframe, keyframe])

    def capture_plot_frames_for_au_eyes(self):
        smart_bake = self.smart_bake_check_box.isChecked()
        startframe, endframe = self.get_timerange()

        # Flatten animation keys that we will be replacing
        flatten_curve_list = [
            '{0}:au_eyes_ctl.tx'.format(self.namespace),
            '{0}:au_eyes_ctl.ty'.format(self.namespace),
            '{0}:L_au_eyes_ctl.tx'.format(self.namespace),
            '{0}:L_au_eyes_ctl.ty'.format(self.namespace),
            '{0}:R_au_eyes_ctl.tx'.format(self.namespace),
            '{0}:R_au_eyes_ctl.ty'.format(self.namespace),
        ]
        plotting_utilities.flatten_anim_curve(flatten_curve_list, startframe, endframe)

        self.control_curve_tuple_list = [
            ('{0}:{1}'.format(self.namespace, self.look_at_main_control_curve),
             '{0}:{1}'.format(self.namespace, self.au_eyes_main_control_curve),
             'C_TX',
             'C_TY'),
            ('{0}:{1}'.format(self.namespace, self.look_at_left_control_curve),
             '{0}:{1}'.format(self.namespace, self.au_eyes_left_control_curve),
             'L_TX',
             'L_TY'),
            ('{0}:{1}'.format(self.namespace, self.look_at_right_control_curve),
             '{0}:{1}'.format(self.namespace, self.au_eyes_right_control_curve),
             'R_TX',
             'R_TY')
        ]

        # Get list of keys for all "au_eyes" controls
        combined_keys_to_plot = []
        if not smart_bake:
            combined_keys_to_plot = range(startframe, endframe + 1)
        else:
            for control_curve_tuple in self.control_curve_tuple_list:
                # Unpack control_curve_tuples
                source_control = control_curve_tuple[0]
                keys_to_plot = self.get_sparse_bake_index(source_control)
                # Combine control keys into a single list.
                for key in keys_to_plot:
                    if key not in combined_keys_to_plot:
                        combined_keys_to_plot.append(key)

        self.combined_keys_to_plot = combined_keys_to_plot

    def write_plot_frames_to_au_eyes(self):
        for key in self.combined_keys_to_plot:
            cmds.currentTime(key)
            for control_curve_tuple in self.control_curve_tuple_list:
                # Unpack control_curve_tuples
                target_control = control_curve_tuple[1]
                x_attribute = control_curve_tuple[2]
                y_attribute = control_curve_tuple[3]
                x_key_value = cmds.getAttr('{0}:{1}.{2}'.format(self.namespace, self.plot_to_au_values, x_attribute))
                y_key_value = cmds.getAttr('{0}:{1}.{2}'.format(self.namespace, self.plot_to_au_values, y_attribute))
                cmds.setAttr('{0}.tx'.format(target_control), x_key_value)
                cmds.setAttr('{0}.ty'.format(target_control), y_key_value)
                cmds.setKeyframe('{0}.tx'.format(target_control))
                cmds.setKeyframe('{0}.ty'.format(target_control))

    def reset_lookat(self):
        """
        Clears all animation on the lookAt control and reset's its' position to 0,0,0.
        """
        cmds.cutKey('{0}:{1}'.format(self.namespace, self.look_at_main_control_curve))
        cmds.cutKey('{0}:{1}'.format(self.namespace, self.look_at_left_control_curve))
        cmds.cutKey('{0}:{1}'.format(self.namespace, self.look_at_right_control_curve))

        # Cut existing keys on the lookAt to force the user defined distance.
        cmds.setAttr('{0}:{1}.tx'.format(self.namespace, self.look_at_main_control_curve), 0)
        cmds.setAttr('{0}:{1}.ty'.format(self.namespace, self.look_at_main_control_curve), 0)
        cmds.setAttr('{0}:{1}.tz'.format(self.namespace, self.look_at_main_control_curve), 0)

        cmds.setAttr('{0}:{1}.tx'.format(self.namespace, self.look_at_left_control_curve), 0)
        cmds.setAttr('{0}:{1}.ty'.format(self.namespace, self.look_at_left_control_curve), 0)
        cmds.setAttr('{0}:{1}.tz'.format(self.namespace, self.look_at_left_control_curve), 0)

        cmds.setAttr('{0}:{1}.tx'.format(self.namespace, self.look_at_right_control_curve), 0)
        cmds.setAttr('{0}:{1}.ty'.format(self.namespace, self.look_at_right_control_curve), 0)
        cmds.setAttr('{0}:{1}.tz'.format(self.namespace, self.look_at_right_control_curve), 0)

    def get_sparse_bake_index(self, control_curve):
        """
        Returns a list of sparse keys for plotting a single control curve.
        """
        startframe, endframe = self.get_timerange()

        tx_key_index = cmds.keyframe(control_curve, at='tx', query=True)
        ty_key_index = cmds.keyframe(control_curve, at='ty', query=True)
        tz_key_index = cmds.keyframe(control_curve, at='tz', query=True)

        compiled_key_index = []
        if tx_key_index:
            for key in ty_key_index:
                if key not in compiled_key_index:
                    compiled_key_index.append(key)
        if ty_key_index:
            for key in tx_key_index:
                if key not in compiled_key_index:
                    compiled_key_index.append(key)
        if tz_key_index:
            for key in tz_key_index:
                if key not in compiled_key_index:
                    compiled_key_index.append(key)

        sparse_bake_index = [float(startframe)] +\
                            [key for key in compiled_key_index if startframe <= key <= endframe] +\
                            [float(endframe)]
        return sparse_bake_index
