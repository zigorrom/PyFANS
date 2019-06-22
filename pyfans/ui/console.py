from PyQt4 import uic, QtCore, QtGui
from pyfans.ui.forms.UI_Console import Ui_Console

# consoleViewBase, consoleViewForm = uic.loadUiType("UI/UI_Console.ui")
# class UI_Console(consoleViewBase, consoleViewForm):
class UI_Console(QtGui.QWidget, Ui_Console):
    def __init__(self, parent = None):
        # super(consoleViewBase,self).__init__(parent)
        super().__init__(parent)
        self.setupUi()
        #self.


    def setupUi(self):
        super().setupUi(self)

    @QtCore.pyqtSlot(str)
    def append_text(self, text):
        self.console_widget.appendPlainText(text)

    def clear(self):
        pass
