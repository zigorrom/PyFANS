import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import numpy as np

from pyqtgraph.dockarea import *

class MainView(QtGui.QMainWindow):
    def __init__(self):
        super(MainView,self).__init__()
        self.setupUi()

    def setupUi(self):
        self.statusBar()

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        restoreAction = QtGui.QAction(QtGui.QIcon('restore_wnd.png'), '&Restore windows', self)
        restoreAction.setShortcut('Ctrl+R')
        restoreAction.setStatusTip('Restore dock positions')
        
        wndMenu = menubar.addMenu('&Window')
        wndMenu.addAction(restoreAction)

        dockArea = DockArea()
        self.dockArea = dockArea
        self.setCentralWidget(dockArea)
        
        tt_d = Dock("Timetrace")
        noise_d = Dock("Noise")
        frequencies_d = Dock("Frequencies", autoOrientation=False)#, size=(10,10))
        voltages_d = Dock("Voltages", autoOrientation=False)#, size=(500,200)
        controls_d = Dock("Controls", autoOrientation=False,size=(10,10))#, closable=True)

        dockArea.addDock(tt_d, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
        dockArea.addDock(noise_d, 'bottom',tt_d)     ## place d2 at right edge of dock area
        dockArea.addDock(controls_d, 'right')## place d3 at bottom edge of d1
        dockArea.addDock(frequencies_d, 'bottom',controls_d)     ## place d4 at right edge of dock area
        dockArea.addDock(voltages_d, 'bottom',controls_d)



        w1 = pg.LayoutWidget()
        startBtn = QtGui.QPushButton('Start')
        stopBtn = QtGui.QPushButton('Stop')
        singleShotBtn = QtGui.QPushButton('Single shot')
        w1.addWidget(startBtn, row=0, col=0)
        w1.addWidget(stopBtn, row=0, col=1)
        w1.addWidget(singleShotBtn, row = 1, col=0, colspan =2)
        controls_d.addWidget(w1)

        w2 = pg.PlotWidget(title = "Timetrace")
        w2.plot(np.random.normal(size = 50000))
        tt_d.addWidget(w2)
        
        

        self.save()

        exitAction.triggered.connect(self.quit)
        restoreAction.triggered.connect(self.load)


        self.setWindowIcon(QtGui.QIcon('pyfans.png'))
        self.setWindowTitle('PyFANS')    
        self.showMaximized()
        

    def save(self):
        self.state = self.dockArea.saveState()
        
    def load(self):
        print("clicked")
        self.dockArea.restoreState(self.state)

    def quit(self):
        print("quit")
        QtGui.qApp.quit()
    
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainView()
    sys.exit(app.exec_())

##    
##
##app = QtGui.QApplication([])
##win = QtGui.QMainWindow()
##area = DockArea()
##win.setCentralWidget(area)
##win.resize(1000,500)
##win.setWindowTitle('pyqtgraph example: dockarea')
##
#### Create docks, place them into the window one at a time.
#### Note that size arguments are only a suggestion; docks will still have to
#### fill the entire dock area and obey the limits of their internal widgets.
##tt_d = Dock("Timetrace")
##noise_d = Dock("Noise")
##frequencies_d = Dock("Frequencies", autoOrientation=False)#, size=(500,400)
##voltages_d = Dock("Voltages", autoOrientation=False)#, size=(500,200)
##controls_d = Dock("Controls", autoOrientation=False)#, closable=True)
##area.addDock(tt_d, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
##area.addDock(noise_d, 'bottom',tt_d)     ## place d2 at right edge of dock area
##area.addDock(controls_d, 'right')## place d3 at bottom edge of d1
##area.addDock(frequencies_d, 'bottom',controls_d)     ## place d4 at right edge of dock area
##area.addDock(voltages_d, 'bottom',controls_d)
##
#### Test ability to move docks programatically after they have been placed
####area.moveDock(d4, 'top', d2)     ## move d4 to top edge of d2
####area.moveDock(d6, 'above', d4)   ## move d6 to stack on top of d4
####area.moveDock(d5, 'top', d2)     ## move d5 to top edge of d2
##
##
#### Add widgets into each dock
##
#### first dock gets save/restore buttons
##w1 = pg.LayoutWidget()
##label = QtGui.QLabel(""" -- DockArea Example -- 
##This window has 6 Dock widgets in it. Each dock can be dragged
##by its title bar to occupy a different space within the window 
##but note that one dock has its title bar hidden). Additionally,
##the borders between docks may be dragged to resize. Docks that are dragged on top
##of one another are stacked in a tabbed layout. Double-click a dock title
##bar to place it in its own window.
##""")
##saveBtn = QtGui.QPushButton('Save dock state')
##restoreBtn = QtGui.QPushButton('Restore dock state')
##restoreBtn.setEnabled(False)
##w1.addWidget(label, row=0, col=0)
##w1.addWidget(saveBtn, row=1, col=0)
##w1.addWidget(restoreBtn, row=2, col=0)
##controls_d.addWidget(w1)
##state = None
##def save():
##    global state
##    state = area.saveState()
##    restoreBtn.setEnabled(True)
##def load():
##    global state
##    area.restoreState(state)
##saveBtn.clicked.connect(save)
##restoreBtn.clicked.connect(load)
##
##
##
##
#### Hide title bar on dock 3
####d3.hideTitleBar()
####w3 = pg.PlotWidget(title="Plot inside dock with no title bar")
####w3.plot(np.random.normal(size=100))
####d3.addWidget(w3)
##
####w4 = pg.PlotWidget(title="Dock 4 plot")
####w4.plot(np.random.normal(size=100))
####d4.addWidget(w4)
##
##
##
##
##win.show()



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
##    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    main()
##        QtGui.QApplication.instance().exec_()
##        mw = MainView()
####        mw.show()
