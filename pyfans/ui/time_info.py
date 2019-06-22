import time
from PyQt4 import uic, QtCore, QtGui
from pyfans.ui.forms.UI_TimeInfo import Ui_TimeInfo

# timeinfoViewBase, timeinfoViewForm = uic.loadUiType("UI/UI_TimeInfo.ui")
# class UI_TimeInfo(timeinfoViewBase, timeinfoViewForm):
class UI_TimeInfo(QtGui.QWidget, Ui_TimeInfo):
    def __init__(self, parent = None):
        # super(timeinfoViewBase,self).__init__(parent)
        super().__init__(parent)
        self.setupUi(self)
        self._timer = QtCore.QTimer()
        self.reset()
        self.time_format = "%Y-%m-%d %H:%M:%S"
        self._timer.timeout.connect(self.update_time)
        #self._experiment_start_time = None
        #self._experiment_elapsed_time = None
        #self._experiment_time_left = None

    def start_timer(self):
        self._timer.start(1000)

    def stop_timer(self):
        self._timer.stop()

    def set_time(self, experiment_start_time, experiment_elapsed_time, experiment_time_left):
        self._experiment_start_time = experiment_start_time
        self._experiment_elapsed_time = experiment_elapsed_time
        self._experiment_time_left = experiment_time_left

    def update_time(self):
        self._experiment_elapsed_time += 1
        self._experiment_time_left -= 1
        if self._experiment_time_left<0:
            self._experiment_time_left = 0
        self.ui_update_time()

    def ui_update_time(self):
        #time_tuple = time.localtime(timestamp)
        #time_tuple = (2008, 11, 12, 13, 51, 18, 2, 317, 0)
        #date_str = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)
        self.ui_experiment_started.setText(time.strftime(self.time_format, time.localtime(self._experiment_start_time)))
        self.ui_elapsed_time.setText(time.strftime("%H:%M:%S", time.gmtime(self._experiment_elapsed_time)))
        self.ui_time_left.setText(time.strftime("%H:%M:%S", time.gmtime(self._experiment_time_left)))

    def reset(self):
        self._experiment_start_time = 0
        self._experiment_elapsed_time = 0
        self._experiment_time_left = 0
