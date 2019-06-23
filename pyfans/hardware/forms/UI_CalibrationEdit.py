# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_CalibrationEdit.ui'
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

class Ui_CalibrationEdit(object):
    def setupUi(self, CalibrationEdit):
        CalibrationEdit.setObjectName(_fromUtf8("CalibrationEdit"))
        CalibrationEdit.setWindowModality(QtCore.Qt.ApplicationModal)
        CalibrationEdit.resize(374, 377)
        self.verticalLayout_2 = QtGui.QVBoxLayout(CalibrationEdit)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(CalibrationEdit)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.checkBox = QtGui.QCheckBox(CalibrationEdit)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.horizontalLayout.addWidget(self.checkBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.widget = QtGui.QWidget(CalibrationEdit)
        self.widget.setEnabled(False)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.ui_frequency_response = QtGui.QPushButton(self.widget)
        self.ui_frequency_response.setObjectName(_fromUtf8("ui_frequency_response"))
        self.gridLayout.addWidget(self.ui_frequency_response, 3, 1, 1, 1)
        self.ui_selected_calibration = QtGui.QComboBox(self.widget)
        self.ui_selected_calibration.setObjectName(_fromUtf8("ui_selected_calibration"))
        self.gridLayout.addWidget(self.ui_selected_calibration, 0, 0, 1, 2)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.ui_homemade_amplifier_gain = QtGui.QLineEdit(self.widget)
        self.ui_homemade_amplifier_gain.setObjectName(_fromUtf8("ui_homemade_amplifier_gain"))
        self.gridLayout.addWidget(self.ui_homemade_amplifier_gain, 2, 1, 1, 1)
        self.ui_calibration_name = QtGui.QLineEdit(self.widget)
        self.ui_calibration_name.setObjectName(_fromUtf8("ui_calibration_name"))
        self.gridLayout.addWidget(self.ui_calibration_name, 1, 1, 1, 1)
        self.ui_freq_resp_fname = QtGui.QLineEdit(self.widget)
        self.ui_freq_resp_fname.setObjectName(_fromUtf8("ui_freq_resp_fname"))
        self.gridLayout.addWidget(self.ui_freq_resp_fname, 4, 0, 1, 2)
        self.label_4 = QtGui.QLabel(self.widget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.ui_amplifier_noise = QtGui.QPushButton(self.widget)
        self.ui_amplifier_noise.setObjectName(_fromUtf8("ui_amplifier_noise"))
        self.gridLayout.addWidget(self.ui_amplifier_noise, 5, 1, 1, 1)
        self.ui_ampl_noise_fname = QtGui.QLineEdit(self.widget)
        self.ui_ampl_noise_fname.setObjectName(_fromUtf8("ui_ampl_noise_fname"))
        self.gridLayout.addWidget(self.ui_ampl_noise_fname, 6, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.widget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.ui_calibration_add = QtGui.QPushButton(CalibrationEdit)
        self.ui_calibration_add.setObjectName(_fromUtf8("ui_calibration_add"))
        self.horizontalLayout_2.addWidget(self.ui_calibration_add)
        self.ui_calibration_remove = QtGui.QPushButton(CalibrationEdit)
        self.ui_calibration_remove.setEnabled(False)
        self.ui_calibration_remove.setObjectName(_fromUtf8("ui_calibration_remove"))
        self.horizontalLayout_2.addWidget(self.ui_calibration_remove)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(CalibrationEdit)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(CalibrationEdit)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CalibrationEdit.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CalibrationEdit.reject)
        QtCore.QObject.connect(self.checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.widget.setEnabled)
        QtCore.QObject.connect(self.checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.ui_calibration_remove.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(CalibrationEdit)

    def retranslateUi(self, CalibrationEdit):
        CalibrationEdit.setWindowTitle(_translate("CalibrationEdit", "Calibration Edit", None))
        self.label.setText(_translate("CalibrationEdit", "Active Calibration:", None))
        self.checkBox.setText(_translate("CalibrationEdit", "Allow Changes", None))
        self.label_5.setText(_translate("CalibrationEdit", "Calibration Name:", None))
        self.label_2.setText(_translate("CalibrationEdit", "Homemade Amplifier Gain:", None))
        self.ui_frequency_response.setText(_translate("CalibrationEdit", "...", None))
        self.label_3.setText(_translate("CalibrationEdit", "Frequency Response:", None))
        self.label_4.setText(_translate("CalibrationEdit", "Amplifier Noise:", None))
        self.ui_amplifier_noise.setText(_translate("CalibrationEdit", "...", None))
        self.ui_calibration_add.setText(_translate("CalibrationEdit", "Add", None))
        self.ui_calibration_remove.setText(_translate("CalibrationEdit", "Remove", None))

