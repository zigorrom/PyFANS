# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_powersupplysettings.ui'
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

class Ui_PowerSupplySettings(object):
    def setupUi(self, PowerSupplySettings):
        PowerSupplySettings.setObjectName(_fromUtf8("PowerSupplySettings"))
        PowerSupplySettings.resize(686, 522)
        self.gridLayout = QtGui.QGridLayout(PowerSupplySettings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(PowerSupplySettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.groupBox_3 = QtGui.QGroupBox(PowerSupplySettings)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 3, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 1, 1, 1)
        self.DrainCurrentMeasured = QtGui.QLineEdit(self.groupBox_3)
        self.DrainCurrentMeasured.setObjectName(_fromUtf8("DrainCurrentMeasured"))
        self.gridLayout_2.addWidget(self.DrainCurrentMeasured, 2, 2, 1, 1)
        self.RloadSet = QtGui.QSpinBox(self.groupBox_3)
        self.RloadSet.setObjectName(_fromUtf8("RloadSet"))
        self.gridLayout_2.addWidget(self.RloadSet, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 2, 1, 1, 1)
        self.RsampleMeasured = QtGui.QLineEdit(self.groupBox_3)
        self.RsampleMeasured.setObjectName(_fromUtf8("RsampleMeasured"))
        self.gridLayout_2.addWidget(self.RsampleMeasured, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(PowerSupplySettings)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.drainsourcevoltage = QtGui.QLCDNumber(self.groupBox)
        self.drainsourcevoltage.setFrameShape(QtGui.QFrame.Box)
        self.drainsourcevoltage.setFrameShadow(QtGui.QFrame.Raised)
        self.drainsourcevoltage.setLineWidth(2)
        self.drainsourcevoltage.setDigitCount(12)
        self.drainsourcevoltage.setObjectName(_fromUtf8("drainsourcevoltage"))
        self.verticalLayout.addWidget(self.drainsourcevoltage)
        self.DrainSourceVoltageSet = QtGui.QDial(self.groupBox)
        self.DrainSourceVoltageSet.setMinimum(-10)
        self.DrainSourceVoltageSet.setMaximum(10)
        self.DrainSourceVoltageSet.setSingleStep(11)
        self.DrainSourceVoltageSet.setObjectName(_fromUtf8("DrainSourceVoltageSet"))
        self.verticalLayout.addWidget(self.DrainSourceVoltageSet)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(PowerSupplySettings)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gatevoltage = QtGui.QLCDNumber(self.groupBox_2)
        self.gatevoltage.setLineWidth(2)
        self.gatevoltage.setDigitCount(12)
        self.gatevoltage.setProperty("value", 0.123123)
        self.gatevoltage.setObjectName(_fromUtf8("gatevoltage"))
        self.verticalLayout_2.addWidget(self.gatevoltage)
        self.GateVoltageSet = QtGui.QDial(self.groupBox_2)
        self.GateVoltageSet.setObjectName(_fromUtf8("GateVoltageSet"))
        self.verticalLayout_2.addWidget(self.GateVoltageSet)
        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)

        self.retranslateUi(PowerSupplySettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PowerSupplySettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PowerSupplySettings.reject)
        QtCore.QMetaObject.connectSlotsByName(PowerSupplySettings)

    def retranslateUi(self, PowerSupplySettings):
        PowerSupplySettings.setWindowTitle(_translate("PowerSupplySettings", "Power Supply", None))
        self.groupBox_3.setTitle(_translate("PowerSupplySettings", "Measured data", None))
        self.label_3.setText(_translate("PowerSupplySettings", "R sample", None))
        self.label.setText(_translate("PowerSupplySettings", "R load", None))
        self.label_2.setText(_translate("PowerSupplySettings", "Drain Current", None))
        self.groupBox.setTitle(_translate("PowerSupplySettings", "Drain-Source Voltage", None))
        self.groupBox_2.setTitle(_translate("PowerSupplySettings", "Gate Voltage", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PowerSupplySettings = QtGui.QDialog()
    ui = Ui_PowerSupplySettings()
    ui.setupUi(PowerSupplySettings)
    PowerSupplySettings.show()
    sys.exit(app.exec_())

