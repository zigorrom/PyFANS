﻿import collections, math
from math import cos, sin
import numpy as np
from PyQt4 import QtCore
import pyqtgraph as pg
from pyqtgraph import functions as fn
from PyQt4 import uic, QtGui, QtCore
from pyqtgraph import UIGraphicsItem, GraphicsObject
import pyfans_analyzer.spectrum_processing as sp
import pyfans.physics.physical_calculations as phys
from pyfans.forms.UI_WaterfallNoise import Ui_WaterfallNoise
# Basic PyQtGraph settings
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', None) #'w')
pg.setConfigOption('foreground','k')

class Handle(UIGraphicsItem):
    """
    Handle represents a single user-interactable point attached to an ROI. They
    are usually created by a call to one of the ROI.add___Handle() methods.
    
    Handles are represented as a square, diamond, or circle, and are drawn with 
    fixed pixel size regardless of the scaling of the view they are displayed in.
    
    Handles may be dragged to change the position, size, orientation, or other
    properties of the ROI they are attached to.
    
    
    """
    types = {   ## defines number of sides, start angle for each handle type
        't': (4, np.pi/4),
        'f': (4, np.pi/4), 
        's': (4, 0),
        'r': (12, 0),
        'sr': (12, 0),
        'rf': (12, 0),
    }

    sigClicked = QtCore.Signal(object, object)   # self, event
    sigRemoveRequested = QtCore.Signal(object)   # self
    sigPositionChanged = QtCore.Signal(object, object)
    
    def __init__(self, name, radius, typ=None, pen=(200, 200, 220), parent=None, deletable=False, handle_offset = None):
        #print "   create item with parent", parent
        #self.bounds = QtCore.QRectF(-1e-10, -1e-10, 2e-10, 2e-10)
        #self.setFlags(self.ItemIgnoresTransformations | self.ItemSendsScenePositionChanges)
        UIGraphicsItem.__init__(self, parent=parent)
        self._name = name
        self.radius = radius
        self.typ = typ
        self.pen = pg.mkPen(pen)
        self.currentPen = self.pen
        self.pen.setWidth(0)
        self.pen.setCosmetic(True)
        self.isMoving = False
        self.sides, self.startAng = self.types[typ]
        self.buildPath()
        self._shape = None
        self.menu = self.buildMenu()
        self._handle_offset = QtCore.QPointF(0, 20)
        if handle_offset:
            self.handle_offset = handle_offset

        # UIGraphicsItem.__init__(self, parent=parent)
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.deletable = deletable
        if deletable:
            self.setAcceptedMouseButtons(QtCore.Qt.RightButton)        
        
        self.setZValue(11)

        # pixmap = QtGui.QPixmap()
        # pixmap.load("UI/flicker.png")
        # self.pixmap = pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)

    # def setPos(self, *args):
    #     super().setPos(*args)
    #     pos = QtCore.QPointF(*args)
    #     # parent = self.parentItem()
    #     # pos = parent.mapToView(pos)
    #     self.sigPositionChanged.emit(pos)
    def calculateCurve(self, frequency):
        raise NotImplementedError()

    @property
    def handle_offset(self):
        return self._handle_offset

    @handle_offset.setter
    def handle_offset(self, value):
        self._handle_offset = value
    

    @property
    def currentPosition(self):
        parent = self.parentItem()
        p = self.pos() 

        p = parent.mapToScene(p)
        p = p - self.handle_offset
        p = parent.mapFromScene(p)

        p = parent.mapToView(p)
        return p

    
    def setCurrentPosition(self, *args):
        position = None
        if len(args) == 1:
            if isinstance(args[0], QtCore.QPointF):
                position = args[0]
            else:
                raise TypeError()

        elif len(args) == 2:
            x = args[0]
            y = args[1]
            position = QtCore.QPointF(x,y)
        
        else:
            raise TypeError()

        if position is None:
            return

        parent = self.parentItem()
        position = parent.mapFromView(position)
        position = parent.mapToScene(position)
        position = position+self.handle_offset
        position = parent.mapFromScene(position)
        self.setPos(position)
        self.sigPositionChanged.emit(self, self.currentPosition)

   


    @property
    def name(self):
        return self._name
    
    @property
    def handlePen(self):
        return self.pen
            
    def setDeletable(self, b):
        self.deletable = b
        if b:
            self.setAcceptedMouseButtons(self.acceptedMouseButtons() | QtCore.Qt.RightButton)
        else:
            self.setAcceptedMouseButtons(self.acceptedMouseButtons() & ~QtCore.Qt.RightButton)
            
    def removeClicked(self):
        self.sigRemoveRequested.emit(self)

    def hoverEvent(self, ev):
        hover = False
        if not ev.isExit():
            if ev.acceptDrags(QtCore.Qt.LeftButton):
                hover=True
            for btn in [QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MidButton]:
                if int(self.acceptedMouseButtons() & btn) > 0 and ev.acceptClicks(btn):
                    hover=True
                    
        if hover:
            self.currentPen = fn.mkPen(255, 255,0)
        else:
            self.currentPen = self.pen
        self.update()
        

    def mouseClickEvent(self, ev):
        ## right-click cancels drag
        if ev.button() == QtCore.Qt.RightButton and self.isMoving:
            self.isMoving = False  ## prevents any further motion
            ev.accept()
        elif int(ev.button() & self.acceptedMouseButtons()) > 0:
            ev.accept()
            if ev.button() == QtCore.Qt.RightButton and self.deletable:
                self.raiseContextMenu(ev)
            self.sigClicked.emit(self, ev)
        else:
            ev.ignore()        
            
                           
    def buildMenu(self):
        menu = QtGui.QMenu()
        menu.setTitle("Handle")
        self.removeAction = menu.addAction("Remove handle", self.removeClicked) 

        # alpha = QtGui.QWidgetAction(menu)
        # alphaSlider = QtGui.QSlider()
        # alphaSlider.setOrientation(QtCore.Qt.Horizontal)
        # alphaSlider.setMaximum(255)
        # alphaSlider.setValue(255)
        # # alphaSlider.valueChanged.connect(self.setAlpha)
        # alpha.setDefaultWidget(alphaSlider)
        # menu.addAction(alpha)

        return menu
        
    def getMenu(self):
        return self.menu

    def raiseContextMenu(self, ev):
        menu = self.scene().addParentContextMenus(self, self.getMenu(), ev)
        
        ## Make sure it is still ok to remove this handle
        # self.removeAction.setEnabled(removeAllowed)
        pos = ev.screenPos()
        menu.popup(QtCore.QPoint(pos.x(), pos.y()))    

    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            return
        ev.accept()
        
        if ev.isFinish():
            self.isMoving = False
        elif ev.isStart():
            self.isMoving = True
            self.startPos = self.scenePos()
            self.cursorOffset = self.scenePos() - ev.buttonDownScenePos()
            
        if self.isMoving:  ## note: isMoving may become False in mid-drag due to right-click.
            pos = ev.scenePos() + self.cursorOffset 
            pos_to_report = pos - self.handle_offset
            parent = self.parentItem()
            
            pos = parent.mapFromScene(pos)
            pos_to_report = parent.mapFromScene(pos_to_report)
            pos_to_report = parent.mapToView(pos_to_report)

            self.setPos(pos)
            #correct by the offset 
            # pos = pos - self.handle_offsetpos_pos_to_report
            # pos = parent.mapToView(pos)
            
            self.sigPositionChanged.emit(self, pos_to_report)
            # print(pos)

   

    def buildPath(self):
        size = self.radius
        self.path = QtGui.QPainterPath()
        ang = self.startAng
        dt = 2*np.pi / self.sides
        for i in range(0, self.sides+1):
            x = size * cos(ang)
            y = size * sin(ang)
            ang += dt
            if i == 0:
                self.path.moveTo(x, y)
            else:
                self.path.lineTo(x, y)            
            
        # self.path.addText(-40,40,QtGui.QFont("Helvetica", 24), "TEST")

    

    def paint(self, p, opt, widget):
        p.setRenderHints(p.Antialiasing, True)
        p.setPen(self.currentPen)
        p.drawPath(self.shape())
        p.fillPath(self.shape(), self.currentPen.brush())
        pos = self.pos()
        # print(pos)
        # p.drawLine(1,-2,2,-4)
        # p.setFont(QtGui.QFont("Helvetica", 24))
        # p.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        # p.drawText(0,0,"flicker")
    
        # if not isinstance(self.pixmap, QtGui.QPixmap):
        #     return
        # half_pixmap_width = self.radius/2 
        # p.drawPixmap(-half_pixmap_width,-half_pixmap_width, self.pixmap )#position.toPoint(), self._pixmap) #position.x(), position.y(), self._pixmap)
        
            
    def shape(self):
        if self._shape is None:
            s = self.generateShape()
            if s is None:
                return self.path
            self._shape = s
            self.prepareGeometryChange()  ## beware--this can cause the view to adjust, which would immediately invalidate the shape.
        return self._shape
    
    def boundingRect(self):
        #print 'roi:', self.roi
        s1 = self.shape()
        #print "   s1:", s1
        #s2 = self.shape()
        #print "   s2:", s2
        
        return self.shape().boundingRect()
            
    def generateShape(self):
        ## determine rotation of transform
        #m = self.sceneTransform()  ## Qt bug: do not access sceneTransform() until we know this object has a scene.
        #mi = m.inverted()[0]
        dt = self.deviceTransform()
        
        if dt is None:
            self._shape = self.path
            return None
        
        v = dt.map(QtCore.QPointF(1, 0)) - dt.map(QtCore.QPointF(0, 0))
        va = np.arctan2(v.y(), v.x())
        
        dti = fn.invertQTransform(dt)
        devPos = dt.map(QtCore.QPointF(0,0))
        tr = QtGui.QTransform()
        tr.translate(devPos.x(), devPos.y())
        tr.rotate(va * 180. / 3.1415926)
        
        return dti.map(tr.map(self.path))
        
        
    def viewTransformChanged(self):
        GraphicsObject.viewTransformChanged(self)
        self._shape = None  ## invalidate shape, recompute later if requested.
        self.update()
  
