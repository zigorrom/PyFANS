import sys, signal, time

from PyQt4 import QtCore, QtGui

from ui_mainform import Ui_mainWindow
from ui_acquisitionsettings import Ui_AcquisitionSettings
from ui_channelsettings import Ui_ChannelSettings
from ui_outputsettings import Ui_OutputSettings
from ui_powersupplysettings import Ui_PowerSupplySettings

from plot import SpectrumPlotWidget, WaterfallPlotWidget
from data import *
from fans_controller import *


class OutputSettings(QtGui.QDialog, Ui_OutputSettings):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.setupUi(self)
##        self.
    def accept(self):
        print("outp settings accepted")
        QtGui.QDialog.accept(self)
        
class AcquisitionSettings(QtGui.QDialog, Ui_AcquisitionSettings):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.setupUi(self)

    def accept(self):
        print("adc settings accepted")
        QtGui.QDialog.accept(self)

class ChannelSettings(QtGui.QDialog, Ui_ChannelSettings):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.setupUi(self)

    def accept(self):
        print("channel settings accepted")
        QtGui.QDialog.accept(self)

class PowerSupplySettings(QtGui.QDialog, Ui_PowerSupplySettings):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

    def accept(self):
        print("power settings accepted")
        QtGui.QDialog.accept(self)


class fansMainWindow(QtGui.QMainWindow, Ui_mainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setupDAQ()
##        print(self.noisePlot)
        
        
        self.load_settings()
        self.show()

    def closeEvent(self,event):
        print("closing")
        self.save_settings()

    def setupDAQ(self):
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
            
    

def main():
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("FZJ")
    app.setOrganizationDomain("fz-juelich.de")
    app.setApplicationName("FANS")
    window = fansMainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
