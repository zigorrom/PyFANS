# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_ExperimentDataExtractor.ui'
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

class Ui_ExperimentDataExtractor(object):
    def setupUi(self, ExperimentDataExtractor):
        ExperimentDataExtractor.setObjectName(_fromUtf8("ExperimentDataExtractor"))
        ExperimentDataExtractor.resize(800, 600)
        self.centralwidget = QtGui.QWidget(ExperimentDataExtractor)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 751, 232))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.listWidget = QtGui.QListWidget(self.groupBox)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout.addWidget(self.listWidget)
        ExperimentDataExtractor.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ExperimentDataExtractor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuImport = QtGui.QMenu(self.menuFile)
        self.menuImport.setObjectName(_fromUtf8("menuImport"))
        self.menuExport_As = QtGui.QMenu(self.menuFile)
        self.menuExport_As.setObjectName(_fromUtf8("menuExport_As"))
        ExperimentDataExtractor.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(ExperimentDataExtractor)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        ExperimentDataExtractor.setStatusBar(self.statusbar)
        self.actionImportSingle = QtGui.QAction(ExperimentDataExtractor)
        self.actionImportSingle.setObjectName(_fromUtf8("actionImportSingle"))
        self.actionImportMany = QtGui.QAction(ExperimentDataExtractor)
        self.actionImportMany.setObjectName(_fromUtf8("actionImportMany"))
        self.actionExportSingleFile = QtGui.QAction(ExperimentDataExtractor)
        self.actionExportSingleFile.setObjectName(_fromUtf8("actionExportSingleFile"))
        self.actionExportToOriginalLocation = QtGui.QAction(ExperimentDataExtractor)
        self.actionExportToOriginalLocation.setObjectName(_fromUtf8("actionExportToOriginalLocation"))
        self.actionClear_Imports = QtGui.QAction(ExperimentDataExtractor)
        self.actionClear_Imports.setObjectName(_fromUtf8("actionClear_Imports"))
        self.menuImport.addAction(self.actionImportSingle)
        self.menuImport.addAction(self.actionImportMany)
        self.menuImport.addAction(self.actionClear_Imports)
        self.menuExport_As.addAction(self.actionExportSingleFile)
        self.menuExport_As.addAction(self.actionExportToOriginalLocation)
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addAction(self.menuExport_As.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(ExperimentDataExtractor)
        QtCore.QMetaObject.connectSlotsByName(ExperimentDataExtractor)

    def retranslateUi(self, ExperimentDataExtractor):
        ExperimentDataExtractor.setWindowTitle(_translate("ExperimentDataExtractor", "MainWindow", None))
        self.groupBox.setTitle(_translate("ExperimentDataExtractor", "Selected Measurement Files", None))
        self.menuFile.setTitle(_translate("ExperimentDataExtractor", "File", None))
        self.menuImport.setTitle(_translate("ExperimentDataExtractor", "Import", None))
        self.menuExport_As.setTitle(_translate("ExperimentDataExtractor", "Export As", None))
        self.actionImportSingle.setText(_translate("ExperimentDataExtractor", "Single", None))
        self.actionImportMany.setText(_translate("ExperimentDataExtractor", "Many", None))
        self.actionExportSingleFile.setText(_translate("ExperimentDataExtractor", "Single File", None))
        self.actionExportToOriginalLocation.setText(_translate("ExperimentDataExtractor", "To original location", None))
        self.actionClear_Imports.setText(_translate("ExperimentDataExtractor", "Clear Imports", None))