class FlickerHandle(Handle):
    sigAlphaChanged = QtCore.Signal(float) 
    def __init__(self, name, **kwargs):
        kwargs.setdefault("handle_offset", QtCore.QPointF(-20, 20))
        kwargs.setdefault("typ", "t")
        kwargs.setdefault("deletable", True)
        kwargs.setdefault("radius", 10)
        super().__init__(name, **kwargs)
        self._alpha = 1

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    def buildMenu(self):
        menu = super().buildMenu()
        alpha = QtGui.QWidgetAction(menu)
        dummy = QtGui.QWidget()
        label = QtGui.QLabel("Alpha")

        spinBox = QtGui.QDoubleSpinBox()
        spinBox.setRange(0.01, 100)
        spinBox.setSingleStep(0.1)
        spinBox.setValue(1.0)
        spinBox.valueChanged.connect(self.on_alpha_changed)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(spinBox)

        dummy.setLayout(layout)
        alpha.setDefaultWidget(dummy)
        menu.addAction(alpha)
        return menu

    @QtCore.pyqtSlot(float)
    def on_alpha_changed(self, value):
        print(value)
        self.alpha = value
        self.sigAlphaChanged.emit(value)

   

    def calculateCurve(self, frequency):
        p = self.currentPosition
        Amplitude = np.power(10,p.y())
        CurrentFreq = np.power(10,p.x())
        
        data = Amplitude * np.power(CurrentFreq/frequency, self.alpha)
        return data
        # pos_to_report = parent.mapToView(pos_to_report)
    
