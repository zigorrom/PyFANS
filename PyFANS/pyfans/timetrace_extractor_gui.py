import sys
import os
import argparse
from PyQt4 import uic, QtGui, QtCore


def get_pyfans_folder():
    this_folder = os.path.dirname(__file__)
    head, tail = os.path.split(this_folder)
    while tail != "pyfans":
        head, tail = os.path.split(head)

    return head
    

if __name__ =="__main__":
    parentdir = get_pyfans_folder()
    sys.path.insert(0,parentdir) 


import pyfans.utils.ui_helper as uih
from pyfans.utils.utils import open_folder_with_file_selected, open_folder_in_explorer
from pyfans.hardware.modern_fans_timetrace_extractor import Parameters
from pyfans.forms.UI_TimetraceExtractor import Ui_TimetraceExtractor



# timetraceExtractorViewBase, timetraceExtractorViewForm = uic.loadUiType(os.path.join(get_pyfans_folder(), "UI/UI_TimetraceExtractor.ui"))
# class TimetraceExtractorGUI(timetraceExtractorViewBase, timetraceExtractorViewForm):
class TimetraceExtractorGUI(QtGui.QWidget, Ui_TimetraceExtractor):
    measurement_data_filename_ui = uih.bind("ui_measurement_data_filename","text",str)
    filename_ui = uih.bind("ui_filename","text",str)

    sample_rate_ui = uih.bind("ui_sample_rate","text",int)
    points_per_shot_ui = uih.bind("ui_points_per_shot","text",int)
    total_amplification_ui = uih.bind("ui_total_amplification","text",int)
    total_time_to_convert_ui = uih.bind("ui_total_time_to_convert","text",int)
    decimated_sample_rate_ui = uih.bind("ui_decimate_sample_rate","text", int)

    use_timetrace_extractor_settings = uih.bind("ui_use_timetrace_settings", "checked", bool)
    use_sample_rate = uih.bind("ui_use_sample_rate", "checked", bool)
    use_points_per_shot = uih.bind("ui_use_points_per_shot", "checked", bool)
    use_amplification = uih.bind("ui_use_amplification", "checked", bool)
    use_total_time = uih.bind("ui_use_total_time", "checked", bool)
    use_decimated_sample_rate = uih.bind("ui_use_decimated_sample_rate", "checked", bool)
    use_redirect_output = uih.bind("ui_redirect_output", "checked", bool)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi()

        self._working_directory  = ""
        self._output_directory = ""
        self._measurement_data_filename=  ""
        self._filename = ""

        self._script_directory = os.path.dirname(__file__)
        self._timetrace_converter_script_name = os.path.join(self._script_directory, "hardware\\modern_fans_timetrace_extractor.py")
        print(self._script_directory)
        print(self._timetrace_converter_script_name)

        self.process = QtCore.QProcess(self)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.on_programm_execution_started)
        self.process.finished.connect(self.on_programm_execution_finished)
        #ui_program_output

    def __del__(self):
        if self.process:
            self.process.kill()


    def setupUi(self):
        super().setupUi(self)
        self.ui_sample_rate.setValidator(QtGui.QIntValidator())
        self.ui_points_per_shot.setValidator(QtGui.QIntValidator())
        self.ui_total_amplification.setValidator(QtGui.QIntValidator())
        self.ui_total_time_to_convert.setValidator(QtGui.QIntValidator())
        self.ui_decimate_sample_rate.setValidator(QtGui.QIntValidator())
        self.ui_use_sample_rate.stateChanged.connect(lambda state: self.ui_sample_rate.setEnabled(bool(state)))
        self.ui_use_points_per_shot.stateChanged.connect(lambda state: self.ui_points_per_shot.setEnabled(bool(state)))
        self.ui_use_amplification.stateChanged.connect(lambda state: self.ui_total_amplification.setEnabled(bool(state)))
        self.ui_use_total_time.stateChanged.connect(lambda state: self.ui_total_time_to_convert.setEnabled(bool(state)))
        self.ui_use_decimated_sample_rate.stateChanged.connect(lambda state: self.ui_decimate_sample_rate.setEnabled(bool(state)))


    def collectSettingsParams(self):
        settings_params = []
        if self.use_timetrace_extractor_settings:
            if self.use_sample_rate:
                settings_params.append(Parameters.SampleRateOption)
                settings_params.append(self.sample_rate_ui)
            
            if self.use_points_per_shot:
                settings_params.append(Parameters.PointsPerShotOption)
                settings_params.append(self.points_per_shot_ui)

            if self.use_amplification:
                settings_params.append(Parameters.AmplificationOption)
                settings_params.append(self.total_amplification_ui)

            if self.use_total_time:
                settings_params.append(Parameters.LengthOption)
                settings_params.append(self.total_time_to_convert_ui)
        
            if self.use_decimated_sample_rate:
                settings_params.append(Parameters.DecimatedSampleRateOption)
                settings_params.append(self.decimated_sample_rate_ui)
        
        if self.use_redirect_output:
            settings_params.append(Parameters.OutputFolderOption)
            settings_params.append(self._output_directory)

        return settings_params

    def callProgram(self, params):
        all_parameters = ['python', self._timetrace_converter_script_name]
        all_parameters.extend(params)
        all_parameters = [str(item) for item in all_parameters]
        print(all_parameters)
        cmd_params = " ".join(all_parameters)
        print(cmd_params)
