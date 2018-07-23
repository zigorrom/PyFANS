import sys
from PyQt4 import QtCore, QtGui, uic

mainViewBase, mainViewForm = uic.loadUiType("UI/UI_ExperimentDataAnalysis.ui")
class ExperimentDataAnalysis(mainViewBase,mainViewForm):
    def __init__(self, parent = None ):
        super(mainViewBase,self).__init__(parent)
        self.setupUi()
    
    def setupUi(self):
        super().setupUi(self)

    

if __name__== "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ExperimentDataAnalysis")
    app.setStyle("cleanlooks")
    wnd = ExperimentDataAnalysis()
    wnd.show()

    sys.exit(app.exec_())