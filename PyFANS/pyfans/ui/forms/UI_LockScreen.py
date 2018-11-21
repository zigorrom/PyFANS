# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_LockScreen.ui'
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

class Ui_LockScreen(object):
    def setupUi(self, LockScreen):
        LockScreen.setObjectName(_fromUtf8("LockScreen"))
        LockScreen.resize(1016, 613)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Icons/lock_64x64.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LockScreen.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(LockScreen)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(LockScreen)
        font = QtGui.QFont()
        font.setPointSize(50)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.label.setFont(font)
        self.label.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(LockScreen)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setScaledContents(False)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.ui_unlock_button = QtGui.QPushButton(LockScreen)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_unlock_button.sizePolicy().hasHeightForWidth())
        self.ui_unlock_button.setSizePolicy(sizePolicy)
        self.ui_unlock_button.setMinimumSize(QtCore.QSize(0, 100))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.ui_unlock_button.setFont(font)
        self.ui_unlock_button.setInputMethodHints(QtCore.Qt.ImhNone)
        self.ui_unlock_button.setObjectName(_fromUtf8("ui_unlock_button"))
        self.verticalLayout.addWidget(self.ui_unlock_button)

        self.retranslateUi(LockScreen)
        QtCore.QMetaObject.connectSlotsByName(LockScreen)

    def retranslateUi(self, LockScreen):
        LockScreen.setWindowTitle(_translate("LockScreen", "Lock Screen", None))
        self.label.setText(_translate("LockScreen", "Experiment in progress!", None))
        self.label_2.setText(_translate("LockScreen", "Press the button if you want to interact with UI", None))
        self.ui_unlock_button.setText(_translate("LockScreen", "Unlock", None))

from . import icon_resources_rc
