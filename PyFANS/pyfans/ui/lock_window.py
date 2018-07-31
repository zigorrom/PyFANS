from PyQt4 import uic

LockViewBase, LockViewForm = uic.loadUiType("UI/UI_LockScreen.ui")
class UI_LockWindow(LockViewBase, LockViewForm):
    def __init__(self, parent = None):
        super(LockViewBase,self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)
        self.ui_unlock_button.clicked.connect(self.accept)
