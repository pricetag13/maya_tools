from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from maya import OpenMayaUI

from plotting_widget import PlottingWidget
from setup_lookat_widget import SetUpLookAtWidget


def maya_main_window():
    main_window_pointer = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_pointer), QtWidgets.QWidget)


def delete_maya_tool(object_name):
    top_level_windows = QtWidgets.QApplication.topLevelWindows()
    for window in top_level_windows:
        if object_name in window.objectName():
            window.setParent(None)
            window.deleteLater()


class AdvancedLookAtMain(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(AdvancedLookAtMain, self).__init__(parent)
        self.setObjectName("lookat_main")
        self.setWindowTitle("Advanced Lookat")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setFixedSize(600, 275)

        main_layout = QtWidgets.QVBoxLayout()
        tab_bar = QtWidgets.QTabWidget()

        # Plotting Tab
        self.plotting_widget = PlottingWidget()
        tab_bar.addTab(self.plotting_widget, "Plotting Utilities")

        # Set-Up Tab
        self.set_up_widget = SetUpLookAtWidget()
        tab_bar.addTab(self.set_up_widget, "Set Up")

        main_layout.addWidget(tab_bar)

        self.setLayout(main_layout)
