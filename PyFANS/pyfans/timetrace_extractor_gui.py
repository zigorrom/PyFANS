import sys
import os
from PyQt4 import uic, QtGui, QtCore

timetraceExtractorViewBase, timetraceExtractorViewForm = uic.loadUiType("UI/UI_TimetraceExtractor.ui")
class TimetraceExtractorGUI(timetraceExtractorViewBase, timetraceExtractorViewForm):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi()

        self._working_directory  = ""
        self._measurement_data_filename=  ""
        self._filename = ""

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
        self.disable_user_input()

    def on_programm_execution_finished(self):
        print("finished")
        self.enable_user_input()

    def enable_user_input(self):
        pass

    def disable_user_input(self):
        pass

    #************************************************************
    def open_file_dialog(self):
        print("Select file")
        filename = os.path.abspath(QtGui.QFileDialog.getOpenFileName(self,caption="Select Folder", directory = self._working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(folder_name)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        return filename
        
    def set_filename(self, filename):
        pass

    def set_measurement_data_filename(self, measurement_data_filename):
        pass

    def set_working_folder(self, folder):
        pass

    @QtCore.pyqtSlot()
    def on_ui_select_measurement_data_file_clicked(self):
        print("select measur data file")
        filename = self.open_file_dialog()
        if filename and os.path.isfile(filename):
            self.set_filename(filename)

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