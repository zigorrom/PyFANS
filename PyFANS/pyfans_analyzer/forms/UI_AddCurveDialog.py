# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_AddCurveDialog.ui'
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

class Ui_AddCurveDialog(object):
    def setupUi(self, AddCurveDialog):
        AddCurveDialog.setObjectName(_fromUtf8("AddCurveDialog"))
        AddCurveDialog.resize(331, 267)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddCurveDialog.sizePolicy().hasHeightForWidth())
        AddCurveDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(AddCurveDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_4 = QtGui.QLabel(AddCurveDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.ui_curve_name = QtGui.QLineEdit(AddCurveDialog)
        self.ui_curve_name.setObjectName(_fromUtf8("ui_curve_name"))
        self.horizontalLayout_2.addWidget(self.ui_curve_name)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.ui_log_mode_y = QtGui.QCheckBox(AddCurveDialog)
        self.ui_log_mode_y.setObjectName(_fromUtf8("ui_log_mode_y"))
        self.gridLayout.addWidget(self.ui_log_mode_y, 4, 3, 1, 1)
        self.line = QtGui.QFrame(AddCurveDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 2, 1, 2)
        self.label_2 = QtGui.QLabel(AddCurveDialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        self.ui_x_axis_value = QtGui.QComboBox(AddCurveDialog)
        self.ui_x_axis_value.setObjectName(_fromUtf8("ui_x_axis_value"))
        self.gridLayout.addWidget(self.ui_x_axis_value, 2, 2, 1, 1)
        self.ui_x_axis_function = QtGui.QPushButton(AddCurveDialog)
        self.ui_x_axis_function.setObjectName(_fromUtf8("ui_x_axis_function"))
        self.gridLayout.addWidget(self.ui_x_axis_function, 3, 2, 1, 1)
        self.ui_y_axis_function = QtGui.QPushButton(AddCurveDialog)
        self.ui_y_axis_function.setObjectName(_fromUtf8("ui_y_axis_function"))
        self.gridLayout.addWidget(self.ui_y_axis_function, 3, 3, 1, 1)
        self.label = QtGui.QLabel(AddCurveDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.ui_y_axis_value = QtGui.QComboBox(AddCurveDialog)
        self.ui_y_axis_value.setObjectName(_fromUtf8("ui_y_axis_value"))
        self.gridLayout.addWidget(self.ui_y_axis_value, 2, 3, 1, 1)
        self.line_2 = QtGui.QFrame(AddCurveDialog)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 0, 1, 5, 1)
        self.ui_log_mode_x = QtGui.QCheckBox(AddCurveDialog)
        self.ui_log_mode_x.setObjectName(_fromUtf8("ui_log_mode_x"))
        self.gridLayout.addWidget(self.ui_log_mode_x, 4, 2, 1, 1)
        self.ui_auto_update = QtGui.QCheckBox(AddCurveDialog)
        self.ui_auto_update.setObjectName(_fromUtf8("ui_auto_update"))
        self.gridLayout.addWidget(self.ui_auto_update, 0, 0, 1, 1)
        self.ui_curve_color = ColorButton(AddCurveDialog)
        self.ui_curve_color.setObjectName(_fromUtf8("ui_curve_color"))
        self.gridLayout.addWidget(self.ui_curve_color, 2, 0, 1, 1)
        self.ui_line_width = QtGui.QSpinBox(AddCurveDialog)
        self.ui_line_width.setMaximum(20)
        self.ui_line_width.setProperty("value", 1)
        self.ui_line_width.setObjectName(_fromUtf8("ui_line_width"))
        self.gridLayout.addWidget(self.ui_line_width, 4, 0, 1, 1)
        self.label_3 = QtGui.QLabel(AddCurveDialog)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.line_3 = QtGui.QFrame(AddCurveDialog)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.verticalLayout.addWidget(self.line_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ui_select_position = QtGui.QCheckBox(AddCurveDialog)
        self.ui_select_position.setObjectName(_fromUtf8("ui_select_position"))
        self.horizontalLayout.addWidget(self.ui_select_position)
        self.ui_desired_position = QtGui.QComboBox(AddCurveDialog)
        self.ui_desired_position.setObjectName(_fromUtf8("ui_desired_position"))
        self.ui_desired_position.addItem(_fromUtf8(""))
        self.ui_desired_position.addItem(_fromUtf8(""))
        self.ui_desired_position.addItem(_fromUtf8(""))
        self.ui_desired_position.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.ui_desired_position)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(AddCurveDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddCurveDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddCurveDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddCurveDialog.reject)
        QtCore.QObject.connect(self.ui_select_position, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.ui_desired_position.setVisible)
        QtCore.QMetaObject.connectSlotsByName(AddCurveDialog)

    def retranslateUi(self, AddCurveDialog):
        AddCurveDialog.setWindowTitle(_translate("AddCurveDialog", "Dialog", None))
        self.label_4.setText(_translate("AddCurveDialog", "Curve name:", None))
        self.ui_log_mode_y.setText(_translate("AddCurveDialog", "Log Y", None))
        self.label_2.setText(_translate("AddCurveDialog", "Y Axis", None))
        self.ui_x_axis_function.setText(_translate("AddCurveDialog", "Function", None))
        self.ui_y_axis_function.setText(_translate("AddCurveDialog", "Function", None))
        self.label.setText(_translate("AddCurveDialog", "X Axis", None))
        self.ui_log_mode_x.setText(_translate("AddCurveDialog", "Log X", None))
        self.ui_auto_update.setText(_translate("AddCurveDialog", "Auto Update", None))
        self.ui_curve_color.setText(_translate("AddCurveDialog", "Color", None))
        self.label_3.setText(_translate("AddCurveDialog", "Line Width", None))
        self.ui_select_position.setText(_translate("AddCurveDialog", "Select position", None))
        self.ui_desired_position.setItemText(0, _translate("AddCurveDialog", "top", None))
        self.ui_desired_position.setItemText(1, _translate("AddCurveDialog", "bottom", None))
        self.ui_desired_position.setItemText(2, _translate("AddCurveDialog", "left", None))
        self.ui_desired_position.setItemText(3, _translate("AddCurveDialog", "right", None))

from pyqtgraph import ColorButton
