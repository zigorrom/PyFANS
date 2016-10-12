import sys, signal, time

from PyQt4 import QtCore, QtGui

from mainform import Ui_mainWindow


class daqMainWindow(QtGui.QMainWindow, Ui_mainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.show()
        

def main():
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("FZJ")
    app.setOrganizationDomain("fz-juelich.de")
    app.setApplicationName("FANS")
    window = daqMainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
