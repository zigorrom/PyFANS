from mainform import *

class MainWindow(Ui_MainWindow):
    def __init__(self,mw):
        super(MainWindow,self).__init__()
        self.ui = mw
        self.state = self.saveState(self.ui)
        
        
    def helpClicked(self):
        print("restore")
        self.ui.restoreState(self.state)
        print("restored")
        
    def saveState(self, mw):
        a = self.ui.saveState()
        return a
    

    def setupUi(self):
        super(MainWindow,self).setupUi(self.ui)
        print("setup")
        self.actionRestoreState.triggered.connect(self.helpClicked)

        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    mw = QtGui.QMainWindow()
    ui = MainWindow(mw)
    ui.setupUi()
    mw.show()
    sys.exit(app.exec_())
