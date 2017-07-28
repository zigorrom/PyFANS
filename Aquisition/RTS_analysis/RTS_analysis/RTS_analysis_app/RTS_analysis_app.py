import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, uic
from pyqtgraph.Point import Point


##generate layout
#app = QtGui.QApplication([])
#win = pg.GraphicsWindow()
#win.setWindowTitle('pyqtgraph example: crosshair')
#label = pg.LabelItem(justify='right')
#win.addItem(label)
#p1 = win.addPlot(row=1, col=0)
#p2 = win.addPlot(row=2, col=0)

#region = pg.LinearRegionItem()
#region.setZValue(10)
## Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
## item when doing auto-range calculations.
#p2.addItem(region, ignoreBounds=True)

##pg.dbg()
#p1.setAutoVisible(y=True)


##create numpy arrays
##make the numbers large to show that the xrange shows data from 10000 to all the way 0
#data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
#data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)

#p1.plot(data1, pen="r")
#p1.plot(data2, pen="g")

#p2.plot(data1, pen="w")

#def update():
#    region.setZValue(10)
#    minX, maxX = region.getRegion()
#    p1.setXRange(minX, maxX, padding=0)    

#region.sigRegionChanged.connect(update)

#def updateRegion(window, viewRange):
#    rgn = viewRange[0]
#    region.setRegion(rgn)

#p1.sigRangeChanged.connect(updateRegion)

#region.setRegion([1000, 2000])

##cross hair
#vLine = pg.InfiniteLine(angle=90, movable=False)
#hLine = pg.InfiniteLine(angle=0, movable=False)
#p1.addItem(vLine, ignoreBounds=True)
#p1.addItem(hLine, ignoreBounds=True)

#vb = p1.vb

#def mouseMoved(evt):
#    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
#    if p1.sceneBoundingRect().contains(pos):
#        mousePoint = vb.mapSceneToView(pos)
#        index = int(mousePoint.x())
#        if index > 0 and index < len(data1):
#            label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
#        vLine.setPos(mousePoint.x())
#        hLine.setPos(mousePoint.y())



#proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
##p1.scene().sigMouseMoved.connect(mouseMoved)

mainViewBase, mainViewForm = uic.loadUiType("RTS_main_view.ui")
class RTSmainView(mainViewBase,mainViewForm):
    def __init__(self, parent = None):
        super().__init__()
        self.setupUi()
        

    def setupUi(self):
        super().setupUi(self)
        self.plot1 = self.ui_plot_area.addPlot(row=1, col=0)
        self.plot2 = self.ui_plot_area.addPlot(row=2, col=0)
        self.label = pg.LabelItem(justify='right')

        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.region.sigRegionChanged.connect(self.update)
        ## Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
        ## item when doing auto-range calculations.
        self.plot2.addItem(self.region, ignoreBounds=True)
        self.plot1.setAutoVisible(y=True)
        
        self.general_curve = self.plot2.plot(pen = pg.mkColor("g"))
        self.general_curve.setVisible(True)
        self.analysis_curve = self.plot1.plot(pen = pg.mkColor("y"))
        self.analysis_curve.setVisible(True)
        print("init")

    def update(self):
        minX, maxX = self.region.getRegion()
        self.plot1.setXRange(minX, maxX, padding=0)  

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        print("opening")
        print("Select folder")
        
        folder_name = os.path.abspath(QtGui.QFileDialog.getExistingDirectory(self,caption="Select Folder"))#, directory = self._settings.working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(folder_name)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        if retval and self._settings:
           pass

    def load_data(self):
        pass



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #    QtGui.QApplication.instance().exec_()

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("RTS analysis")

    wnd = RTSmainView()
    wnd.show()

    sys.exit(app.exec_())
