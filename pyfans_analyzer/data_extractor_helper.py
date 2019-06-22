import os
import sys

from PyQt4 import QtCore, QtGui, uic

def select_files():
    file_list = list()
    
    fname = QtGui.QFileDialog.getOpenFileName()
    pass

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ExperimentDataAnalysis")
    app.setStyle("cleanlooks")
    
    return 0
    # wnd.show()
    # return app.exec_()


if __name__ == "__main__":
    main()