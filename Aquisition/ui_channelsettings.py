# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_channelsettings.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ui_channelsettings(object):
    def setupUi(self, ui_channelsettings):
        ui_channelsettings.setObjectName(_fromUtf8("ui_channelsettings"))
        ui_channelsettings.resize(500, 185)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ui_channelsettings.sizePolicy().hasHeightForWidth())
        ui_channelsettings.setSizePolicy(sizePolicy)
        ui_channelsettings.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(ui_channelsettings)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.range_in1 = QtGui.QComboBox(ui_channelsettings)
        self.range_in1.setObjectName(_fromUtf8("range_in1"))
        self.range_in1.addItem(_fromUtf8(""))
        self.range_in1.addItem(_fromUtf8(""))
        self.range_in1.addItem(_fromUtf8(""))
        self.range_in1.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.range_in1, 2, 1, 1, 1)
        self.enabled_in2 = QtGui.QCheckBox(ui_channelsettings)
        self.enabled_in2.setText(_fromUtf8(""))
        self.enabled_in2.setObjectName(_fromUtf8("enabled_in2"))
        self.gridLayout.addWidget(self.enabled_in2, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(ui_channelsettings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 4, 1, 1)
        self.label_3 = QtGui.QLabel(ui_channelsettings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 3, 1, 1)
        self.enabled_in1 = QtGui.QCheckBox(ui_channelsettings)
        self.enabled_in1.setText(_fromUtf8(""))
        self.enabled_in1.setObjectName(_fromUtf8("enabled_in1"))
        self.gridLayout.addWidget(self.enabled_in1, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(ui_channelsettings)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.label_7 = QtGui.QLabel(ui_channelsettings)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.label_8 = QtGui.QLabel(ui_channelsettings)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(ui_channelsettings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.enabled_in4 = QtGui.QCheckBox(ui_channelsettings)
        self.enabled_in4.setText(_fromUtf8(""))
        self.enabled_in4.setObjectName(_fromUtf8("enabled_in4"))
        self.gridLayout.addWidget(self.enabled_in4, 1, 4, 1, 1)
        self.enabled_in3 = QtGui.QCheckBox(ui_channelsettings)
        self.enabled_in3.setText(_fromUtf8(""))
        self.enabled_in3.setObjectName(_fromUtf8("enabled_in3"))
        self.gridLayout.addWidget(self.enabled_in3, 1, 3, 1, 1)
        self.label = QtGui.QLabel(ui_channelsettings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_5 = QtGui.QLabel(ui_channelsettings)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.function_in1 = QtGui.QComboBox(ui_channelsettings)
        self.function_in1.setObjectName(_fromUtf8("function_in1"))
        self.function_in1.addItem(_fromUtf8(""))
        self.function_in1.addItem(_fromUtf8(""))
        self.function_in1.addItem(_fromUtf8(""))
        self.function_in1.addItem(_fromUtf8(""))
        self.function_in1.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.function_in1, 4, 1, 1, 1)
        self.polarity_in4 = QtGui.QComboBox(ui_channelsettings)
        self.polarity_in4.setObjectName(_fromUtf8("polarity_in4"))
        self.polarity_in4.addItem(_fromUtf8(""))
        self.polarity_in4.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.polarity_in4, 3, 4, 1, 1)
        self.range_in3 = QtGui.QComboBox(ui_channelsettings)
        self.range_in3.setObjectName(_fromUtf8("range_in3"))
        self.range_in3.addItem(_fromUtf8(""))
        self.range_in3.addItem(_fromUtf8(""))
        self.range_in3.addItem(_fromUtf8(""))
        self.range_in3.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.range_in3, 2, 3, 1, 1)
        self.range_in2 = QtGui.QComboBox(ui_channelsettings)
        self.range_in2.setObjectName(_fromUtf8("range_in2"))
        self.range_in2.addItem(_fromUtf8(""))
        self.range_in2.addItem(_fromUtf8(""))
        self.range_in2.addItem(_fromUtf8(""))
        self.range_in2.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.range_in2, 2, 2, 1, 1)
        self.range_in4 = QtGui.QComboBox(ui_channelsettings)
        self.range_in4.setObjectName(_fromUtf8("range_in4"))
        self.range_in4.addItem(_fromUtf8(""))
        self.range_in4.addItem(_fromUtf8(""))
        self.range_in4.addItem(_fromUtf8(""))
        self.range_in4.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.range_in4, 2, 4, 1, 1)
        self.polarity_in1 = QtGui.QComboBox(ui_channelsettings)
        self.polarity_in1.setObjectName(_fromUtf8("polarity_in1"))
        self.polarity_in1.addItem(_fromUtf8(""))
        self.polarity_in1.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.polarity_in1, 3, 1, 1, 1)
        self.polarity_in3 = QtGui.QComboBox(ui_channelsettings)
        self.polarity_in3.setObjectName(_fromUtf8("polarity_in3"))
        self.polarity_in3.addItem(_fromUtf8(""))
        self.polarity_in3.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.polarity_in3, 3, 3, 1, 1)
        self.polarity_in2 = QtGui.QComboBox(ui_channelsettings)
        self.polarity_in2.setObjectName(_fromUtf8("polarity_in2"))
        self.polarity_in2.addItem(_fromUtf8(""))
        self.polarity_in2.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.polarity_in2, 3, 2, 1, 1)
        self.function_in2 = QtGui.QComboBox(ui_channelsettings)
        self.function_in2.setObjectName(_fromUtf8("function_in2"))
        self.function_in2.addItem(_fromUtf8(""))
        self.function_in2.addItem(_fromUtf8(""))
        self.function_in2.addItem(_fromUtf8(""))
        self.function_in2.addItem(_fromUtf8(""))
        self.function_in2.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.function_in2, 4, 2, 1, 1)
        self.function_in3 = QtGui.QComboBox(ui_channelsettings)
        self.function_in3.setObjectName(_fromUtf8("function_in3"))
        self.function_in3.addItem(_fromUtf8(""))
        self.function_in3.addItem(_fromUtf8(""))
        self.function_in3.addItem(_fromUtf8(""))
        self.function_in3.addItem(_fromUtf8(""))
        self.function_in3.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.function_in3, 4, 3, 1, 1)
        self.function_in4 = QtGui.QComboBox(ui_channelsettings)
        self.function_in4.setObjectName(_fromUtf8("function_in4"))
        self.function_in4.addItem(_fromUtf8(""))
        self.function_in4.addItem(_fromUtf8(""))
        self.function_in4.addItem(_fromUtf8(""))
        self.function_in4.addItem(_fromUtf8(""))
        self.function_in4.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.function_in4, 4, 4, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ui_channelsettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ui_channelsettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ui_channelsettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ui_channelsettings.reject)
        QtCore.QMetaObject.connectSlotsByName(ui_channelsettings)

    def retranslateUi(self, ui_channelsettings):
        ui_channelsettings.setWindowTitle(_translate("ui_channelsettings", "Dialog", None))
        self.range_in1.setItemText(0, _translate("ui_channelsettings", "1.25 V", None))
        self.range_in1.setItemText(1, _translate("ui_channelsettings", "2.5 V", None))
        self.range_in1.setItemText(2, _translate("ui_channelsettings", "5 V", None))
        self.range_in1.setItemText(3, _translate("ui_channelsettings", "10 V", None))
        self.label_4.setText(_translate("ui_channelsettings", "Input 4", None))
        self.label_3.setText(_translate("ui_channelsettings", "Input 3", None))
        self.label_6.setText(_translate("ui_channelsettings", "Range", None))
        self.label_7.setText(_translate("ui_channelsettings", "Polarity", None))
        self.label_8.setText(_translate("ui_channelsettings", "Function", None))
        self.label_2.setText(_translate("ui_channelsettings", "Input 2", None))
        self.label.setText(_translate("ui_channelsettings", "Input 1", None))
        self.label_5.setText(_translate("ui_channelsettings", "Enabled", None))
        self.function_in1.setItemText(0, _translate("ui_channelsettings", "None", None))
        self.function_in1.setItemText(1, _translate("ui_channelsettings", "Vds", None))
        self.function_in1.setItemText(2, _translate("ui_channelsettings", "Vlg", None))
        self.function_in1.setItemText(3, _translate("ui_channelsettings", "Vbg", None))
        self.function_in1.setItemText(4, _translate("ui_channelsettings", "Vmain", None))
        self.polarity_in4.setItemText(0, _translate("ui_channelsettings", "Unipolar", None))
        self.polarity_in4.setItemText(1, _translate("ui_channelsettings", "Bipolar", None))
        self.range_in3.setItemText(0, _translate("ui_channelsettings", "1.25 V", None))
        self.range_in3.setItemText(1, _translate("ui_channelsettings", "2.5 V", None))
        self.range_in3.setItemText(2, _translate("ui_channelsettings", "5 V", None))
        self.range_in3.setItemText(3, _translate("ui_channelsettings", "10 V", None))
        self.range_in2.setItemText(0, _translate("ui_channelsettings", "1.25 V", None))
        self.range_in2.setItemText(1, _translate("ui_channelsettings", "2.5 V", None))
        self.range_in2.setItemText(2, _translate("ui_channelsettings", "5 V", None))
        self.range_in2.setItemText(3, _translate("ui_channelsettings", "10 V", None))
        self.range_in4.setItemText(0, _translate("ui_channelsettings", "1.25 V", None))
        self.range_in4.setItemText(1, _translate("ui_channelsettings", "2.5 V", None))
        self.range_in4.setItemText(2, _translate("ui_channelsettings", "5 V", None))
        self.range_in4.setItemText(3, _translate("ui_channelsettings", "10 V", None))
        self.polarity_in1.setItemText(0, _translate("ui_channelsettings", "Unipolar", None))
        self.polarity_in1.setItemText(1, _translate("ui_channelsettings", "Bipolar", None))
        self.polarity_in3.setItemText(0, _translate("ui_channelsettings", "Unipolar", None))
        self.polarity_in3.setItemText(1, _translate("ui_channelsettings", "Bipolar", None))
        self.polarity_in2.setItemText(0, _translate("ui_channelsettings", "Unipolar", None))
        self.polarity_in2.setItemText(1, _translate("ui_channelsettings", "Bipolar", None))
        self.function_in2.setItemText(0, _translate("ui_channelsettings", "None", None))
        self.function_in2.setItemText(1, _translate("ui_channelsettings", "Vds", None))
        self.function_in2.setItemText(2, _translate("ui_channelsettings", "Vlg", None))
        self.function_in2.setItemText(3, _translate("ui_channelsettings", "Vbg", None))
        self.function_in2.setItemText(4, _translate("ui_channelsettings", "Vmain", None))
        self.function_in3.setItemText(0, _translate("ui_channelsettings", "None", None))
        self.function_in3.setItemText(1, _translate("ui_channelsettings", "Vds", None))
        self.function_in3.setItemText(2, _translate("ui_channelsettings", "Vlg", None))
        self.function_in3.setItemText(3, _translate("ui_channelsettings", "Vbg", None))
        self.function_in3.setItemText(4, _translate("ui_channelsettings", "Vmain", None))
        self.function_in4.setItemText(0, _translate("ui_channelsettings", "None", None))
        self.function_in4.setItemText(1, _translate("ui_channelsettings", "Vds", None))
        self.function_in4.setItemText(2, _translate("ui_channelsettings", "Vlg", None))
        self.function_in4.setItemText(3, _translate("ui_channelsettings", "Vbg", None))
        self.function_in4.setItemText(4, _translate("ui_channelsettings", "Vmain", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui_channelsettings = QtGui.QDialog()
    ui = Ui_ui_channelsettings()
    ui.setupUi(ui_channelsettings)
    ui_channelsettings.show()
    sys.exit(app.exec_())

