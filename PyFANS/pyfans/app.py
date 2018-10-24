# with open('qdata') as f:
#     f.fileinfo = {'description': 'this file contains stuff...'}
#     print(f.fileinfo)
import sys
import ctypes
from queue import Queue
from PyQt4 import QtCore, QtGui

from pyfans import __app_id__, __app_name__, __version__ #, FANS_UI_Controller, FANS_UI_MainView
import pyfans.main_window #import FANS_UI_MainView
import pyfans.main_controller #import FANS_UI_Controller

import pyfans.utils.utils as util


class PyFANSapp(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName(__app_name__)
        self.setApplicationVersion(__version__)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__app_id__)

        self.setupUiStyle()
        self.setupApplication()

    def setupUiStyle(self):
        icon_file = "UI/Icons/pyfans_icon2.png"
    
        app_icon = QtGui.QIcon()
        app_icon.addFile(icon_file, QtCore.QSize(16,16))
        app_icon.addFile(icon_file, QtCore.QSize(24,24))
        app_icon.addFile(icon_file, QtCore.QSize(32,32))
        app_icon.addFile(icon_file, QtCore.QSize(48,48))
        app_icon.addFile(icon_file, QtCore.QSize(256,256))
        self.setWindowIcon(app_icon)

    def setupApplication(self):
        self._main_window = pyfans.main_window.FANS_UI_MainView()
        self._controller = pyfans.main_controller.FANS_UI_Controller(self._main_window)

        script_executed_with_console = util.check_if_script_executed_with_console()
        self._controller.script_executed_with_console = script_executed_with_console
        self._main_window.ui_show_message_in_status_bar("Execution in {0} mode".format("console" if script_executed_with_console else "window"), 5000)
        
        if not script_executed_with_console:
            q = Queue()
            sys.stdout = util.WriteStream(q)
            console_thread = QtCore.QThread()
            receiver = util.MyReceiver(q)
            receiver.mysignal.connect(self._controller.console_window.append_text)
            receiver.moveToThread(console_thread)
            console_thread.started.connect(receiver.run)
            console_thread.start()

    def run(self):
        sys.exit(self.exec_())


