# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_acquisitionsettings.ui'
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

class Ui_ui_acquisitionsettings(object):
    def setupUi(self, ui_acquisitionsettings):
        ui_acquisitionsettings.setObjectName(_fromUtf8("ui_acquisitionsettings"))
        ui_acquisitionsettings.resize(400, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ui_acquisitionsettings.sizePolicy().hasHeightForWidth())
        ui_acquisitionsettings.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(ui_acquisitionsettings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEdit = QtGui.QLineEdit(ui_acquisitionsettings)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.spinBox_2 = QtGui.QSpinBox(ui_acquisitionsettings)
        self.spinBox_2.setObjectName(_fromUtf8("spinBox_2"))
        self.gridLayout.addWidget(self.spinBox_2, 3, 1, 1, 1)
        self.spinBox = QtGui.QSpinBox(ui_acquisitionsettings)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.gridLayout.addWidget(self.spinBox, 2, 1, 1, 1)
        self.label_5 = QtGui.QLabel(ui_acquisitionsettings)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.label_3 = QtGui.QLabel(ui_acquisitionsettings)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label = QtGui.QLabel(ui_acquisitionsettings)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.checkBox = QtGui.QCheckBox(ui_acquisitionsettings)
        self.checkBox.setText(_fromUtf8(""))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 4, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ui_acquisitionsettings)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.line = QtGui.QFrame(ui_acquisitionsettings)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.label_4 = QtGui.QLabel(ui_acquisitionsettings)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.comboBox_2 = QtGui.QComboBox(ui_acquisitionsettings)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox_2, 6, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(ui_acquisitionsettings)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox, 5, 1, 1, 1)
        self.label_6 = QtGui.QLabel(ui_acquisitionsettings)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.label_7 = QtGui.QLabel(ui_acquisitionsettings)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 1)
        self.comboBox_3 = QtGui.QComboBox(ui_acquisitionsettings)
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.gridLayout.addWidget(self.comboBox_3, 7, 1, 1, 1)

        self.retranslateUi(ui_acquisitionsettings)
        QtCore.QMetaObject.connectSlotsByName(ui_acquisitionsettings)

    def retranslateUi(self, ui_acquisitionsettings):
        ui_acquisitionsettings.setWindowTitle(_translate("ui_acquisitionsettings", "Form", None))
        self.label_5.setText(_translate("ui_acquisitionsettings", "PGA", None))
        self.label_3.setText(_translate("ui_acquisitionsettings", "Acquisition channel", None))
        self.label.setText(_translate("ui_acquisitionsettings", "SampleRate", None))
        self.label_2.setText(_translate("ui_acquisitionsettings", "Points per shot", None))
        self.label_4.setText(_translate("ui_acquisitionsettings", "Homemade amplifier", None))
        self.comboBox_2.setItemText(0, _translate("ui_acquisitionsettings", "1", None))
        self.comboBox_2.setItemText(1, _translate("ui_acquisitionsettings", "10", None))
        self.comboBox_2.setItemText(2, _translate("ui_acquisitionsettings", "100", None))
        self.comboBox.setItemText(0, _translate("ui_acquisitionsettings", "1", None))
        self.comboBox.setItemText(1, _translate("ui_acquisitionsettings", "10", None))
        self.comboBox.setItemText(2, _translate("ui_acquisitionsettings", "100", None))
        self.label_6.setText(_translate("ui_acquisitionsettings", "Filter gain", None))
        self.label_7.setText(_translate("ui_acquisitionsettings", "Filter cutoff", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui_acquisitionsettings = QtGui.QWidget()
    ui = Ui_ui_acquisitionsettings()
    ui.setupUi(ui_acquisitionsettings)
    ui_acquisitionsettings.show()
    sys.exit(app.exec_())