class GRHandle(Handle):
    sigAlphaChanged = QtCore.Signal(float) 
    def __init__(self, name, **kwargs):
        kwargs.setdefault("handle_offset", QtCore.QPointF(-40, 40))
        kwargs.setdefault("typ", "r")
        kwargs.setdefault("deletable", True)
        kwargs.setdefault("radius", 10)
        super().__init__(name, **kwargs)
        self._alpha = 1

    def calculateCurve(self, frequency):
        p = self.currentPosition
        Amplitude = np.power(10,p.y())
        CurrentFreq = np.power(10,p.x())
        df = frequency/CurrentFreq
        sqr_f = df*df
        # return Amplitude/(1+sqr_f)
        data = Amplitude/(1+sqr_f) 
        return data

class SpectrumPlotWidget:
    """Main spectrum plot"""
    def __init__(self, layout, spectrum_ranges, create_helper_handles=False, update_history=False):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        
        assert isinstance(spectrum_ranges, dict), "Spectrum ranges must be a dictionary of parameters"
        self.spectrum_ranges = spectrum_ranges
        
        self.main_curve_color = pg.mkColor("b")
        self.resulting_curve_color = pg.mkColor("r")
        self.thermal_curve_color = pg.mkColor("m")
        self.curves = {}

        # self._historySize = 10
        self.handles = {}

        #self.data_size = 10000
        self.historySize = 10
        self.history_buffer = None#
        self.history_curves = list()

        self.create_plot()
        self.create_curves()
        
        self.update_history = update_history
        # self.roi = None
        if create_helper_handles:
            self.create_helper_handle()
        
    @property
    def historySize(self):
        return self._historySize

    @historySize.setter
    def historySize(self, value):
        self._historySize = value


    def setHelperCurvesVisible(self, visibility):
        self.curves["flicker"].setVisible(visibility)
        self.curves["gr"].setVisible(visibility)
        self.flickerHandle.setVisible(visibility)
        self.grHandle.setVisible(visibility)

    def setHistoryCurvesVisible(self, visibility):
        for curve in self.history_curves:
            curve.setVisible(visibility)

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

        for idx in range(self.historySize):
            color = pg.intColor(idx, width = 1)#pg.mkColor("g")#pg.intColor(idx, width = 2)
            c = self.plot.plot(pen=color)
            c.setZValue(1000-idx-1)
            c.setVisible(True)
            self.history_curves.append(c)
            # freq = np.logspace(0,5, 51)
            # print(freq)
            # data = np.repeat(1e-5/(idx+1), 51)
            # print(data)
            # c.setData(freq,data)


        curve = self.plot.plot(pen = self.resulting_curve_color)
        curve.setZValue(1000)
        curve.setVisible(True)
        self.curves[-1] = curve

        thermal_noise_curve = self.plot.plot(pen = self.thermal_curve_color)
        thermal_noise_curve.setZValue(800)
        thermal_noise_curve.setVisible(True)
        self.curves[-2] = thermal_noise_curve

        # flickerCurve = self.plot.plot(pen = pg.mkColor("r"))
        # flickerCurve.setZValue(700)
        # flickerCurve.setVisible(True)
        # self.curves["flicker"] =  flickerCurve

        # grCurve = self.plot.plot(pen = pg.mkColor("b"))
        # grCurve.setZValue(700)
        # grCurve.setVisible(True)
        # self.curves["gr"] =  grCurve
    
    def create_curve(self, name, pen="r",zValue= 1000, **kwargs):
        curve = self.plot.plot(pen=pen, **kwargs)
        curve.setZValue(zValue)
        visible = kwargs.get("visible", True)
        curve.setVisible(visible)
        self.curves[name] = curve
        return curve

    def remove_curve(self,name):
        curve = self.curves.pop(name,None)
        if curve is not None:
            self.plot.removeItem(curve)

    def clear_curves(self):
        for rang, curve in self.curves.items():
            curve.clear()

    def get_curve_by_name(self, name):
        return self.curves.get(name, None)

    def remove_handle(self, name):
        handle_to_remove = self.handles.pop(name, None)
        if handle_to_remove is not None:
            self.plot.removeItem(handle_to_remove)
        
            curve_to_remove = self.curves.pop(name,None)
            if curve_to_remove is not None:
                self.plot.removeItem(curve_to_remove)


    def remove_all_handles(self):
        for k, handle in self.handles.items():
            self.plot.removeItem(handle)
            curve_to_remove = self.curves.get(k,None)
            if curve_to_remove is not None:
                self.plot.removeItem(curve_to_remove)

    def get_handle_by_name(self, name):
        return self.handles.get(name,None)

    def create_curve_for_handle(self, handle):
        curve = self.curves.get(handle.name, None)
        if curve is None:
            curve = self.plot.plot(pen = handle.handlePen) #pg.mkColor("b"))
            curve.setZValue(700)
            curve.setVisible(True)
            self.curves[handle.name] =  curve
        return curve

    

    def create_flicker_handle(self, name, pen="r", initPosition=None, positionChangedCallback=None, scenePosition=None):
        handle = self.get_handle_by_name(name)
        if handle is not None:
            return handle

        handle = FlickerHandle(name=name, pen=pen)
        # handle = Handle(name = "flicker", radius=10, typ="t", pen=pg.mkPen(width=4.5, color='r'), deletable=True)#, parent=self.plot)
        if scenePosition is not None:
            pos = self.plot.vb.mapSceneToView(scenePosition)
            handle.setPos(pos)

        elif isinstance(initPosition, tuple) and len(initPosition)==2:
            x,y = initPosition
            handle.setPos(x,y)
        else:
            handle.setPos(1,-2)

        if callable(positionChangedCallback):
            handle.sigPositionChanged.connect(positionChangedCallback) #self.on_handlePositionChanged)
        handle.setZValue(1500)
        self.plot.addItem(handle)
        self.create_curve_for_handle(handle)
        self.handles[name] = handle
        return handle

    def create_gr_handle(self, name, pen="r", initPosition=None, positionChangedCallback=None, scenePosition=None):
        handle = self.get_handle_by_name(name)
        if handle is not None:
            return handle

        handle = GRHandle(name=name, pen=pen)
        # handle = Handle(name = "flicker", radius=10, typ="t", pen=pg.mkPen(width=4.5, color='r'), deletable=True)#, parent=self.plot)
        if scenePosition is not None:
            pos = self.plot.vb.mapSceneToView(scenePosition)
            handle.setPos(pos)
            # print(pos)
            # handle.setScenePosition(scenePosition)

        elif isinstance(initPosition, tuple) and len(initPosition)==2:
            x,y = initPosition
            handle.setPos(x,y)

        else:
            handle.setPos(1,-2)

        if callable(positionChangedCallback):
            handle.sigPositionChanged.connect(positionChangedCallback)#self.on_handlePositionChanged)
        handle.setZValue(1500)
        self.plot.addItem(handle)
        self.create_curve_for_handle(handle)
        self.handles[name] = handle
        return handle


    def create_helper_handle(self):
        # self.roi = pg.LineROI([1, -17], [4, -17],width = 0, pen=pg.mkPen('b'))
        # self.plot.addItem(self.roi)
        # item = QtGui.QGraphicsRectItem( 10, 100.0, 1, 11 )
        # pixmap = QtGui.QPixmap()
        # pixmap.load("UI/flicker.png")
        
        # self.movable_handle = MovableHandle()#QtCore.QRectF(0, 0, 0.01, 0.01))
        # self.plot.addItem(self.movable_handle)
        # self.plot.addItem(item)

        # handle = Handle(radius=10, typ="f", pen=QtGui.QPen(QtGui.QColor(0, 0, 0)), parent=self.plot)
        
        
        # handle = FlickerHandle(name = "flicker", pen=pg.mkPen(width=4.5, color='r'))
        # # handle = Handle(name = "flicker", radius=10, typ="t", pen=pg.mkPen(width=4.5, color='r'), deletable=True)#, parent=self.plot)
        # handle.setPos(1,-2)
        # handle.sigPositionChanged.connect(self.on_handlePositionChanged)
        # self.plot.addItem(handle)
        # self.flickerHandle = handle
        self.flickerHandle = self.create_flicker_handle(name = "flicker", pen=pg.mkPen(width=4.5, color='r'), initPosition=(1,-2),positionChangedCallback=self.on_handlePositionChanged)
        # self.create_curve_for_handle(self.flickerHandle)

        # handle = Handle(name = "gr", radius=10, typ="r", pen=pg.mkPen(width=4.5, color='b'), deletable=True, handle_offset=QtCore.QPointF(-40, 40))#, parent=self.plot)
        # handle = GRHandle(name="gr", pen=pg.mkPen(width=4.5, color='b'))
        # handle.setPos(2,-2)
        # handle.sigPositionChanged.connect(self.on_handlePositionChanged)
        # self.plot.addItem(handle)
        # self.grHandle = handle
        self.grHandle = self.create_gr_handle(name = "gr", pen=pg.mkPen(width=4.5, color='b'), initPosition=(2,-2),positionChangedCallback=self.on_handlePositionChanged)
        # self.create_curve_for_handle(self.grHandle)

    def setLabelForAxis(self, axis, label, size=15, units=None, **kwargs):
        self.plot.setLabel(axis, "<font size=\"{s}\">{l}</font>".format(l=label,s=size))#, units="Hz")

    def setXLabel(self, label, **kwargs):
        self.setLabelForAxis("bottom", label)

    def setYLabel(self, label):
        self.setLabelForAxis("left", label)

    def setXRange(self, xmin, xmax):
        self.plot.setXRange(xmin,xmax)

    def getViewRange(self):
        return self.plot.viewRange()

    def subscribe_to_viewbox_x_range_changed(self, slot):
        self.plot.sigXRangeChanged.connect(slot)

    def subscribe_to_mouse_clicked(self, slot):
        return pg.SignalProxy(
            self.plot.scene().sigMouseClicked, 
            rateLimit=60, 
            slot=slot
            )

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
        # self.plot.setLabel("left", "<font size=\"15\">Power Spectral Density, S<sub>V</sub> (V<sup>2</sup>Hz<sup>-1</sup>)</font>")#, units="<font size=\"15\">V^2Hz-1</font>")
        self.setYLabel("Power Spectral Density, S<sub>V</sub> (V<sup>2</sup>Hz<sup>-1</sup>)")
        # self.plot.setLabel("bottom", "Frequency", units="Hz")
        # self.plot.setLabel("bottom", "<font size=\"15\">Frequency, f (Hz)</font>")#, units="Hz")
        self.setXLabel("Frequency, f (Hz)")
        #self.plot.setLimits(xMin=0.01,xMax = 7, yMin = -50, yMax = 10)
        self.plot.setLimits(xMin=-1,xMax = 7, yMin = -50, yMax = 10)
        self.plot.setXRange(-1,5)#(0.1,5)
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
        # self.mouseClickedProxy = pg.SignalProxy(
        #     self.plot.scene().sigMouseClicked, 
        #     rateLimit=60, 
        #     slot=self.mouse_clicked
        #     )

    def getViewRange(self):
        return self.plot.viewRange()

    def on_handlePositionChanged(self, handle, position):
        print(10*"=")
        print(position)
        
        rng = self.getViewRange()#self.plot.viewRange()
        xmin, xmax = rng[0]
        npoints = (xmax-xmin)/0.1 +1
        
        # freq = np.logspace(0,5, 51)
        freq = np.logspace(xmin,xmax, npoints)
        data = handle.calculateCurve(freq)

        print(freq)
        print(data)
        if handle.name in self.curves:
            self.curves[handle.name].setData(freq,data)
        print(10*"=")

    def appendToHistory(self, freq, data):
        if not self.history_buffer:
            self.history_buffer=HistoryBuffer(len(freq), self.historySize)
        self.history_buffer.append(data)
        buffer = self.history_buffer.get_buffer()
        for idx, a in enumerate(buffer):
            self.history_curves[idx].setData(freq,a)



    def updata_resulting_spectrum(self, freq,data, force = False):
        curve = self.curves[-1]
        curve.setData(freq,data)
        if self.update_history:
            self.appendToHistory(freq, data)

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

    # def mouse_clicked(self, evt):
    #     print("clicked")

