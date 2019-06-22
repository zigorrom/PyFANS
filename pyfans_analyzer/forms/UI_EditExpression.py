# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_EditExpression.ui'
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

class Ui_EditExpression(object):
    def setupUi(self, EditExpression):
        EditExpression.setObjectName(_fromUtf8("EditExpression"))
        EditExpression.resize(472, 105)
        self.ui_main_layout = QtGui.QVBoxLayout(EditExpression)
        self.ui_main_layout.setContentsMargins(0, 0, 0, 9)
        self.ui_main_layout.setObjectName(_fromUtf8("ui_main_layout"))
        self.widget = QtGui.QWidget(EditExpression)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.widget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ui_expression = QtGui.QLineEdit(self.groupBox)
        self.ui_expression.setObjectName(_fromUtf8("ui_expression"))
        self.verticalLayout.addWidget(self.ui_expression)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.ui_main_layout.addWidget(self.widget)

        self.retranslateUi(EditExpression)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EditExpression.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EditExpression.reject)
        QtCore.QMetaObject.connectSlotsByName(EditExpression)

    def retranslateUi(self, EditExpression):
        EditExpression.setWindowTitle(_translate("EditExpression", "Dialog", None))
        self.groupBox.setTitle(_translate("EditExpression", "Expression", None))

