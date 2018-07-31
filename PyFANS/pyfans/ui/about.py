from PyQt4 import uic

aboutViewBase, aboutViewForm = uic.loadUiType("UI/UI_About.ui")
class UI_About(aboutViewBase, aboutViewForm):
    def __init__(self,parent = None):
        super(aboutViewBase, self).__init__(parent)
        self.setupUi(self)