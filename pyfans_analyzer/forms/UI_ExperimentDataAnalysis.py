# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_ExperimentDataAnalysis.ui'
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

class Ui_ExperimentDataAnalysis(object):
    def setupUi(self, ExperimentDataAnalysis):
        ExperimentDataAnalysis.setObjectName(_fromUtf8("ExperimentDataAnalysis"))
        ExperimentDataAnalysis.resize(891, 517)
        self.centralwidget = QtGui.QWidget(ExperimentDataAnalysis)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        ExperimentDataAnalysis.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ExperimentDataAnalysis)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 891, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuPlot = QtGui.QMenu(self.menubar)
        self.menuPlot.setObjectName(_fromUtf8("menuPlot"))
        self.menuLink = QtGui.QMenu(self.menuPlot)
        self.menuLink.setObjectName(_fromUtf8("menuLink"))
        self.menuTimetrace = QtGui.QMenu(self.menuPlot)
        self.menuTimetrace.setObjectName(_fromUtf8("menuTimetrace"))
        self.menuCurve = QtGui.QMenu(self.menubar)
        self.menuCurve.setObjectName(_fromUtf8("menuCurve"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuExport_As = QtGui.QMenu(self.menuFile)
        self.menuExport_As.setObjectName(_fromUtf8("menuExport_As"))
        self.menuRemove = QtGui.QMenu(self.menuFile)
        self.menuRemove.setObjectName(_fromUtf8("menuRemove"))
        ExperimentDataAnalysis.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(ExperimentDataAnalysis)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        ExperimentDataAnalysis.setStatusBar(self.statusbar)
        self.actionAddPlot = QtGui.QAction(ExperimentDataAnalysis)
        self.actionAddPlot.setObjectName(_fromUtf8("actionAddPlot"))
        self.actionAddCurve = QtGui.QAction(ExperimentDataAnalysis)
        self.actionAddCurve.setObjectName(_fromUtf8("actionAddCurve"))
        self.actionLinkAxes = QtGui.QAction(ExperimentDataAnalysis)
        self.actionLinkAxes.setObjectName(_fromUtf8("actionLinkAxes"))
        self.actionLinkXAxis = QtGui.QAction(ExperimentDataAnalysis)
        self.actionLinkXAxis.setObjectName(_fromUtf8("actionLinkXAxis"))
        self.actionLinkYAxis = QtGui.QAction(ExperimentDataAnalysis)
        self.actionLinkYAxis.setObjectName(_fromUtf8("actionLinkYAxis"))
        self.actionUnlink = QtGui.QAction(ExperimentDataAnalysis)
        self.actionUnlink.setObjectName(_fromUtf8("actionUnlink"))
        self.actionRemovePlot = QtGui.QAction(ExperimentDataAnalysis)
        self.actionRemovePlot.setObjectName(_fromUtf8("actionRemovePlot"))
        self.actionRemoveCurve = QtGui.QAction(ExperimentDataAnalysis)
        self.actionRemoveCurve.setObjectName(_fromUtf8("actionRemoveCurve"))
        self.actionCurveProperties = QtGui.QAction(ExperimentDataAnalysis)
        self.actionCurveProperties.setObjectName(_fromUtf8("actionCurveProperties"))
        self.actionImport = QtGui.QAction(ExperimentDataAnalysis)
        self.actionImport.setObjectName(_fromUtf8("actionImport"))
        self.actionOpenWorkingFolder = QtGui.QAction(ExperimentDataAnalysis)
        self.actionOpenWorkingFolder.setObjectName(_fromUtf8("actionOpenWorkingFolder"))
        self.action_plot_histogram = QtGui.QAction(ExperimentDataAnalysis)
        self.action_plot_histogram.setObjectName(_fromUtf8("action_plot_histogram"))
        self.action_plot_tlp = QtGui.QAction(ExperimentDataAnalysis)
        self.action_plot_tlp.setObjectName(_fromUtf8("action_plot_tlp"))
        self.actionExportAsImage = QtGui.QAction(ExperimentDataAnalysis)
        self.actionExportAsImage.setObjectName(_fromUtf8("actionExportAsImage"))
        self.actionExportAsFile = QtGui.QAction(ExperimentDataAnalysis)
        self.actionExportAsFile.setObjectName(_fromUtf8("actionExportAsFile"))
        self.actionSaveFile = QtGui.QAction(ExperimentDataAnalysis)
        self.actionSaveFile.setObjectName(_fromUtf8("actionSaveFile"))
        self.actionRemoveColumns = QtGui.QAction(ExperimentDataAnalysis)
        self.actionRemoveColumns.setObjectName(_fromUtf8("actionRemoveColumns"))
        self.menuLink.addAction(self.actionLinkXAxis)
        self.menuLink.addAction(self.actionLinkYAxis)
        self.menuLink.addAction(self.actionLinkAxes)
        self.menuLink.addAction(self.actionUnlink)
        self.menuTimetrace.addAction(self.action_plot_histogram)
        self.menuTimetrace.addAction(self.action_plot_tlp)
        self.menuPlot.addAction(self.actionAddPlot)
        self.menuPlot.addAction(self.actionRemovePlot)
        self.menuPlot.addAction(self.menuLink.menuAction())
        self.menuPlot.addSeparator()
        self.menuPlot.addAction(self.menuTimetrace.menuAction())
        self.menuCurve.addAction(self.actionAddCurve)
        self.menuCurve.addAction(self.actionRemoveCurve)
        self.menuCurve.addAction(self.actionCurveProperties)
        self.menuExport_As.addAction(self.actionExportAsImage)
        self.menuExport_As.addAction(self.actionExportAsFile)
        self.menuRemove.addAction(self.actionRemoveColumns)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionSaveFile)
        self.menuFile.addAction(self.menuExport_As.menuAction())
        self.menuFile.addAction(self.actionOpenWorkingFolder)
        self.menuFile.addAction(self.menuRemove.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuPlot.menuAction())
        self.menubar.addAction(self.menuCurve.menuAction())

        self.retranslateUi(ExperimentDataAnalysis)
        QtCore.QMetaObject.connectSlotsByName(ExperimentDataAnalysis)

    def retranslateUi(self, ExperimentDataAnalysis):
        ExperimentDataAnalysis.setWindowTitle(_translate("ExperimentDataAnalysis", "Data Plotter", None))
        self.menuPlot.setTitle(_translate("ExperimentDataAnalysis", "Plot", None))
        self.menuLink.setTitle(_translate("ExperimentDataAnalysis", "Link", None))
        self.menuTimetrace.setTitle(_translate("ExperimentDataAnalysis", "Timetrace", None))
        self.menuCurve.setTitle(_translate("ExperimentDataAnalysis", "Curve", None))
        self.menuFile.setTitle(_translate("ExperimentDataAnalysis", "File", None))
        self.menuExport_As.setTitle(_translate("ExperimentDataAnalysis", "Export As", None))
        self.menuRemove.setTitle(_translate("ExperimentDataAnalysis", "Remove", None))
        self.actionAddPlot.setText(_translate("ExperimentDataAnalysis", "Add", None))
        self.actionAddCurve.setText(_translate("ExperimentDataAnalysis", "Add", None))
        self.actionLinkAxes.setText(_translate("ExperimentDataAnalysis", "Axes", None))
        self.actionLinkXAxis.setText(_translate("ExperimentDataAnalysis", "X axis", None))
        self.actionLinkYAxis.setText(_translate("ExperimentDataAnalysis", "Y axis", None))
        self.actionUnlink.setText(_translate("ExperimentDataAnalysis", "Unlink", None))
        self.actionRemovePlot.setText(_translate("ExperimentDataAnalysis", "Remove", None))
        self.actionRemoveCurve.setText(_translate("ExperimentDataAnalysis", "Remove", None))
        self.actionCurveProperties.setText(_translate("ExperimentDataAnalysis", "Properties", None))
        self.actionImport.setText(_translate("ExperimentDataAnalysis", "Import", None))
        self.actionOpenWorkingFolder.setText(_translate("ExperimentDataAnalysis", "Open working folder", None))
        self.action_plot_histogram.setText(_translate("ExperimentDataAnalysis", "Histogram", None))
        self.action_plot_tlp.setText(_translate("ExperimentDataAnalysis", "TLP", None))
        self.actionExportAsImage.setText(_translate("ExperimentDataAnalysis", "Image", None))
        self.actionExportAsFile.setText(_translate("ExperimentDataAnalysis", "File", None))
        self.actionSaveFile.setText(_translate("ExperimentDataAnalysis", "Save", None))
        self.actionRemoveColumns.setText(_translate("ExperimentDataAnalysis", "Columns", None))

