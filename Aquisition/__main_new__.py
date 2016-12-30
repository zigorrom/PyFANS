from PyQt4 import QtCore, QtGui, uic
import sys

from plot import SpectrumPlotWidget, WaterfallPlotWidget
from data import *
from fans_controller import *






output_settings_form_name = "ui_outputsettings.ui"
output_settings_base, output_settings_form = uic.loadUiType(output_settings_form_name)

class OutputSettings(output_settings_base, output_settings_form):
    def __init__(self,parent = None):
        super(output_settings_base,self).__init__(parent)
        self.setupUi(self)
##        self.
    def accept(self):
        print("outp settings accepted")
        QtGui.QDialog.accept(self)


acquisition_settings_form_name = "ui_acquisitionsettings.ui"
acquisition_settings_base,acquisition_settings_form = uic.loadUiType(acquisition_settings_form_name)

class AcquisitionSettings(acquisition_settings_base, acquisition_settings_form):
    def __init__(self,parent = None):
        super(acquisition_settings_base,self).__init__(parent)
        self.setupUi(self)

    def accept(self):
        print("adc settings accepted")
        QtGui.QDialog.accept(self)


channel_settings_form_name = "ui_channelsettings.ui"
channel_settings_base, channel_settings_form = uic.loadUiType(channel_settings_form_name)


class ChannelSettings(channel_settings_base, channel_settings_form):
    def __init__(self,parent = None):
        super(channel_settings_base,self).__init__(parent)
        self.setupUi(self)

    def accept(self):
        print("channel settings accepted")
        QtGui.QDialog.accept(self)


power_supply_form_name = "ui_powersupplysettings.ui"
power_supply_settings_base, power_supply_settings_form = uic.loadUiType(power_supply_form_name)

class PowerSupplySettings(power_supply_settings_base, power_supply_settings_form):
    def __init__(self, parent = None):
        super(power_supply_settings_base,self).__init__(parent)
        self.setupUi(self)

    def accept(self):
        print("power settings accepted")
        QtGui.QDialog.accept(self)


main_form_name = "ui_mainform.ui"
base, form = uic.loadUiType(main_form_name)

class FANS_main_window(base,form):
    def __init__(self,parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        self.load_settings()
        self.setup_daq()

    def setup_daq(self):
        self.spectrumPlotWidget = SpectrumPlotWidget(self.noisePlot)
        self.sample_rate = 500000
        self.points_per_shot = 50000
        self.data_storage = DataHandler(sample_rate=self.sample_rate,points_per_shot = self.points_per_shot)
        self.data_storage.data_updated.connect(self.spectrumPlotWidget.update_plot)
        self.data_storage.average_updated.connect(self.spectrumPlotWidget.update_average)
        self.data_storage.peak_hold_max_updated.connect(self.spectrumPlotWidget.update_peak_hold_max)
        self.data_storage.peak_hold_min_updated.connect(self.spectrumPlotWidget.update_peak_hold_min)

##        self.fans_controller = FANScontroller("ADC",self.data_storage)
##        self.fans_controller.init_acquisition(self.sample_rate,self.points_per_shot,[AI_1,AI_2,AI_3,AI_4])

    def load_settings(self):
        pass

    def closeEvent(self,event):
        print("closing")
        self.save_settings()
## FILE MENU ITEM
    
    @QtCore.pyqtSlot()
    def on_actionWorkingFolder_triggered(self):
        print("working folder clicked")

    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self):
        print("exit pressed")
        
## SETTINGS MENU ITEM
    
    @QtCore.pyqtSlot()
    def on_actionSaveAll_2_triggered(self):
        print("save all")

    @QtCore.pyqtSlot()
    def on_actionLoadAll_triggered(self):
        print("load all")

    @QtCore.pyqtSlot()
    def on_actionChannelSettings_triggered(self):
        dialog = ChannelSettings(self)
        if dialog.exec_():
           print("channel settings")


    @QtCore.pyqtSlot()
    def on_actionOutputSettings_triggered(self):
        dialog = OutputSettings(self)
        if dialog.exec_():
            print("output settings")    
        

    @QtCore.pyqtSlot()  
    def on_actionAcquisitionSettings_triggered(self):
        dialog = AcquisitionSettings(self)
        if dialog.exec_():
            print("acquisition settings")

    @QtCore.pyqtSlot()  
    def on_actionPowerSupplySettings_triggered(self):
        dialog = PowerSupplySettings(self)
        if dialog.exec_():
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
        self.fans_controller.start_acquisition()
        
    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        print("start")
        self.start()

    def stop(self):
        self.fans_controller.stop_acquisition()

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        print("stop")
        self.stop()

    @QtCore.pyqtSlot()
    def on_singleShotButton_clicked(self):
        print("single shot")


    @QtCore.pyqtSlot()
    def on_AddFrequencyRangeButton_clicked(self):
        print("add frequency range")

    @QtCore.pyqtSlot()
    def on_DeleteFrequencyRangeButton_clicked(self):
        print("delete frequency range")


    def save_settings(self):
        print("savng settings")
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

    wnd = FANS_main_window()
    wnd.show()

    sys.exit(app.exec_())
