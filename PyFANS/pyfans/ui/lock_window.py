from PyQt4 import uic, QtGui
from pyfans.ui.forms.UI_LockScreen import Ui_LockScreen

# LockViewBase, LockViewForm = uic.loadUiType("UI/UI_LockScreen.ui")
# class UI_LockWindow(LockViewBase, LockViewForm):
class UI_LockWindow(QtGui.QDialog, Ui_LockScreen):
    def __init__(self, parent = None):
        # super(LockViewBase,self).__init__(parent)
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.ui_unlock_button.clicked.connect(self.accept)
