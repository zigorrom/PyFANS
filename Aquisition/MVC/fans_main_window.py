from PyQt4 import QtCore, QtGui, uic
import sys

from fans_plot import SpectrumPlotWidget, WaterfallPlotWidget, TimetracePlotWidget
from settings import WndTutorial, ChannelSettingsEditor, VoltageSettingsEditor
from node_configuration import Configuration
from fans_controller import FANS_CONTROLLER,FANS_AQUISITION_CONTROLLER
from data import DataHandler
from fans_measurement_file_writer import NoiseExperimentWriter

fans_main_view_base, fans_main_view_form = uic.loadUiType("Views/FANS_main_view.ui")
class FANS_MAIN_WINDOW(fans_main_view_base,fans_main_view_form):
    def __init__(self,configuration = None, parent = None):
        super(fans_main_view_base,self).__init__(parent)
        self.setupUi(self)
        self.setup_fans_ui()
        self._configuration = Configuration()
        ### make to import visa resource from configuration
        self._fans_controller = FANS_CONTROLLER("USB0::0x0957::0x1718::TW52524501::INSTR")
        self._fans_controller.set_configuration(self._configuration)
        self._data_handler = DataHandler(max_history_size = 50)
        self._data_handler.data_updated.connect(self.spectrumPlotWidget.update_plot)
        self._data_handler.average_updated.connect(self.spectrumPlotWidget.update_average)
        self._data_handler.data_updated.connect(self.timetracePlotWidget.update_plot)
        self._data_handler.history_updated.connect(self.timeNoisePlotWidget.update_plot)

        self._fans_acquisition = FANS_AQUISITION_CONTROLLER(self._fans_controller)
        self._fans_acquisition.daq_sample_rate = 500000
        self._fans_acquisition.daq_points_per_shot = 50000
        self._fans_acquisition.daq_total_samples = 50000000
        
        
        
        self.load_settings()
        self.setup_daq()
        
        

    def setup_fans_ui(self):
        max_hist_size=  50
        self.spectrumPlotWidget = SpectrumPlotWidget(self.noisePlot,0)
        self.timetracePlotWidget = TimetracePlotWidget(self.timetracePlot,0)
        self.timeNoisePlotWidget = WaterfallPlotWidget(self.timeNoisePlot,  self.histogramPlotLayout, max_history_size=max_hist_size)

    def setup_daq(self):
        pass
        
    

    def closeEvent(self,event):
        print("closing")
        self.save_settings()
## FILE MENU ITEM
    
    @QtCore.pyqtSlot()
    def on_actionWorkingFolder_triggered(self):
        print("working folder clicked")
        self.__select_working_folder()

    def __select_working_folder(self):
        folder_name = QtGui.QFileDialog.getExistingDirectory(self, "Select Folder")
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(folder_name)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()


    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self):
        print("exit pressed")
        
## SETTINGS MENU ITEM
    
    @QtCore.pyqtSlot()
    def on_actionInputSettings_triggered(self):
        node = self._configuration.get_node_from_path("input_settings")
        dialog = ChannelSettingsEditor(node)
        dialog.exec_()
        #dialog = ChannelSettings(self)
        #if dialog.exec_():
        #   print("channel settings")
        print("channel settings")


    @QtCore.pyqtSlot()
    def on_actionOutputSettings_triggered(self):
        node = self._configuration.get_node_from_path("out_settings")
        dialog = ChannelSettingsEditor(node)
        dialog.exec_()
        #dialog = OutputSettings(self)
        #if dialog.exec_():
        print("output settings")    
        

    @QtCore.pyqtSlot()  
    def on_actionAcquisitionSettings_triggered(self):
        #dialog = AcquisitionSettings(self)
        #if dialog.exec_():
        print("acquisition settings")

    @QtCore.pyqtSlot()  
    def on_actionVoltageSettings_triggered(self):
        dialog = VoltageSettingsEditor(self._configuration)
        dialog.exec_()
        #dialog = PowerSupplySettings(self)
        #if dialog.exec_():
        print("acquisition settings")
        
    
## WINDOW MENU ITEM
    @QtCore.pyqtSlot()
    def on_actionRestoreWindows_triggered(self):
        print("window restore")
        self.restoreWindow()
    
## HELP MENU ITEM
    @QtCore.pyqtSlot()
    def on_actionAbout_triggered(self):
        print("about")

##
    def start(self):
        self._fans_acquisition.daq_init_acquisition(self._data_handler)
        self._fans_acquisition.daq_start_acquisition()

        
    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        print("start")
        self.start()

    def stop(self):
        self._fans_acquisition.daq_stop_acquisition()
        #music = pyglet.resource.media("stop.mp3")
        #music.play()
        #pyglet.app.run()


    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        print("stop")
        self.stop()

    @QtCore.pyqtSlot()
    def on_singleShotButton_clicked(self):
        print("single shot")


    


    def save_settings(self):
        print("savng settings")
        self._configuration.save_config()
        self.saveWindowState()

    def load_settings(self):
        print("loading settings")
        self.restoreWindow()

    
    def restoreWindow(self):
        settings = QtCore.QSettings()
        if settings.value("window_state"):
            self.restoreState(settings.value("window_state"))
        if settings.value("plotsplitter_state"):
            self.plotSplitter.restoreState(settings.value("plotsplitter_state"))
        if settings.value("window_geometry"):
            self.restoreGeometry(settings.value("window_geometry"))

    def saveWindowState(self):
        settings = QtCore.QSettings()
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
        settings.setValue("plotsplitter_state", self.plotSplitter.saveState())




if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS")
    app.setStyle("cleanlooks")
    app.setStyleSheet("QMainWindow {background: 'white';}")


    wnd = FANS_MAIN_WINDOW()
    wnd.show()
    

    sys.exit(app.exec_())
 

