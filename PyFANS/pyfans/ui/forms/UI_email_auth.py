# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_email_auth.ui'
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

class Ui_EmailAuth(object):
    def setupUi(self, EmailAuth):
        EmailAuth.setObjectName(_fromUtf8("EmailAuth"))
        EmailAuth.resize(268, 108)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EmailAuth.sizePolicy().hasHeightForWidth())
        EmailAuth.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Icons/mail_64x64.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EmailAuth.setWindowIcon(icon)
        self.formLayout = QtGui.QFormLayout(EmailAuth)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(EmailAuth)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.ui_login = QtGui.QLineEdit(EmailAuth)
        self.ui_login.setObjectName(_fromUtf8("ui_login"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.ui_login)
        self.label_2 = QtGui.QLabel(EmailAuth)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.ui_password = QtGui.QLineEdit(EmailAuth)
        self.ui_password.setInputMask(_fromUtf8(""))
        self.ui_password.setEchoMode(QtGui.QLineEdit.Password)
        self.ui_password.setObjectName(_fromUtf8("ui_password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.ui_password)
        self.buttonBox = QtGui.QDialogButtonBox(EmailAuth)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(EmailAuth)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EmailAuth.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EmailAuth.reject)
        QtCore.QMetaObject.connectSlotsByName(EmailAuth)

    def retranslateUi(self, EmailAuth):
        EmailAuth.setWindowTitle(_translate("EmailAuth", "Dialog", None))
        self.label.setText(_translate("EmailAuth", "Login", None))
        self.label_2.setText(_translate("EmailAuth", "Password", None))

from . import icon_resources_rc
