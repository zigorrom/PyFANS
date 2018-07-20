import collections, math
import numpy as np
from PyQt4 import QtCore
import pyqtgraph as pg
from PyQt4 import uic, QtGui, QtCore

# Basic PyQtGraph settings
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', None) #'w')
pg.setConfigOption('foreground','k')

class MovableHandle(QtGui.QGraphicsRectItem):
    def __init__(self, *args, pixmap=None):
        QtGui.QGraphicsRectItem.__init__(self, *args)
        self.setAcceptHoverEvents(True)
        self._pixmap = QtGui.QPixmap()
        self._pixmap.load("UI/flicker.png")
        # self._pixmap = None#pixmap.scaledToWidth(radius)
        radius = 5
        self._pixmap_offset = 2
        self._pixmap_width = 2*(radius - self._pixmap_offset)
        if pixmap:
            self._pixmap = pixmap.scaledToWidth(self._pixmap_width) #2*radius)

    def hoverEnterEvent(self, ev):
        self.savedPen = self.pen()
        self.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        ev.ignore()

    def hoverLeaveEvent(self, ev):
        self.setPen(self.savedPen)
        ev.ignore()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            self.pressDelta = self.mapToParent(ev.pos()) - self.pos()
        else:
            ev.ignore()     

    def mouseMoveEvent(self, ev):
        self.setPos(self.mapToParent(ev.pos()) - self.pressDelta)
       
    # def paint(self, p, opt, widget):
    #     super().paint(p,opt,widget)
    #     if not isinstance(self._pixmap, QtGui.QPixmap):
    #         return
    #     p.setRenderHints(p.Antialiasing, True)
    #     half_pixmap_width = self._pixmap_width / 2  # self.radius/2 
    #     p.drawPixmap(-half_pixmap_width,-half_pixmap_width, self._pixmap )#position.toPoint(), self._pixmap) #position.x(), position.y(), self._pixmap)
        


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
        self.thermal_curve_color = pg.mkColor("m")
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
        thermal_noise_curve = self.plot.plot(pen = self.thermal_curve_color)
        thermal_noise_curve.setZValue(800)
        thermal_noise_curve.setVisible(True)
        self.curves[-2] = thermal_noise_curve


    def clear_curves(self):
        for rang, curve in self.curves.items():
            curve.clear()

    def create_roi(self):
        self.roi = pg.LineROI([0.2, -17], [4, -17],width = 0, pen=pg.mkPen('b'))
        self.plot.addItem(self.roi)
        # self.movable_handle = MovableHandle(QtCore.QRectF(0, 0, 0.01, 0.01))
        # # self.movable_handle.setPen(QtGui.QPen(QtGui.QColor(100, 200, 100)))
        # self.plot.addItem(self.movable_handle)

    def create_plot(self):
        """Create main spectrum plot"""
        self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
        self.plot = self.layout.addPlot(row=1, col=0)
        self.plot.showGrid(x=True, y=True)
        self.plot.setLogMode(x=True, y=True)
        right_axis = self.plot.getAxis("right")
        right_axis.setStyle(showValues = False)
        top_axis = self.plot.getAxis("top")
        top_axis.setStyle(showValues = False)

        left_axis = self.plot.getAxis("left")
        bottom_axis = self.plot.getAxis("bottom")
        font = QtGui.QFont()
        font.setPixelSize(20)
        left_axis.tickFont = font
        left_axis.setStyle(tickTextOffset = 10)
        left_axis.setWidth(120)
        bottom_axis.tickFont = font
        bottom_axis.setStyle(tickTextOffset = 10)

        self.plot.showAxis("right", show=True)
        self.plot.showAxis("top", show=True)
        # self.plot.setLabel("left", "Power", units="V^2Hz-1")
        self.plot.setLabel("left", "<font size=\"15\">Power Spectral Density, S<sub>V</sub> (V<sup>2</sup>Hz<sup>-1</sup>)</font>")#, units="<font size=\"15\">V^2Hz-1</font>")
        # self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLabel("bottom", "<font size=\"15\">Frequency, f (Hz)</font>")#, units="Hz")
        self.plot.setLimits(xMin=0.01,xMax = 7, yMin = -50, yMax = 10)
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

    def update_thermal_noise(self, freq, data, force = False):
        curve = self.curves[-2]
        curve.setData(freq, data)

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

