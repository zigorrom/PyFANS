from PyQt4 import QtGui, uic
from pyfans.ui.forms.UI_About import Ui_About

# aboutViewBase, aboutViewForm = uic.loadUiType("UI/UI_About.ui")
# class UI_About(aboutViewBase, aboutViewForm):
class UI_About(QtGui.QWidget, Ui_About):
    def __init__(self,parent = None):
        # super(aboutViewBase, self).__init__(parent)
        super().__init__(parent)
        self.setupUi(self)