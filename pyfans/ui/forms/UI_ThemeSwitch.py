# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_ThemeSwitch.ui'
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

class Ui_ThemeSwitch(object):
    def setupUi(self, ThemeSwitch):
        ThemeSwitch.setObjectName(_fromUtf8("ThemeSwitch"))
        ThemeSwitch.resize(180, 79)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Icons/theme_switch_64x64.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ThemeSwitch.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ThemeSwitch)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ui_light_button = QtGui.QRadioButton(ThemeSwitch)
        self.ui_light_button.setChecked(True)
        self.ui_light_button.setObjectName(_fromUtf8("ui_light_button"))
        self.horizontalLayout.addWidget(self.ui_light_button)
        self.ui_dark_button = QtGui.QRadioButton(ThemeSwitch)
        self.ui_dark_button.setObjectName(_fromUtf8("ui_dark_button"))
        self.horizontalLayout.addWidget(self.ui_dark_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ThemeSwitch)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ThemeSwitch)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ThemeSwitch.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ThemeSwitch.reject)
        QtCore.QMetaObject.connectSlotsByName(ThemeSwitch)

    def retranslateUi(self, ThemeSwitch):
        ThemeSwitch.setWindowTitle(_translate("ThemeSwitch", "Theme Switch", None))
        self.ui_light_button.setText(_translate("ThemeSwitch", "Light", None))
        self.ui_dark_button.setText(_translate("ThemeSwitch", "Dark", None))

from . import icon_resources_rc
