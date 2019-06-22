# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_WaterfallNoise.ui'
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

class Ui_WaterfallNoise(object):
    def setupUi(self, WaterfallNoise):
        WaterfallNoise.setObjectName(_fromUtf8("WaterfallNoise"))
        WaterfallNoise.resize(793, 684)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/Icons/realtime_noise_64x64.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WaterfallNoise.setWindowIcon(icon)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(WaterfallNoise)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ui_waterfall_plot = GraphicsLayoutWidget(WaterfallNoise)
        self.ui_waterfall_plot.setObjectName(_fromUtf8("ui_waterfall_plot"))
        self.horizontalLayout.addWidget(self.ui_waterfall_plot)
        self.ui_histogram_layout = GraphicsLayoutWidget(WaterfallNoise)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_histogram_layout.sizePolicy().hasHeightForWidth())
        self.ui_histogram_layout.setSizePolicy(sizePolicy)
        self.ui_histogram_layout.setMinimumSize(QtCore.QSize(200, 0))
        self.ui_histogram_layout.setObjectName(_fromUtf8("ui_histogram_layout"))
        self.horizontalLayout.addWidget(self.ui_histogram_layout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(WaterfallNoise)
        QtCore.QMetaObject.connectSlotsByName(WaterfallNoise)

    def retranslateUi(self, WaterfallNoise):
        WaterfallNoise.setWindowTitle(_translate("WaterfallNoise", "Waterfall Noise Plot", None))

from pyqtgraph import GraphicsLayoutWidget
from . import icon_resources_rc