##        self.process.start('python', cmd_params)
        self.process.start(cmd_params)
        
    def dataReady(self):
        cursor = self.ui_program_output.textCursor()
        cursor.movePosition(cursor.End)
        ready_text = str(self.process.readAll(), encoding = "utf-8")
        cursor.insertText(ready_text)
        self.ui_program_output.ensureCursorVisible()
        self.ui_program_output.verticalScrollBar().setValue(self.ui_program_output.verticalScrollBar().maximum())

    def on_programm_execution_started(self):
        print("started")
        self.disable_user_input()

    def on_programm_execution_finished(self):
        print("finished")
        self.enable_user_input()

    def set_user_input_state(self, state):
        self.ui_select_measurement_data_file.setEnabled(state)
        self.ui_open_measurement_data_file.setEnabled(state)
        self.ui_convert_all.setEnabled(state)
        self.ui_select_file.setEnabled(state)
        self.ui_open_file.setEnabled(state)
        self.ui_convert_file.setEnabled(state)
        self.ui_use_timetrace_settings.setEnabled(state)
        self.ui_redirect_output.setEnabled(state)
        self.ui_select_output_folder.setEnabled(state)

    def enable_user_input(self):
        self.set_user_input_state(True)

    def disable_user_input(self):
        self.set_user_input_state(False)

    #************************************************************
    def open_file_dialog(self):
        print("Select file")
        filename = os.path.abspath(QtGui.QFileDialog.getOpenFileName(self,caption="Select Filename", directory = self._working_directory))
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(filename)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        return (retval, filename)
        
    def set_filename(self, filename):
        if not filename or not os.path.isfile:
            print("Filename does not exist or empty parameter")

        self._filename = filename
        folder_name, filename_temp = os.path.split(filename)
        self.filename_ui = ".../{0}".format(filename_temp)
        self.set_working_folder(folder_name)


    def set_measurement_data_filename(self, measurement_data_filename):
        if not measurement_data_filename or not os.path.isfile:
            print("Filename does not exist or empty parameter")

        self._measurement_data_filename = measurement_data_filename
        folder_name, filename_temp = os.path.split(measurement_data_filename)
        self.measurement_data_filename_ui = ".../{0}".format(filename_temp)
        self.set_working_folder(folder_name)


    def set_working_folder(self, folder):
        if folder and os.path.isdir(folder):
            self._working_directory = folder
        else:
            print("Folder is not existing")


    @QtCore.pyqtSlot()
    def on_ui_select_measurement_data_file_clicked(self):
        print("select measur data file")
        result, filename = self.open_file_dialog()
        if result:
            self.set_measurement_data_filename(filename)

    @QtCore.pyqtSlot()
    def on_ui_open_measurement_data_file_clicked(self):
        print("open_folder")
        open_folder_with_file_selected(self._measurement_data_filename)
        if os.path.isdir(self._output_directory) and self.use_redirect_output:
            open_folder_in_explorer(self._output_directory)

    @QtCore.pyqtSlot()
    def on_ui_convert_all_clicked(self):
        print("convert all")
        param_list = []
        #self.callProgram()
        if self._measurement_data_filename and os.path.isfile(self._measurement_data_filename):
            param_list.append(Parameters.MeasurementDataFileOption)
            param_list.append(self._measurement_data_filename)
            param_list.extend(self.collectSettingsParams())
            self.callProgram(param_list)

    @QtCore.pyqtSlot()
    def on_ui_select_file_clicked(self):
        print("select file")
        result, filename = self.open_file_dialog()
        if result:
            self.set_filename(filename)

    @QtCore.pyqtSlot()
    def on_ui_open_file_clicked(self):
        print("select file")
        open_folder_with_file_selected(self._filename)
        if os.path.isdir(self._output_directory) and self.use_redirect_output:
            open_folder_in_explorer(self._output_directory)

    @QtCore.pyqtSlot()
    def on_ui_convert_file_clicked(self):
        print("select convert file")
        param_list = []
        #self.callProgram()
        if self._measurement_data_filename and os.path.isfile(self._measurement_data_filename):
            param_list.append(Parameters.FilenameOption)
            param_list.append(self._filename)
            param_list.extend(self.collectSettingsParams())
            self.callProgram(param_list)
    
    @QtCore.pyqtSlot()
    def on_ui_select_output_folder_clicked(self):
        folder = os.path.abspath(QtGui.QFileDialog.getExistingDirectory(self,caption="Select output folder", directory = self._working_directory))
        self._output_directory = folder

    @QtCore.pyqtSlot()
    def on_ui_terminate_execution_clicked(self):
        if self.process.state() != QtCore.QProcess.NotRunning:
            self.process.kill()

def gui(**kwargs):
    import ctypes
    myappid = "fzj.pyfans.pyfans.21" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    measurement_data_filename = kwargs.get("mf", None)
    filename = kwargs.get("f", None)

    


    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS TimetraceExtractor")
    app.setStyle("cleanlooks")
    #icon_file = "pyfans.ico"
    icon_file = "UI/Icons/pyfans_icon.png"
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

    if measurement_data_filename:
        wnd.set_measurement_data_filename(measurement_data_filename)

    if filename:
        wnd.set_filename(filename)

    wnd.show()
    return app.exec_()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert timetrace from binary format to readable .dat format')
    
    parser.add_argument(Parameters.MeasurementDataFileOption, metavar='measurement_data_file', type=str, nargs='?', default = "",
                    help='The name of main file where all measured data is stored')
    
    parser.add_argument(Parameters.FilenameOption, metavar='filename', type = str, nargs='?' , default = "",
                        help = 'The name of file to convert. You would need to specify params for convertion')

    args = parser.parse_args()
    args = vars(args)

    sys.exit(gui(**args))