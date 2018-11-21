# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_Console.ui'
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

class Ui_Console(object):
    def setupUi(self, Console):
        Console.setObjectName(_fromUtf8("Console"))
        Console.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Icons/console_64x64.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Console.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Console)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.console_widget = QtGui.QPlainTextEdit(Console)
        self.console_widget.setReadOnly(True)
        self.console_widget.setObjectName(_fromUtf8("console_widget"))
        self.verticalLayout.addWidget(self.console_widget)

        self.retranslateUi(Console)
        QtCore.QMetaObject.connectSlotsByName(Console)

    def retranslateUi(self, Console):
        Console.setWindowTitle(_translate("Console", "Console", None))

from . import icon_resources_rc
