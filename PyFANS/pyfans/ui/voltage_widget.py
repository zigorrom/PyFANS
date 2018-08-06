import sys
import functools
from PyQt4 import QtCore, QtGui, uic

class LedWidget(QtGui.QWidget):
    OK_COLOR = QtCore.Qt.green
    WARNING_COLOR = QtCore.Qt.yellow
    ERROR_COLOR = QtCore.Qt.red

    def __init__(self, parent=None):
        super().__init__(parent)

        color1 = QtGui.QColor(self.OK_COLOR) #255, 0, 0)
        color2 = QtGui.QColor(self.WARNING_COLOR) #0, 255, 0)

        self.color_anim = QtCore.QPropertyAnimation(self, 'backColor')
        self.color_anim.setStartValue(color1)
        self.color_anim.setKeyValueAt(0.5, color2)
        self.color_anim.setEndValue(color1)
        self.color_anim.setDuration(1000)
        self.color_anim.setLoopCount(-1)
        self.color_anim.start()

    # def setPalette(self, pal):
    #     super().setPalette(pal)
    #     self.repaint()

    def getBackColor(self):
        return self.palette().color(QtGui.QPalette.Background)

    def setBackColor(self, color):
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Background, color)
        self.setPalette(pal)

    backColor = QtCore.pyqtProperty(QtGui.QColor, getBackColor, setBackColor)

    def set_okay_state(self):
        self.color_anim.stop()
        self.backColor = self.OK_COLOR

    def set_idle_state(self):
        self.color_anim.stop()
        self.backColor = self.WARNING_COLOR

    def set_warning_state(self):
        self.color_anim.stop()
        self.backColor = self.WARNING_COLOR

    def set_error_state(self):
        self.color_anim.stop()
        self.backColor = self.ERROR_COLOR

    def set_in_progress(self):
        self.color_anim.start()


    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(self.getBackColor())
        painter.drawEllipse(0,0,self.width(),self.height())



    
        

# class LedWidget(QtGui.QWidget):
#     def __init__(self, color = None, state=False,**kwargs):
#         super().__init__(**kwargs)
#         self._color = color
#         self._state =  state
#         self._blink_timer = QtCore.QTimer()
#         self._blink_timer.timeout.connect(self.toggle)

#     @property
#     def led_color(self):
#         return self._color

#     @led_color.setter
#     def led_color(self, value):
#         self._color = value 

#     @property
#     def state(self):
#         return self._state

#     @state.setter
#     def state(self, value):
#         self._state = value

#     @property
#     def is_blinking(self):
#         return self._blink_timer.isActive()

#     def set_state(self, state):
#         assert isinstance(state, bool), "state should be boolean"
#         if self._state == state:
#             return

#         self._state = state
#         self.update()

#     def switch_on(self):
#         self.set_state(True)

#     def switch_off(self):
#         self.set_state(False)

#     def paintEvent(self, e):
#         if not self._state:
#             return
#         painter = QtGui.QPainter(self)
#         painter.setRenderHint(QtGui.QPainter.Antialiasing)
#         painter.setBrush(self._color)
#         painter.drawEllipse(0,0,self.width(),self.height())

#     def toggle(self):
#         self.set_state(not self._state)

#     def start_blink(self, delay):
#         self._blink_timer.start(delay)

#     def stop_blink(self):
#         self._blink_timer.stop()

def test_led():    
    app = QtGui.QApplication(sys.argv)
    w = LedWidget()
    timer = QtCore.QTimer(w)
    
    timer.singleShot(1000, w.set_warning_state)
    timer.singleShot(2000, w.set_okay_state)
    timer.singleShot(3000, w.set_error_state)
    timer.singleShot(4000, w.set_in_progress)
    w.show()

    # widget = LedWidget(color=QtCore.Qt.red)
    # widget.resize(200,200)
    # widget.show()
    # widget.start()
    # widget.led_color = QtCore.Qt.green
    # widget.start_blink(300)
    return app.exec_()


