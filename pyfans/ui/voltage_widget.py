import sys
import functools
from PyQt4 import QtCore, QtGui, uic
from pyfans.ui.forms.UI_VoltageView import Ui_VoltageView

# voltageWidgetBase, voltageWidgetForm = uic.loadUiType("UI/UI_VoltageView.ui")
# class UI_VoltageWidget(voltageWidgetBase, voltageWidgetForm):
class UI_VoltageWidget(QtGui.QWidget, Ui_VoltageView):
    OK, WARNING, ERROR, IN_PROGRESS = states = range(4)
    OK_COLOR = QtCore.Qt.green
    WARNING_COLOR = QtCore.Qt.yellow
    ERROR_COLOR = QtCore.Qt.red

    def __init__(self,parent = None):
        # super(voltageWidgetBase, self).__init__(parent)
        super().__init__(parent)
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