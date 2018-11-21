# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_TimeInfo.ui'
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

class Ui_TimeInfo(object):
    def setupUi(self, TimeInfo):
        TimeInfo.setObjectName(_fromUtf8("TimeInfo"))
        TimeInfo.resize(398, 111)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Icons/time_info_64x64.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TimeInfo.setWindowIcon(icon)
        self.gridLayout_2 = QtGui.QGridLayout(TimeInfo)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(TimeInfo)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(TimeInfo)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.ui_elapsed_time = QtGui.QLineEdit(TimeInfo)
        self.ui_elapsed_time.setReadOnly(True)
        self.ui_elapsed_time.setObjectName(_fromUtf8("ui_elapsed_time"))
        self.gridLayout.addWidget(self.ui_elapsed_time, 1, 1, 1, 1)
        self.ui_time_left = QtGui.QLineEdit(TimeInfo)
        self.ui_time_left.setReadOnly(True)
        self.ui_time_left.setObjectName(_fromUtf8("ui_time_left"))
        self.gridLayout.addWidget(self.ui_time_left, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(TimeInfo)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.ui_experiment_started = QtGui.QLineEdit(TimeInfo)
        self.ui_experiment_started.setReadOnly(True)
        self.ui_experiment_started.setObjectName(_fromUtf8("ui_experiment_started"))
        self.gridLayout.addWidget(self.ui_experiment_started, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(TimeInfo)
        QtCore.QMetaObject.connectSlotsByName(TimeInfo)

    def retranslateUi(self, TimeInfo):
        TimeInfo.setWindowTitle(_translate("TimeInfo", "Time info", None))
        self.label_2.setText(_translate("TimeInfo", "Elapsed time:", None))
        self.label.setText(_translate("TimeInfo", "Experiment Start:", None))
        self.label_3.setText(_translate("TimeInfo", "Time left:", None))

from . import icon_resources_rc