class HistoryBuffer:
    """Fixed-size NumPy array ring buffer"""
    def __init__(self, data_size, max_history_size, dtype=float):
        self.data_size = data_size
        self.max_history_size = max_history_size
        self.history_size = 0
        self.counter = 0
        self.buffer = np.empty(shape=(max_history_size, data_size), dtype=dtype)

    def append(self, data):
        """Append new data to ring buffer"""
        self.counter += 1
        if self.history_size < self.max_history_size:
            self.history_size += 1
        self.buffer = np.roll(self.buffer, -1, axis=0)
        self.buffer[-1] = data[:self.data_size]

    def get_buffer(self):
        """Return buffer stripped to size of actual data"""
        if self.history_size < self.max_history_size:
            return self.buffer[-self.history_size:]
        else:
            return self.buffer

    def __getitem__(self, key):
        return self.buffer[key]
    
class WaterfallPlotWidget:
    """Waterfall plot"""
    def __init__(self, layout, histogram_layout=None):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        if histogram_layout and not isinstance(histogram_layout, pg.GraphicsLayoutWidget):
            raise ValueError("histogram_layout must be instance of pyqtgraph.GraphicsLayoutWidget")
        self.spectral_ranges = {0:(0,1600,1),1:(0,102400,64)}
        self.display_range = 0
        self.layout = layout
        self.histogram_layout = histogram_layout
        
        start, stop, step = self.spectral_ranges[self.display_range]
        self.data_size = int(stop/step)
        self.history_size = 100
        self.history = HistoryBuffer(self.data_size, self.history_size)
        
        self.counter = 0

        self.create_plot()

    def create_plot(self):
        """Create waterfall plot"""
        self.plot = self.layout.addPlot()
        self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLabel("left", "Time")

        self.plot.setYRange(-self.history_size, 0)
        self.plot.setLimits(xMin=0, yMax=0)
        self.plot.showButtons()
        #self.plot.setAspectLocked(True)
        #self.plot.setDownsampling(mode="peak")
        #self.plot.setClipToView(True)

        # Setup histogram widget (for controlling waterfall plot levels and gradients)
        if self.histogram_layout:
            self.histogram = pg.HistogramLUTItem()
            self.histogram_layout.addItem(self.histogram)
            self.histogram.gradient.loadPreset("flame")
            #self.histogram.setHistogramRange(-50, 0)
            #self.histogram.setLevels(-50, 0)

    #def update_spectrum(self, rang, data, force = False):
    #    curve = self.curves[rang]
    #    curve.setData(data['f'],data['d'])

    def update_plot(self, rang, data):
        """Update waterfall plot"""
        if rang != self.display_range:
            return

        self.counter += 1
        spectral_data = data['d']
        frequencies = data['f']

        self.history.append(spectral_data)

        # Create waterfall image on first run
        if self.counter == 1:
            self.waterfallImg = pg.ImageItem()
            self.waterfallImg.scale((frequencies[-1] - frequencies[0]) / len(frequencies), 1)
            self.plot.clear()
            self.plot.addItem(self.waterfallImg)

        # Roll down one and replace leading edge with new data
        self.waterfallImg.setImage(self.history.buffer[-self.counter:].T,
                                   autoLevels=False, autoRange=False)

        # Move waterfall image to always start at 0
        self.waterfallImg.setPos(
            frequencies[0],
            -self.counter if self.counter < self.history_size else -self.history_size
        )

        # Link histogram widget to waterfall image on first run
        # (must be done after first data is received or else levels would be wrong)
        if self.counter == 1 and self.histogram_layout:
            self.histogram.setImageItem(self.waterfallImg)

    def clear_plot(self):
        """Clear waterfall plot"""
        self.counter = 0


waterfallViewBase, waterfallViewForm = uic.loadUiType("UI/UI_WaterfallNoise.ui")
class WaterfallNoiseWindow(waterfallViewBase, waterfallViewForm):
    def __init__(self, parent = None):
        super(waterfallViewBase, self).__init__(parent)
        self.setupUi(self)
        self.waterfall_widget = WaterfallPlotWidget(self.ui_waterfall_plot, self.ui_histogram_layout)

    def update_data(self, rang, data):
        self.waterfall_widget.update_plot(rang, data)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    wnd = WaterfallNoiseWindow()
    wnd.show()
    sys.exit(app.exec_())