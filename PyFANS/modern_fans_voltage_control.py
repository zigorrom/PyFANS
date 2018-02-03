import sys
from PyQt4 import QtCore, QtGui, uic

class LedWidget(QtGui.QWidget):
    def __init__(self, color = None, state=False,**kwargs):
        super().__init__(**kwargs)
        self._color = color
        self._state =  state
        self._blink_timer = QtCore.QTimer()
        self._blink_timer.timeout.connect(self.toggle)

    @property
    def led_color(self):
        return self._color

    @led_color.setter
    def led_color(self, value):
        self._color = value 

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def is_blinking(self):
        return self._blink_timer.isActive()

    def set_state(self, state):
        assert isinstance(state, bool), "state should be boolean"
        if self._state == state:
            return

        self._state = state
        self.update()

    def switch_on(self):
        self.set_state(True)

    def switch_off(self):
        self.set_state(False)

    def paintEvent(self, e):
        if not self._state:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(self._color)
        painter.drawEllipse(0,0,self.width(),self.height())

    def toggle(self):
        self.set_state(not self._state)

    def start_blink(self, delay):
        self._blink_timer.start(delay)

    def stop_blink(self):
        self._blink_timer.stop()

def test_led():    
    app = QtGui.QApplication(sys.argv)
    widget = LedWidget(QtCore.Qt.red, True)
    widget.resize(200,200)
    widget.show()
    widget.start_blink(300)
    return app.exec_()


voltageControlBase, voltageControlForm = uic.loadUiType("UI_VoltageView.ui")
class VoltageControl(voltageControlBase, voltageControlForm):
    OK, WARNING, ERROR, IN_PROGRESS = states = range(4)
    OK_COLOR = QtCore.Qt.green
    WARNING_COLOR = QtCore.Qt.yellow
    ERROR_COLOR = QtCore.Qt.red

    def __init__(self,parent = None):
        super(voltageControlBase, self).__init__(parent)
        self.setupUi(self)
        
        self._state = self.IN_PROGRESS
        self.reset()
        


    def set_state(self, state):
        if not state in self.states:
            return
        if self.ui_status_led.is_blinking:
            self.ui_status_led.stop_blink()

        if state is self.OK:
            self.ui_status_led.led_color = self.OK_COLOR
        elif state is self.WARNING:
            self.ui_status_led.led_color = self.WARNING_COLOR
        elif state is self.ERROR:
            self.ui_status_led.led_color = self.ERROR_COLOR
        elif state is self.IN_PROGRESS:
            self.ui_status_led.led_color = self.WARNING_COLOR
            self.ui_status_led.start_blink(200)

        self.ui_status_led.switch_on()
        self._state = state

    def set_okay_state(self):
        self.set_state(self.OK)

    def set_warning_state(self):
        self.set_state(self.WARNING)

    def set_error_state(self):
        self.set_state(self.ERROR)

    def set_in_progress_state(self):
        self.set_state(self.IN_PROGRESS)

    def set_drain_source_voltage(self, voltage):
        self.ui_drain_source_voltage.setText("{0:6.3f}".format(voltage))

    def set_gate_source_voltage(self, voltage):
        self.ui_gate_source_voltage.setText("{0:6.3f}".format(voltage))

    def reset(self):
        self.set_okay_state()
        self.set_drain_source_voltage(0)
        self.set_gate_source_voltage(0)

def test_voltage_control():
    app = QtGui.QApplication(sys.argv)
    widget = VoltageControl()
    widget.show()
    widget.set_drain_source_voltage(12.4211351313)
    return app.exec_()


if __name__ == "__main__":
    #sys.exit(test_led())
    sys.exit(test_voltage_control())