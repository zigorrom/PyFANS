# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_VoltageView.ui'
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

class Ui_VoltageView(object):
    def setupUi(self, VoltageView):
        VoltageView.setObjectName(_fromUtf8("VoltageView"))
        VoltageView.resize(250, 93)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VoltageView.sizePolicy().hasHeightForWidth())
        VoltageView.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(VoltageView)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.main_layout = QtGui.QHBoxLayout()
        self.main_layout.setObjectName(_fromUtf8("main_layout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(VoltageView)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.ui_drain_source_voltage = QtGui.QLineEdit(VoltageView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_drain_source_voltage.sizePolicy().hasHeightForWidth())
        self.ui_drain_source_voltage.setSizePolicy(sizePolicy)
        self.ui_drain_source_voltage.setReadOnly(True)
        self.ui_drain_source_voltage.setObjectName(_fromUtf8("ui_drain_source_voltage"))
        self.horizontalLayout.addWidget(self.ui_drain_source_voltage)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(VoltageView)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.ui_gate_source_voltage = QtGui.QLineEdit(VoltageView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_gate_source_voltage.sizePolicy().hasHeightForWidth())
        self.ui_gate_source_voltage.setSizePolicy(sizePolicy)
        self.ui_gate_source_voltage.setReadOnly(True)
        self.ui_gate_source_voltage.setObjectName(_fromUtf8("ui_gate_source_voltage"))
        self.horizontalLayout_2.addWidget(self.ui_gate_source_voltage)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.main_layout.addLayout(self.verticalLayout)
        self.ui_status_led = LedWidget(VoltageView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_status_led.sizePolicy().hasHeightForWidth())
        self.ui_status_led.setSizePolicy(sizePolicy)
        self.ui_status_led.setMinimumSize(QtCore.QSize(50, 50))
        self.ui_status_led.setBaseSize(QtCore.QSize(100, 100))
        self.ui_status_led.setObjectName(_fromUtf8("ui_status_led"))
        self.main_layout.addWidget(self.ui_status_led)
        self.verticalLayout_2.addLayout(self.main_layout)
        spacerItem = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)

        self.retranslateUi(VoltageView)
        QtCore.QMetaObject.connectSlotsByName(VoltageView)

    def retranslateUi(self, VoltageView):
        VoltageView.setWindowTitle(_translate("VoltageView", "Voltage View", None))
        self.label.setText(_translate("VoltageView", "Vds", None))
        self.label_2.setText(_translate("VoltageView", "Vgs", None))

from .led_widget import LedWidget
