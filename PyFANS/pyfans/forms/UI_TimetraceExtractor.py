# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\Programming\Repositories\PyFANS\PyFANS\UI\UI_TimetraceExtractor.ui'
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

class Ui_TimetraceExtractor(object):
    def setupUi(self, TimetraceExtractor):
        TimetraceExtractor.setObjectName(_fromUtf8("TimetraceExtractor"))
        TimetraceExtractor.resize(749, 637)
        self.gridLayout_4 = QtGui.QGridLayout(TimetraceExtractor)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.ui_use_timetrace_settings = QtGui.QGroupBox(TimetraceExtractor)
        self.ui_use_timetrace_settings.setCheckable(True)
        self.ui_use_timetrace_settings.setChecked(False)
        self.ui_use_timetrace_settings.setObjectName(_fromUtf8("ui_use_timetrace_settings"))
        self.verticalLayout = QtGui.QVBoxLayout(self.ui_use_timetrace_settings)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.ui_use_sample_rate = QtGui.QCheckBox(self.ui_use_timetrace_settings)
        self.ui_use_sample_rate.setObjectName(_fromUtf8("ui_use_sample_rate"))
        self.gridLayout_3.addWidget(self.ui_use_sample_rate, 0, 0, 1, 1)
        self.ui_sample_rate = QtGui.QLineEdit(self.ui_use_timetrace_settings)
        self.ui_sample_rate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_sample_rate.sizePolicy().hasHeightForWidth())
        self.ui_sample_rate.setSizePolicy(sizePolicy)
        self.ui_sample_rate.setObjectName(_fromUtf8("ui_sample_rate"))
        self.gridLayout_3.addWidget(self.ui_sample_rate, 0, 1, 1, 1)
        self.ui_use_points_per_shot = QtGui.QCheckBox(self.ui_use_timetrace_settings)
        self.ui_use_points_per_shot.setObjectName(_fromUtf8("ui_use_points_per_shot"))
        self.gridLayout_3.addWidget(self.ui_use_points_per_shot, 1, 0, 1, 1)
        self.ui_points_per_shot = QtGui.QLineEdit(self.ui_use_timetrace_settings)
        self.ui_points_per_shot.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_points_per_shot.sizePolicy().hasHeightForWidth())
        self.ui_points_per_shot.setSizePolicy(sizePolicy)
        self.ui_points_per_shot.setObjectName(_fromUtf8("ui_points_per_shot"))
        self.gridLayout_3.addWidget(self.ui_points_per_shot, 1, 1, 1, 1)
        self.ui_use_amplification = QtGui.QCheckBox(self.ui_use_timetrace_settings)
        self.ui_use_amplification.setObjectName(_fromUtf8("ui_use_amplification"))
        self.gridLayout_3.addWidget(self.ui_use_amplification, 2, 0, 1, 1)
        self.ui_total_amplification = QtGui.QLineEdit(self.ui_use_timetrace_settings)
        self.ui_total_amplification.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_total_amplification.sizePolicy().hasHeightForWidth())
        self.ui_total_amplification.setSizePolicy(sizePolicy)
        self.ui_total_amplification.setObjectName(_fromUtf8("ui_total_amplification"))
        self.gridLayout_3.addWidget(self.ui_total_amplification, 2, 1, 1, 1)
        self.ui_use_total_time = QtGui.QCheckBox(self.ui_use_timetrace_settings)
        self.ui_use_total_time.setObjectName(_fromUtf8("ui_use_total_time"))
        self.gridLayout_3.addWidget(self.ui_use_total_time, 3, 0, 1, 1)
        self.ui_total_time_to_convert = QtGui.QLineEdit(self.ui_use_timetrace_settings)
        self.ui_total_time_to_convert.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_total_time_to_convert.sizePolicy().hasHeightForWidth())
        self.ui_total_time_to_convert.setSizePolicy(sizePolicy)
        self.ui_total_time_to_convert.setObjectName(_fromUtf8("ui_total_time_to_convert"))
        self.gridLayout_3.addWidget(self.ui_total_time_to_convert, 3, 1, 1, 1)
        self.ui_use_decimated_sample_rate = QtGui.QCheckBox(self.ui_use_timetrace_settings)
        self.ui_use_decimated_sample_rate.setChecked(True)
        self.ui_use_decimated_sample_rate.setObjectName(_fromUtf8("ui_use_decimated_sample_rate"))
        self.gridLayout_3.addWidget(self.ui_use_decimated_sample_rate, 4, 0, 1, 1)
        self.ui_decimate_sample_rate = QtGui.QLineEdit(self.ui_use_timetrace_settings)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_decimate_sample_rate.sizePolicy().hasHeightForWidth())
        self.ui_decimate_sample_rate.setSizePolicy(sizePolicy)
        self.ui_decimate_sample_rate.setObjectName(_fromUtf8("ui_decimate_sample_rate"))
        self.gridLayout_3.addWidget(self.ui_decimate_sample_rate, 4, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.verticalLayout_3.addWidget(self.ui_use_timetrace_settings)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ui_redirect_output = QtGui.QCheckBox(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_redirect_output.sizePolicy().hasHeightForWidth())
        self.ui_redirect_output.setSizePolicy(sizePolicy)
        self.ui_redirect_output.setObjectName(_fromUtf8("ui_redirect_output"))
        self.horizontalLayout.addWidget(self.ui_redirect_output)
        self.ui_select_output_folder = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_select_output_folder.sizePolicy().hasHeightForWidth())
        self.ui_select_output_folder.setSizePolicy(sizePolicy)
        self.ui_select_output_folder.setObjectName(_fromUtf8("ui_select_output_folder"))
        self.horizontalLayout.addWidget(self.ui_select_output_folder)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.gridLayout_4.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.ui_select_measurement_data_file = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_select_measurement_data_file.sizePolicy().hasHeightForWidth())
        self.ui_select_measurement_data_file.setSizePolicy(sizePolicy)
        self.ui_select_measurement_data_file.setObjectName(_fromUtf8("ui_select_measurement_data_file"))
        self.gridLayout_2.addWidget(self.ui_select_measurement_data_file, 1, 0, 1, 1)
        self.ui_open_measurement_data_file = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_open_measurement_data_file.sizePolicy().hasHeightForWidth())
        self.ui_open_measurement_data_file.setSizePolicy(sizePolicy)
        self.ui_open_measurement_data_file.setObjectName(_fromUtf8("ui_open_measurement_data_file"))
        self.gridLayout_2.addWidget(self.ui_open_measurement_data_file, 1, 1, 1, 1)
        self.ui_convert_all = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_convert_all.sizePolicy().hasHeightForWidth())
        self.ui_convert_all.setSizePolicy(sizePolicy)
        self.ui_convert_all.setObjectName(_fromUtf8("ui_convert_all"))
        self.gridLayout_2.addWidget(self.ui_convert_all, 1, 2, 1, 1)
        self.ui_measurement_data_filename = QtGui.QLineEdit(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_measurement_data_filename.sizePolicy().hasHeightForWidth())
        self.ui_measurement_data_filename.setSizePolicy(sizePolicy)
        self.ui_measurement_data_filename.setReadOnly(True)
        self.ui_measurement_data_filename.setObjectName(_fromUtf8("ui_measurement_data_filename"))
        self.gridLayout_2.addWidget(self.ui_measurement_data_filename, 0, 0, 1, 3)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.ui_filename = QtGui.QLineEdit(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_filename.sizePolicy().hasHeightForWidth())
        self.ui_filename.setSizePolicy(sizePolicy)
        self.ui_filename.setReadOnly(True)
        self.ui_filename.setObjectName(_fromUtf8("ui_filename"))
        self.gridLayout.addWidget(self.ui_filename, 0, 0, 1, 3)
        self.ui_select_file = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_select_file.sizePolicy().hasHeightForWidth())
        self.ui_select_file.setSizePolicy(sizePolicy)
        self.ui_select_file.setObjectName(_fromUtf8("ui_select_file"))
        self.gridLayout.addWidget(self.ui_select_file, 1, 0, 1, 1)
        self.ui_open_file = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_open_file.sizePolicy().hasHeightForWidth())
        self.ui_open_file.setSizePolicy(sizePolicy)
        self.ui_open_file.setObjectName(_fromUtf8("ui_open_file"))
        self.gridLayout.addWidget(self.ui_open_file, 1, 1, 1, 1)
        self.ui_convert_file = QtGui.QPushButton(TimetraceExtractor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui_convert_file.sizePolicy().hasHeightForWidth())
        self.ui_convert_file.setSizePolicy(sizePolicy)
        self.ui_convert_file.setObjectName(_fromUtf8("ui_convert_file"))
        self.gridLayout.addWidget(self.ui_convert_file, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.ui_terminate_execution = QtGui.QPushButton(TimetraceExtractor)
        self.ui_terminate_execution.setObjectName(_fromUtf8("ui_terminate_execution"))
        self.verticalLayout_2.addWidget(self.ui_terminate_execution)
        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.ui_program_output = QtGui.QTextEdit(TimetraceExtractor)
        self.ui_program_output.setReadOnly(True)
        self.ui_program_output.setObjectName(_fromUtf8("ui_program_output"))
        self.gridLayout_4.addWidget(self.ui_program_output, 3, 0, 1, 2)

        self.retranslateUi(TimetraceExtractor)
        QtCore.QMetaObject.connectSlotsByName(TimetraceExtractor)

    def retranslateUi(self, TimetraceExtractor):
        TimetraceExtractor.setWindowTitle(_translate("TimetraceExtractor", "Timetrace Extractor", None))
        self.ui_use_timetrace_settings.setTitle(_translate("TimetraceExtractor", "Timetrace extractor settings", None))
        self.ui_use_sample_rate.setText(_translate("TimetraceExtractor", "Sample Rate", None))
        self.ui_sample_rate.setText(_translate("TimetraceExtractor", "500000", None))
        self.ui_use_points_per_shot.setText(_translate("TimetraceExtractor", "Points Per Shot", None))
        self.ui_points_per_shot.setText(_translate("TimetraceExtractor", "50000", None))
        self.ui_use_amplification.setText(_translate("TimetraceExtractor", "Total Amplification", None))
        self.ui_total_amplification.setText(_translate("TimetraceExtractor", "17200", None))
        self.ui_use_total_time.setText(_translate("TimetraceExtractor", "Total time to convert", None))
        self.ui_total_time_to_convert.setText(_translate("TimetraceExtractor", "-1", None))
        self.ui_use_decimated_sample_rate.setText(_translate("TimetraceExtractor", "Decimated Sample Rate", None))
        self.ui_decimate_sample_rate.setText(_translate("TimetraceExtractor", "10000", None))
        self.ui_redirect_output.setText(_translate("TimetraceExtractor", "Redirect output", None))
        self.ui_select_output_folder.setText(_translate("TimetraceExtractor", "...", None))
        self.ui_select_measurement_data_file.setText(_translate("TimetraceExtractor", "...", None))
        self.ui_open_measurement_data_file.setText(_translate("TimetraceExtractor", "Open", None))
        self.ui_convert_all.setText(_translate("TimetraceExtractor", "Convert all", None))
        self.ui_select_file.setText(_translate("TimetraceExtractor", "...", None))
        self.ui_open_file.setText(_translate("TimetraceExtractor", "Open", None))
        self.ui_convert_file.setText(_translate("TimetraceExtractor", "Convert file", None))
        self.ui_terminate_execution.setText(_translate("TimetraceExtractor", "Terminate", None))

