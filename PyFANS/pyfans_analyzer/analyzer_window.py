import os
import sys
import numpy as np

from PyQt4 import QtCore, QtGui, uic

import pyfans.plot as plt
import pyfans.utils.ui_helper as uih
from pyfans_analyzer.analyzer_model import AnalyzerModel

main_view_base, main_view = uic.loadUiType("UI/UI_Analyzer.ui")

class MainView(main_view_base, main_view, uih.DataContextWidget):
    sigOpenFileTriggered = QtCore.pyqtSignal(str)
    sigOpenWorkingFolderTriggered = QtCore.pyqtSignal()
    sigSaveFileTriggered = QtCore.pyqtSignal()
    sigExportTriggered = QtCore.pyqtSignal()
    sigNextTriggered = QtCore.pyqtSignal()
    sigPrevTriggered = QtCore.pyqtSignal()
    sigCropTriggered = QtCore.pyqtSignal()
    sigCropUndoTriggered = QtCore.pyqtSignal()
    sigFlickerResetTriggered = QtCore.pyqtSignal()
    sigAddGRTriggered = QtCore.pyqtSignal()
    sigAddGRAtPosTriggered = QtCore.pyqtSignal(object)
    sigResetGRTriggered = QtCore.pyqtSignal()
    sigRemoveGRTriggered = QtCore.pyqtSignal()
    sigRemoveAllGRTriggered = QtCore.pyqtSignal()
    sigFitTriggered = QtCore.pyqtSignal()
    sigSelectedGRChanged = QtCore.pyqtSignal()
    sigAppClosing = QtCore.pyqtSignal()
    sigOpenPlotterTriggered = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setupBinding()  
        # self.awaiting_for_command = False      

    def setupUi(self):
        super().setupUi(self)
        self._spectrumPlotWidget = plt.SpectrumPlotWidget(self.ui_plot, {})
        self.status_label = QtGui.QLabel(self)
        self.statusbar.addPermanentWidget(self.status_label)
        self.mouseClickedEvent = self._spectrumPlotWidget.subscribe_to_mouse_clicked(self.on_mouse_clicked_in_plot_area)
    
    def setupBinding(self):
        sourceObject = None
        self.remove_pickups = uih.Binding(self.ui_remove_pickups_enabled,"checked", sourceObject, "remove_pickups", converter=uih.AssureBoolConverter())
        self.hide_original = uih.Binding(self.ui_hide_original,"checked", sourceObject, "hide_original", converter=uih.AssureBoolConverter())
        
        self.smoothing_enable = uih.Binding(self.ui_smoothing_enabled,"checked", sourceObject, "smoothing_enabled", converter=uih.AssureBoolConverter())
        self.smoothing_winsize = uih.Binding(self.ui_smoothing_winsize,"value", sourceObject, "smoothing_winsize", converter=uih.AssureIntConverter())
        self.cutoff_correction_enabled = uih.Binding(self.ui_cutoff_correction_enabled,"checked", sourceObject, "cutoff_correction", converter=uih.AssureBoolConverter())
        self.cutoff_correction_capacity = uih.Binding(self.ui_cutoff_correction_capacity,"text", sourceObject, "cutoff_correction_capacity", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.multiply_by_frequency = uih.Binding(self.ui_multiply_by_frequency,"checked", sourceObject, "multiply_by_frequency", converter=uih.AssureBoolConverter())
        self.start_crop_frequency = uih.Binding(self.ui_crop_start_frequency,"text", sourceObject, "start_crop_frequency", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.end_crop_frequency = uih.Binding(self.ui_crop_stop_frequency,"text", sourceObject, "end_crop_frequency", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.thermal_enabled = uih.Binding(self.ui_thermal_groupbox,"checked", sourceObject, "thermal_enabled", converter=uih.AssureBoolConverter())
        self.equivalent_resistance = uih.Binding(self.ui_equivalent_resistance,"text", sourceObject, "equivalent_resistance", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.temperature = uih.Binding(self.ui_temperature,"text", sourceObject, "temperature", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.subtractThermalNoise = uih.Binding(self.ui_subtract_thermal_noise,"checked", sourceObject, "subtract_thermal_noise", converter=uih.AssureBoolConverter())
        self.flicker_enabled = uih.Binding(self.ui_flicker_groupbox,"checked", sourceObject, "flicker_enabled", converter=uih.AssureBoolConverter())
        self.flicker_amplitude = uih.Binding(self.ui_flicker_amplitude,"text", sourceObject, "flicker_amplitude", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.flicker_alpha = uih.Binding(self.ui_flicker_alpha,"text", sourceObject, "flicker_alpha", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.flicker_frequency = uih.Binding(self.ui_flicker_frequency,"text", sourceObject, "flicker_frequency", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.gr_enabled = uih.Binding(self.ui_gr_enabled,"checked", sourceObject, "gr_enabled", converter=uih.AssureBoolConverter())
        self.gr_frequency = uih.Binding(self.ui_gr_frequency,"text", sourceObject, "gr_frequency", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.gr_amplitude = uih.Binding(self.ui_gr_amplitude,"text", sourceObject, "gr_amplitude", converter=uih.StringToFloatConverter(),validator=QtGui.QDoubleValidator())
        self.selected_gr_index = uih.Binding(self.ui_gr_listview,"currentRow", sourceObject, "selected_gr_index", converter=uih.AssureIntConverter())
        self.autofit = uih.Binding(self.ui_autofit,"checked", sourceObject, "autofit", converter=uih.AssureBoolConverter())

    @property
    def plotter(self):
        return self._spectrumPlotWidget

    @QtCore.pyqtSlot()
    def on_actionOpen_File_triggered(self):
        print("opening")
        
        msg = QtGui.QMessageBox()
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        measurement_data_filename = os.path.abspath(QtGui.QFileDialog.getOpenFileName(self,caption="Select Measurement Data File"))
        print(measurement_data_filename)
        if os.path.isfile(measurement_data_filename):        
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText("File selected")
            msg.setInformativeText("This is additional information")
            msg.setWindowTitle("File selected")
            msg.setDetailedText(measurement_data_filename)
            self.sigOpenFileTriggered.emit(measurement_data_filename)

        else:
            msg.setIcon(QtGui.QMessageBox.Warning)
            msg.setText("File selection cancelled")
        retval = msg.exec_()

    def on_mouse_clicked_in_plot_area(self, evt):
        # print("mouse clicked event")
        evt=evt[0]
        if evt.button() == QtCore.Qt.LeftButton:
            if evt.double() == True:
                self.on_add_gr_noise_at_position_triggered(evt.scenePos())
                #self.on_ui_add_gr_noise_button_clicked()  
        # elif evt.button() == QtCore.Qt.RightButton:
        #     print("right")
        # if evt.type() == QtCore.QEvent.MouseButtonPress:

        if evt.button() == QtCore.Qt.MidButton:
            self.on_ui_fit_data_button_clicked()
            evt.accept()
        
        # elif evt.type() == QtCore.QEvent.MouseButtonDblClick:
        #     self.on_ui_add_gr_noise_button_clicked()
        

        

    @QtCore.pyqtSlot()
    def on_actionSave_triggered(self):
        self.sigSaveFileTriggered.emit()
    
    @QtCore.pyqtSlot()
    def on_action_export_triggered(self):
        self.sigExportTriggered.emit()

    @QtCore.pyqtSlot()
    def on_actionPrev_triggered(self):
        self.sigPrevTriggered.emit()

    @QtCore.pyqtSlot()
    def on_actionNext_triggered(self):
        self.sigNextTriggered.emit()

    @QtCore.pyqtSlot()
    def on_ui_crop_button_clicked(self):
        self.sigCropTriggered.emit()

    @QtCore.pyqtSlot()
    def on_ui_crop_undo_button_clicked(self):
        self.sigCropUndoTriggered.emit()

    @QtCore.pyqtSlot()
    def on_ui_flicker_noise_reset_button_clicked(self):
        self.sigFlickerResetTriggered.emit()

    @QtCore.pyqtSlot()
    def on_ui_add_gr_noise_button_clicked(self):
        self.sigAddGRTriggered.emit()

    def on_add_gr_noise_at_position_triggered(self,position):
        self.sigAddGRAtPosTriggered.emit(position)

    @QtCore.pyqtSlot()
    def on_ui_remove_gr_noise_button_clicked(self):
        self.sigRemoveGRTriggered.emit()

    @QtCore.pyqtSlot()
    def on_ui_reset_gr_noise_button_clicked(self):
        self.sigResetGRTriggered.emit()

    @QtCore.pyqtSlot()
    def on_ui_fit_data_button_clicked(self):
        self.sigFitTriggered.emit()

    @QtCore.pyqtSlot(int)
    def on_ui_gr_listview_currentRowChanged(self):
        self.sigSelectedGRChanged.emit()

    @QtCore.pyqtSlot()
    def on_action_open_working_folder_triggered(self):
        self.sigOpenWorkingFolderTriggered.emit()

    @QtCore.pyqtSlot()
    def on_action_open_plotter_triggered(self):
        self.sigOpenPlotterTriggered.emit()


    def set_current_analysis_state(self, max_rows, current_row):
        self.status_label.setText("{0} of {1}".format(current_row, max_rows))

    def add_gr_component(self, name):
        items = self.ui_gr_listview.findItems(name, QtCore.Qt.MatchExactly)
        if len(items)>0:
            return
        self.ui_gr_listview.addItem(name)

    def remove_gr_component(self, name):
        pass

    def remove_all_gr_components(self):
        self.ui_gr_listview.clear()

    def remove_gr_name_by_index(self, index):
        item = self.ui_gr_listview.takeItem(index)
        self.selected_gr_index.sourceData -= 1
        return item.text()

    def getSelectedGRitemText(self):
        item = self.ui_gr_listview.currentItem()
        return item.text()

    def getIndexFromGRname(self, name):
        item = self.ui_gr_listview.findItems(name, QtCore.Qt.MatchExactly)[0]
        index = self.ui_gr_listview.row(item)
        return index

    def get_gr_component_count(self):
        return self.ui_gr_listview.count()

    def setModel(self, model):
        pass
    
    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            if event.key() == QtCore.Qt.Key_E:
                self.on_actionNext_triggered()
            elif event.key() == QtCore.Qt.Key_Q:
                self.on_actionPrev_triggered()
            # print("control pressed")
            # self.awaiting_for_command = True


    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            print("control released")
            # self.awaiting_for_command = False
            
    

    def closeEvent(self, event):
        self.sigAppClosing.emit()
        event.accept()

def main():
    import ctypes
    myappid = "fzj.pyfans_analyzer.pyfans_analyzer.21" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS Analyzer")
    app.setStyle("cleanlooks")
    icon_file = "UI/Icons/pyfans_icon2.png"
    
    app_icon = QtGui.QIcon()
    app_icon.addFile(icon_file, QtCore.QSize(16,16))
    app_icon.addFile(icon_file, QtCore.QSize(24,24))
    app_icon.addFile(icon_file, QtCore.QSize(32,32))
    app_icon.addFile(icon_file, QtCore.QSize(48,48))
    app_icon.addFile(icon_file, QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)
    
    main_window = MainView()
    data = AnalyzerModel(analyzer_window=main_window)
    main_window.dataContext = data
    
    
    # main_window.setModel(settings_model)
    main_window.showMaximized()

    sys.exit(app.exec_())