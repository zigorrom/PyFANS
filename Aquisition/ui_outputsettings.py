# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_outputsettings.ui'
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

class Ui_OutputSettings(object):
    def setupUi(self, OutputSettings):
        OutputSettings.setObjectName(_fromUtf8("OutputSettings"))
        OutputSettings.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(OutputSettings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(OutputSettings)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(OutputSettings)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.label_5 = QtGui.QLabel(OutputSettings)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.enabled_out1 = QtGui.QCheckBox(OutputSettings)
        self.enabled_out1.setObjectName(_fromUtf8("enabled_out1"))
        self.gridLayout.addWidget(self.enabled_out1, 1, 1, 1, 1)
        self.enabled_out2 = QtGui.QCheckBox(OutputSettings)
        self.enabled_out2.setObjectName(_fromUtf8("enabled_out2"))
        self.gridLayout.addWidget(self.enabled_out2, 1, 2, 1, 1)
        self.label_3 = QtGui.QLabel(OutputSettings)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.pin_out1 = QtGui.QComboBox(OutputSettings)
        self.pin_out1.setObjectName(_fromUtf8("pin_out1"))
        self.gridLayout.addWidget(self.pin_out1, 2, 1, 1, 1)
        self.pin_out2 = QtGui.QComboBox(OutputSettings)
        self.pin_out2.setObjectName(_fromUtf8("pin_out2"))
        self.gridLayout.addWidget(self.pin_out2, 2, 2, 1, 1)
        self.label_4 = QtGui.QLabel(OutputSettings)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.function_out1 = QtGui.QComboBox(OutputSettings)
        self.function_out1.setObjectName(_fromUtf8("function_out1"))
        self.gridLayout.addWidget(self.function_out1, 3, 1, 1, 1)
        self.function_out2 = QtGui.QComboBox(OutputSettings)
        self.function_out2.setObjectName(_fromUtf8("function_out2"))
        self.gridLayout.addWidget(self.function_out2, 3, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(OutputSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 132, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)

        self.retranslateUi(OutputSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OutputSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OutputSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(OutputSettings)

    def retranslateUi(self, OutputSettings):
        OutputSettings.setWindowTitle(_translate("OutputSettings", "Output Settings", None))
        self.label.setText(_translate("OutputSettings", "Output 1", None))
        self.label_2.setText(_translate("OutputSettings", "Output 2", None))
        self.label_5.setText(_translate("OutputSettings", "Enabled", None))
        self.enabled_out1.setText(_translate("OutputSettings", "CheckBox", None))
        self.enabled_out2.setText(_translate("OutputSettings", "CheckBox", None))
        self.label_3.setText(_translate("OutputSettings", "Output pin", None))
        self.label_4.setText(_translate("OutputSettings", "Function", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    OutputSettings = QtGui.QDialog()
    ui = Ui_OutputSettings()
    ui.setupUi(OutputSettings)
    OutputSettings.show()
    sys.exit(app.exec_())

