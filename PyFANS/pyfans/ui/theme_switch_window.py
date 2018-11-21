import qdarkstyle
from PyQt4 import uic, QtCore, QtGui
from pyfans.ui.forms.UI_ThemeSwitch import Ui_ThemeSwitch
# ThemeSwitchViewBase, ThemeSwitchViewForm = uic.loadUiType("UI/UI_ThemeSwitch.ui")
# class UI_ThemeSwitchWindow(ThemeSwitchViewBase, ThemeSwitchViewForm):
class UI_ThemeSwitchWindow(QtGui.QDialog, Ui_ThemeSwitch):
    def __init__(self, parent = None):
        # super(ThemeSwitchViewBase,self).__init__(parent)
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.ui_light_button.toggled.connect(self.switch_to_light)
        self.ui_dark_button.toggled.connect(self.switch_to_dark)

    @QtCore.pyqtSlot(bool)
    def switch_to_light(self, checked):
        if checked:
            app = QtGui.QApplication.instance()
            app.setStyleSheet("")

    @QtCore.pyqtSlot(bool)
    def switch_to_dark(self, checked):
        if checked:
            app = QtGui.QApplication.instance()
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
            # with open("stylesheet.qss") as f:
            #     styleSheet = f.read()
            #     app.setStyleSheet(styleSheet)





