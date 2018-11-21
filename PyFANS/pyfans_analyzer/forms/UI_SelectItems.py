# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_SelectItems.ui'
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

class Ui_SelectItems(object):
    def setupUi(self, SelectItems):
        SelectItems.setObjectName(_fromUtf8("SelectItems"))
        SelectItems.resize(517, 382)
        self.verticalLayout = QtGui.QVBoxLayout(SelectItems)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ui_plot_list = QtGui.QListWidget(SelectItems)
        self.ui_plot_list.setObjectName(_fromUtf8("ui_plot_list"))
        self.verticalLayout.addWidget(self.ui_plot_list)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ui_select_all = QtGui.QPushButton(SelectItems)
        self.ui_select_all.setObjectName(_fromUtf8("ui_select_all"))
        self.horizontalLayout.addWidget(self.ui_select_all)
        self.ui_clear_all = QtGui.QPushButton(SelectItems)
        self.ui_clear_all.setObjectName(_fromUtf8("ui_clear_all"))
        self.horizontalLayout.addWidget(self.ui_clear_all)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(SelectItems)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectItems)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SelectItems.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SelectItems.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectItems)

    def retranslateUi(self, SelectItems):
        SelectItems.setWindowTitle(_translate("SelectItems", "Dialog", None))
        self.ui_select_all.setText(_translate("SelectItems", "SelectAll", None))
        self.ui_clear_all.setText(_translate("SelectItems", "ClearAll", None))

