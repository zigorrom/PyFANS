import collections, math

from PyQt4 import QtCore
import pyqtgraph as pg

# Basic PyQtGraph settings
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', None) #'w')
pg.setConfigOption('foreground','k')


class SpectrumPlotWidget:
    """Main spectrum plot"""
    def __init__(self, layout, spectrum_ranges):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        
        assert isinstance(spectrum_ranges, dict), "Spectrum ranges must be a dictionary of parameters"
        self.spectrum_ranges = spectrum_ranges
        
        self.main_curve_color = pg.mkColor("b")
        self.resulting_curve_color = pg.mkColor("r")
        self.curves = {}

        self.create_plot()
        self.create_curves()

        self.roi = None
        self.create_roi()
        

    def create_curves(self):
        colors = [pg.mkColor("b"), pg.mkColor("g")]
        counter = 0
        l = len(colors)
        for rang, vals in self.spectrum_ranges.items():
            #curve = self.plot.plot(pen=self.main_curve_color)
            color = colors[counter%l]
            curve = self.plot.plot(pen=color)
            curve.setZValue(900)
            curve.setVisible(True)
            self.curves[rang] = curve
            counter += 1

        curve = self.plot.plot(pen = self.resulting_curve_color)
        curve.setZValue(1000)
        curve.setVisible(True)
        self.curves[-1] = curve


    def clear_curves(self):
        for rang, curve in self.curves.items():
            curve.clear()

    def create_roi(self):
        self.roi = pg.LineROI([0.2, -17], [4, -17],width = 0, pen=pg.mkPen('b'))
        self.plot.addItem(self.roi)

    def create_plot(self):
        """Create main spectrum plot"""
        self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
        self.plot = self.layout.addPlot(row=1, col=0)
        self.plot.showGrid(x=True, y=True)
        self.plot.setLogMode(x=True, y=True)
        self.plot.setLabel("left", "Power", units="V^2Hz-1")
        self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLimits(xMin=0.1,xMax = 7, yMin = -18, yMax = 2)
        self.plot.setXRange(0.1,5)
        self.plot.setYRange(-20,-1)

        
        self.plot.showButtons()

        # Create crosshair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.vLine.setZValue(1000)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.vLine.setZValue(1000)
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)
        self.mouseProxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
                                         rateLimit=60, slot=self.mouse_moved)

   
    def updata_resulting_spectrum(self, freq,data, force = False):
        curve = self.curves[-1]
        curve.setData(freq,data)

    def update_spectrum(self, rang, data, force = False):
        curve = self.curves[rang]
        curve.setData(data['f'],data['d'])
        
        #if self.curves[range] or force:
            
        
   
    #def update_plot(self, data_storage, force=False):
    #    """Update main spectrum curve"""
    #    if data_storage.frequency_bins is None:
    #        return

    #    if self.main_curve or force:
    #        self.curve.setData(data_storage.frequency_bins, data_storage.psd_data[self.__visualize_index])
    #        if force:
    #            print("forced plot")
    #            self.curve.setVisible(self.main_curve)

    

    #    self.clear_persistence()
    #    self.persistence_data = collections.deque(maxlen=self.persistence_length)
    #    for i in range(min(self.persistence_length, data_storage.history.history_size - 1)):
    #        data = data_storage.history[-i - 2]
    #        if data_storage.smooth:
    #            data = data_storage.smooth_data(data)
    #        self.persistence_data.append(data)
    #    QtCore.QTimer.singleShot(0, lambda: self.update_persistence(data_storage, force=True))

    def mouse_moved(self, evt):
        """Update crosshair when mouse is moved"""
        pos = evt[0]
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            self.posLabel.setText(
                "<span style='font-size: 12pt'>f={} Hz, P={:.5E} V^2/Hz</span>".format( #:0.3f
                    int(10**mousePoint.x()) ,
                    10**mousePoint.y()
                )
            )
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    