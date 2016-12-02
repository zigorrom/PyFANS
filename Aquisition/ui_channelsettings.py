# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ChannelSettings_temp.ui'
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

class Ui_ChannelSettings(object):
    def setupUi(self, ChannelSettings):
        ChannelSettings.setObjectName(_fromUtf8("ChannelSettings"))
        ChannelSettings.resize(485, 226)
        ChannelSettings.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(ChannelSettings)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableWidget = QtGui.QTableWidget(ChannelSettings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setItem(0, 0, item)
        self.verticalLayout.addWidget(self.tableWidget)
        self.buttonBox = QtGui.QDialogButtonBox(ChannelSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ChannelSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ChannelSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ChannelSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(ChannelSettings)

    def retranslateUi(self, ChannelSettings):
        ChannelSettings.setWindowTitle(_translate("ChannelSettings", "Dialog", None))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("ChannelSettings", "Enabled", None))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("ChannelSettings", "Range", None))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("ChannelSettings", "New Row", None))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("ChannelSettings", "Polarity", None))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("ChannelSettings", "Function", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("ChannelSettings", "In1", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("ChannelSettings", "In2", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("ChannelSettings", "In3", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("ChannelSettings", "In4", None))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ChannelSettings = QtGui.QDialog()
    ui = Ui_ChannelSettings()
    ui.setupUi(ChannelSettings)
    ChannelSettings.show()
    sys.exit(app.exec_())

