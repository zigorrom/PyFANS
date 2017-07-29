import os
import numpy as np
import pandas as pd
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
        self.loaded_data = None
        #self.timetrace_filename = ""
        settings = QtCore.QSettings("foo","foo")
        self.timetrace_filename = settings.value('filename', type=str)#.toString()
        if self.timetrace_filename:
            self.load_data(self.timetrace_filename)

    def setupUi(self):
        super().setupUi(self)
        self.plot1 = self.ui_plot_area.addPlot(row=1, col=0)
        self.plot2 = self.ui_plot_area.addPlot(row=2, col=0, colspan =2)
        self.histogram_plot = self.ui_plot_area.addPlot(row = 1, col = 1)
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
        self.histogram_curve = self.histogram_plot.plot(pen = pg.mkColor("b"))
        self.histogram_curve.setVisible(True)

        print("init")

    def closeEvent(self,event):
        print("closing")
        settings = QtCore.QSettings("foo","foo")
        if self.timetrace_filename:
            settings.setValue("filename", self.timetrace_filename)


    def update(self):
        minX, maxX = self.region.getRegion()
        
        self.plot1.setXRange(minX, maxX, padding=0)
        
        region_data = self.loaded_data.loc[lambda df: (df.time > minX) & (df.time < maxX),:]

        data = region_data.data
        #print(data)
        #print(data)
        hist, bin_edges = np.histogram(data, bins = 'fd')
        bin_centers = 0.5*(bin_edges[1:]+bin_edges[:-1])  #0.5*(x[1:] + x[:-1])
        self.histogram_curve.setData(bin_centers, hist)

        #print(hist)
        #print(bin_edges)
        #print(self.region.boundingRect())

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        print("opening")
        print("Select folder")
        
        self.timetrace_filename = os.path.abspath(QtGui.QFileDialog.getOpenFileName(self,caption="Select File"))#, directory = self._settings.working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(timetrace_filename)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        if retval:
           self.load_data(timetrace_filename)

    def load_data(self, filename):
        print("loading file: {0}".format(filename))
        self.loaded_data = pd.read_csv(filename, delimiter = "\t", names=["time", "data"])
        time = self.loaded_data.time #["time"]
        data = self.loaded_data.data #["data"]
        #time,data = np.loadtxt(filename).T
        self.general_curve.setData(time,data)
        self.analysis_curve.setData(time,data)
        self.update()

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
