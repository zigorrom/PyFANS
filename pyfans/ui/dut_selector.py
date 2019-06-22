from PyQt4 import uic, QtCore, QtGui
from functools import partial
from pyfans.ui.forms.UI_TransistorSelector import Ui_TransistorSelector

# dutSelectorViewBase, dutSelectorViewForm = uic.loadUiType("UI/UI_TransistorSelector.ui")
# class DUT_Selector(dutSelectorViewBase, dutSelectorViewForm):
class DUT_Selector(QtGui.QDialog, Ui_TransistorSelector):
    MAX_DUT_COUNT = 32
    DUT_NAME_FORMAT = "DUT#{0}"
    BUTTON_NAME_FORMAT = "pushButton_{0}"
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi()
        self._selected_dut_list = list()
        arglen = len(args)
        if arglen==1:
            self.selected_dut_list = args[0]
        else:
            self.selected_dut_list = args
        # self._selected_dut_list = list(range(0,self.MAX_DUT_COUNT))

    def setupUi(self):
        super().setupUi(self)
        nameFormat = self.BUTTON_NAME_FORMAT
        for i in range(self.MAX_DUT_COUNT):
            ipp = i+1
            name = nameFormat.format(ipp)
            button = getattr(self, name)
            button.setText(str(ipp))
            button.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
            button.toggled.connect(partial(self.on_button_toggled, sender=button))

    @property
    def selected_dut_list(self):
        return self._selected_dut_list

    @selected_dut_list.setter
    def selected_dut_list(self, dut_list):
        # self._selected_dut_list = dut_list
        # self.setStateForList(self.selected_dut_list, True)
        self.setStateForList(dut_list, True)

    def on_button_toggled(self, state, sender):
        dut_number = int(sender.text())
        print("state {0} was set for button {1}".format(state,dut_number))
        
        if state == True:
            if dut_number in self.selected_dut_list:
                return
            else:
                self.selected_dut_list.append(dut_number)
                self.ui_selected_dut_list.addItem(self.DUT_NAME_FORMAT.format(dut_number))

        else:
            if dut_number in self.selected_dut_list:
                self.selected_dut_list.remove(dut_number)
                name = self.DUT_NAME_FORMAT.format(dut_number)
                item = self.ui_selected_dut_list.findItems(name, QtCore.Qt.MatchExactly)[0]
                row = self.ui_selected_dut_list.row(item)
                self.ui_selected_dut_list.takeItem(row)
            else:
                return

        print(self.selected_dut_list)


    def initialize_state(self):
        pass

    def setStateForList(self, dut_list, state):
        nameFormat = self.BUTTON_NAME_FORMAT
        for i in dut_list:
            name = nameFormat.format(i)
            button = getattr(self, name)
            button.setChecked(state)
            # self.on_button_toggled(True, button)

    def setStateForAll(self, state):
        nameFormat  = self.BUTTON_NAME_FORMAT
        for i in range(self.MAX_DUT_COUNT):
            ipp = i+1
            name = nameFormat.format(ipp)
            button = getattr(self, name)
            button.setChecked(state)

    @QtCore.pyqtSlot()
    def on_ui_remove_all_dut_clicked(self):
        self.setStateForAll(False)

    @QtCore.pyqtSlot()
    def on_ui_remove_dut_clicked(self):
        selectedItems = self.ui_selected_dut_list.selectedItems()
        for item in selectedItems:
            text = item.text()
            prefix, n = text.split("#", 1)
            name = self.BUTTON_NAME_FORMAT.format(n)
            button = getattr(self, name)
            button.setChecked(False)

    
    @QtCore.pyqtSlot()
    def on_ui_select_all_dut_clicked(self):
        self.setStateForAll(True)

    

if __name__== "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    wnd = DUT_Selector([1,2,3,4,7])
    wnd.show()
    sys.exit(app.exec_())