class HistoryBuffer:
    """Fixed-size NumPy array ring buffer"""
    def __init__(self, data_size, max_history_size, dtype=float):
        self.data_size = data_size
        self.max_history_size = max_history_size
        self.history_size = 0
        self.counter = 0
        self.buffer = np.empty(shape=(max_history_size, data_size), dtype=dtype)

    @property
    def dataSize(self):
        return self.data_size

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
        
        self.layout = layout
        self.histogram_layout = histogram_layout


        self.spectral_ranges = {0:(1,1600,1),1:(0,102400,64)}
        self.display_range = 0
        
        self.thermal_noise = 0
        self.overal_amplification = 100*172

        self.points_per_decade = 21
        start, stop, step = self.spectral_ranges[self.display_range]
        self.data_size = sp.data_length_log_space(start,stop,points_per_decade=self.points_per_decade) # int((stop-start)/step)
        print(self.data_size)

        self.history_size = 100
        self.history = HistoryBuffer(self.data_size, self.history_size)
        
        self.counter = 0

        self.create_plot()

    def create_plot(self):
        """Create waterfall plot"""
        self.plot = self.layout.addPlot(title="<font size=\"20\">fS<sub>V</sub> Color Map</font>")
        
        self.plot.setLabel("bottom", "Frequency") #, units="Hz")
        self.plot.setLabel("left", "Time")

        self.plot.setYRange(-self.history_size, 0)
        
        self.plot.setLimits(xMin=0, yMax=0)
        self.plot.setLogMode(False,False)
        # self.plot.setXRange(0, 4)
        self.plot.showButtons()

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
        left_axis.setWidth(100)
        bottom_axis.tickFont = font
        bottom_axis.setStyle(tickTextOffset = 10)

        self.plot.showAxis("right", show=True)
        self.plot.showAxis("top", show=True)
        # self.plot.setLabel("left", "Power", units="V^2Hz-1")
        self.plot.setLabel("left", "<font size=\"15\">Time, t (sec)</font>")#, units="<font size=\"15\">V^2Hz-1</font>")
        # self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLabel("bottom", "<font size=\"15\">Frequency, f (Hz)</font>")#, units="Hz")
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

    def update_amplification(self, overal_amplification):
        self.overal_amplification = overal_amplification

    def update_thermal_noise(self, equivalent_resistance, sample_resistance, load_resistance, temperature):
        try:
            value = phys.calculate_thermal_noise(equivalent_resistance, sample_resistance, load_resistance, temperature)
            ampified_value = self.overal_amplification * value
            self.thermal_noise = ampified_value
        except:
            self.thermal_noise = 0

    

    def update_plot(self, rang, data):
        """Update waterfall plot"""
        if rang != self.display_range:
            return

        self.counter += 1
        spectral_data = data['d'][1:]
        frequencies = data['f'][1:]

        spectral_data = sp.remove50Hz(frequencies, spectral_data)
        
        frequencies, spectral_data = sp.interpolate_data_log_space(frequencies, spectral_data, points_per_decade=self.points_per_decade) 
        spectral_data = sp.subtract_thermal_noise(spectral_data, self.thermal_noise)
        spectral_data = np.multiply(frequencies,spectral_data)
        frequencies = np.log10(frequencies)
        spectral_data = np.log10(spectral_data)
        
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


# waterfallViewBase, waterfallViewForm = uic.loadUiType("UI/UI_WaterfallNoise.ui")
# class WaterfallNoiseWindow(waterfallViewBase, waterfallViewForm):
class WaterfallNoiseWindow(QtGui.QWidget, Ui_WaterfallNoise):
    def __init__(self, parent = None):
        # super(waterfallViewBase, self).__init__(parent)
        super().__init__(parent)
        self.setupUi(self)
        self.waterfall_widget = WaterfallPlotWidget(self.ui_waterfall_plot, self.ui_histogram_layout)

    def update_data(self, rang, data):
        self.waterfall_widget.update_plot(rang, data)

    def update_thermal_noise(self, equivalent_resistance, sample_resistance, load_resistance, temperature):
        self.waterfall_widget.update_thermal_noise(equivalent_resistance, sample_resistance, load_resistance, temperature)
    
    def update_amplification(self, overal_amplification):
        self.waterfall_widget.update_amplification(overal_amplification)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    wnd = WaterfallNoiseWindow()
    wnd.show()
    sys.exit(app.exec_())