voltageWidgetBase, voltageWidgetForm = uic.loadUiType("UI/UI_VoltageView.ui")
class UI_VoltageWidget(voltageWidgetBase, voltageWidgetForm):
    OK, WARNING, ERROR, IN_PROGRESS = states = range(4)
    OK_COLOR = QtCore.Qt.green
    WARNING_COLOR = QtCore.Qt.yellow
    ERROR_COLOR = QtCore.Qt.red

    def __init__(self,parent = None):
        super(voltageWidgetBase, self).__init__(parent)
        self.setupUi(self)
        self._closingAllowed = False
        self._closingTimer = QtCore.QTimer(self)
        # self.
        # self.ui_status_led_2 = LedWidget()#LedWidget(QtCore.Qt.red)
        # self.main_layout.addWidget(self.ui_status_led_2)
        # self._state = self.IN_PROGRESS
        self.ui_status_led.show()
        print(self.ui_status_led)
        self.reset()
        


    # def set_state(self, state):
    #     # if not state in self.states:
    #     #     return
    #     # if self.ui_status_led.is_blinking:
    #     #     self.ui_status_led.stop_blink()

    #     if state is self.OK:
    #         # self.ui_status_led.led_color = self.OK_COLOR
    #         self.ui_status_led.set_okay_state()

    #     elif state is self.WARNING:
    #         # self.ui_status_led.led_color = self.WARNING_COLOR
    #         self.ui_status_led.set_warning_state()

    #     elif state is self.ERROR:
    #         # self.ui_status_led.led_color = self.ERROR_COLOR
    #         self.ui_status_led.set_error_state()

    #     elif state is self.IN_PROGRESS:
    #         # self.ui_status_led.led_color = self.WARNING_COLOR
    #         # self.ui_status_led.start_blink(200)
    #         self.ui_status_led.set_in_progress()

    #     # self.ui_status_led.switch_on()
    #     # self._state = state

    def set_okay_state(self):
        # self.set_state(self.OK)
        self.ui_status_led.set_okay_state()

    def set_warning_state(self):
        # self.set_state(self.WARNING)
        self.ui_status_led.set_warning_state()

    def set_error_state(self):
        # self.set_state(self.ERROR)
        self.ui_status_led.set_error_state()

    def set_in_progress_state(self):
        # self.set_state(self.IN_PROGRESS)
        self.ui_status_led.set_in_progress()

    def set_drain_source_voltage(self, voltage):
        self.ui_drain_source_voltage.setText("{0:9.6f}".format(voltage))

    def set_gate_source_voltage(self, voltage):
        self.ui_gate_source_voltage.setText("{0:9.6f}".format(voltage))

    def reset(self):
        self.set_okay_state()
        self.set_drain_source_voltage(0)
        self.set_gate_source_voltage(0)

    def on_close_allowed(self):
        self._closingAllowed = True
        self.close()

    def closeEvent(self, event):
        if self._closingAllowed:
            event.accept()
        
        elif self._closingTimer.isActive():
                event.ignore()
                
        else:
            event.ignore()
            print("start waiting")
            self._closingTimer.singleShot(2000, self.on_close_allowed)
        # close = QMessageBox()
        # close.setText("You sure?")
        # close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        # close = close.exec()

        # if close == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()


def test_voltage_control():
    import time
    app = QtGui.QApplication(sys.argv)
    widget = UI_VoltageWidget()
    timer = QtCore.QTimer(widget)
    

    widget.show()
    widget.set_drain_source_voltage(12.4211351313)
    widget.set_gate_source_voltage(12.4211351313)
    timer.singleShot(1000, widget.set_okay_state)
    timer.singleShot(2000,  widget.set_warning_state)
    timer.singleShot(3000,  widget.set_in_progress_state)
    timer.singleShot(10000,  widget.set_error_state)
   
    # time.sleep(0.5)
    # widget.set_warning_state()
    # time.sleep(0.5)
    # widget.set_in_progress_state()
    # time.sleep(0.5)
    # widget.set_error_state()

    return app.exec_()


if __name__ == "__main__":
    # sys.exit(test_led())
    sys.exit(test_voltage_control())