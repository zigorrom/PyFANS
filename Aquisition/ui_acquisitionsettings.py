# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_acquisitionsettings.ui'
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

class Ui_AcquisitionSettings(object):
    def setupUi(self, AcquisitionSettings):
        AcquisitionSettings.setObjectName(_fromUtf8("AcquisitionSettings"))
        AcquisitionSettings.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(AcquisitionSettings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(AcquisitionSettings)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)
        self.checkBox = QtGui.QCheckBox(AcquisitionSettings)
        self.checkBox.setText(_fromUtf8(""))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 4, 2, 1, 1)
        self.label_3 = QtGui.QLabel(AcquisitionSettings)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 2)
        self.label_7 = QtGui.QLabel(AcquisitionSettings)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 2)
        self.spinBox = QtGui.QSpinBox(AcquisitionSettings)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.gridLayout.addWidget(self.spinBox, 2, 2, 1, 1)
        self.comboBox_3 = QtGui.QComboBox(AcquisitionSettings)
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.gridLayout.addWidget(self.comboBox_3, 7, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(AcquisitionSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.label_6 = QtGui.QLabel(AcquisitionSettings)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 2)
        self.label_5 = QtGui.QLabel(AcquisitionSettings)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 2)
        self.label = QtGui.QLabel(AcquisitionSettings)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 2)
        self.comboBox_2 = QtGui.QComboBox(AcquisitionSettings)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_2, 6, 2, 1, 1)
        self.comboBox = QtGui.QComboBox(AcquisitionSettings)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox, 5, 2, 1, 1)
        self.spinBox_2 = QtGui.QSpinBox(AcquisitionSettings)
        self.spinBox_2.setObjectName(_fromUtf8("spinBox_2"))
        self.gridLayout.addWidget(self.spinBox_2, 3, 2, 1, 1)
        self.lineEdit = QtGui.QLineEdit(AcquisitionSettings)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 2, 1, 1)
        self.label_4 = QtGui.QLabel(AcquisitionSettings)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 2)
        self.line = QtGui.QFrame(AcquisitionSettings)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 3)

        self.retranslateUi(AcquisitionSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AcquisitionSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AcquisitionSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(AcquisitionSettings)

    def retranslateUi(self, AcquisitionSettings):
        AcquisitionSettings.setWindowTitle(_translate("AcquisitionSettings", "Acquisition settings", None))
        self.label_2.setText(_translate("AcquisitionSettings", "Points per shot", None))
        self.label_3.setText(_translate("AcquisitionSettings", "Acquisition channel", None))
        self.label_7.setText(_translate("AcquisitionSettings", "Filter cutoff", None))
        self.label_6.setText(_translate("AcquisitionSettings", "Filter gain", None))
        self.label_5.setText(_translate("AcquisitionSettings", "PGA", None))
        self.label.setText(_translate("AcquisitionSettings", "SampleRate", None))
        self.comboBox_2.setItemText(0, _translate("AcquisitionSettings", "1", None))
        self.comboBox_2.setItemText(1, _translate("AcquisitionSettings", "10", None))
        self.comboBox_2.setItemText(2, _translate("AcquisitionSettings", "100", None))
        self.comboBox.setItemText(0, _translate("AcquisitionSettings", "1", None))
        self.comboBox.setItemText(1, _translate("AcquisitionSettings", "10", None))
        self.comboBox.setItemText(2, _translate("AcquisitionSettings", "100", None))
        self.label_4.setText(_translate("AcquisitionSettings", "Homemade amplifier", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    AcquisitionSettings = QtGui.QDialog()
    ui = Ui_AcquisitionSettings()
    ui.setupUi(AcquisitionSettings)
    AcquisitionSettings.show()
    sys.exit(app.exec_())

