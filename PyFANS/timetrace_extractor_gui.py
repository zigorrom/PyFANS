import sys
import os
from PyQt4 import uic, QtGui, QtCore

timetraceExtractorViewBase, timetraceExtractorViewForm = uic.loadUiType("UI/UI_TimetraceExtractor.ui")
class TimetraceExtractorGUI(timetraceExtractorViewBase, timetraceExtractorViewForm):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi()

        self._script_directory = os.path.dirname(__file__)
        self._timetrace_converter_script_name = os.path.join(self._script_directory, "modern_fans_timetrace_extractor.py")
        print(self._script_directory)
        print(self._timetrace_converter_script_name)

        self.process = QtCore.QProcess(self)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.on_programm_execution_started)
        self.process.finished.connect(self.on_programm_execution_finished)
        #ui_program_output



    def setupUi(self):
        super().setupUi(self)

    def collectParams(self):
        return [self._timetrace_converter_script_name]

    def callProgram(self):
        self.process.start('python',self.collectParams())

    def dataReady(self):
        cursor = self.ui_program_output.textCursor()
        cursor.movePosition(cursor.End)
        ready_text = str(self.process.readAll(), encoding = "utf-8")
        cursor.insertText(ready_text)
        self.ui_program_output.ensureCursorVisible()

    def on_programm_execution_started(self):
        print("started")
        

    def on_programm_execution_finished(self):
        print("finished")

    #************************************************************
    @QtCore.pyqtSlot()
    def on_ui_measurement_data_file_clicked(self):
        print("select folder")

    @QtCore.pyqtSlot()
    def on_ui_open_folder_clicked(self):
        print("open_folder")

    @QtCore.pyqtSlot()
    def on_ui_convert_all_clicked(self):
        print("convert all")
        self.callProgram()
    
    @QtCore.pyqtSlot()
    def on_ui_select_file_clicked(self):
        print("select file")

    @QtCore.pyqtSlot()
    def on_ui_open_file_clicked(self):
        print("select file")

    @QtCore.pyqtSlot()
    def on_ui_convert_file_clicked(self):
        print("select convert file")

    @QtCore.pyqtSlot()
    def on_ui_settings_clicked(self):
        print("settings")






def gui():
    import ctypes
    myappid = "fzj.pyfans.pyfans.21" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS TimetraceExtractor")
    app.setStyle("cleanlooks")
    #icon_file = "pyfans.ico"
    icon_file = "UI/Icons/pyfans.png"
    app_icon = QtGui.QIcon()
    app_icon.addFile(icon_file, QtCore.QSize(16,16))
    app_icon.addFile(icon_file, QtCore.QSize(24,24))
    app_icon.addFile(icon_file, QtCore.QSize(32,32))
    app_icon.addFile(icon_file, QtCore.QSize(48,48))
    app_icon.addFile(icon_file, QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)
    #app.setWindowIcon(QtGui.QIcon('pyfans.ico'))
    #about_window = UI_About()
    #about_window.show()

    wnd = TimetraceExtractorGUI()
    wnd.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(gui())