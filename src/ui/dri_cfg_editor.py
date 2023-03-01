# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\dri_cfg_editor.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DriverConfigEditor(object):
    def setupUi(self, DriverConfigEditor):
        DriverConfigEditor.setObjectName("DriverConfigEditor")
        DriverConfigEditor.resize(323, 322)
        DriverConfigEditor.setWhatsThis("")
        DriverConfigEditor.setAutoFillBackground(False)
        DriverConfigEditor.setStyleSheet("font: 10pt \"Microsoft JhengHei\";\n"
"QLineEdit {\n"
"    border: 1px solid grey;\n"
"     border-radius: 3px;\n"
"}")
        DriverConfigEditor.setSizeGripEnabled(False)
        DriverConfigEditor.setModal(False)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(DriverConfigEditor)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.WrapAllRows)
        self.formLayout.setObjectName("formLayout")
        self.dri_name_label = QtWidgets.QLabel(DriverConfigEditor)
        self.dri_name_label.setObjectName("dri_name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.dri_name_label)
        self.dri_name_input = QtWidgets.QLineEdit(DriverConfigEditor)
        self.dri_name_input.setInputMethodHints(QtCore.Qt.ImhNone)
        self.dri_name_input.setObjectName("dri_name_input")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.dri_name_input)
        self.dri_type_label = QtWidgets.QLabel(DriverConfigEditor)
        self.dri_type_label.setObjectName("dri_type_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.dri_type_label)
        self.dri_type_dropdown = QtWidgets.QComboBox(DriverConfigEditor)
        self.dri_type_dropdown.setObjectName("dri_type_dropdown")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.dri_type_dropdown)
        self.dri_flag_label = QtWidgets.QLabel(DriverConfigEditor)
        self.dri_flag_label.setObjectName("dri_flag_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.dri_flag_label)
        self.dri_flag_area = QtWidgets.QWidget(DriverConfigEditor)
        self.dri_flag_area.setObjectName("dri_flag_area")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dri_flag_area)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dri_flag_preset_dropdown = QtWidgets.QComboBox(self.dri_flag_area)
        self.dri_flag_preset_dropdown.setObjectName("dri_flag_preset_dropdown")
        self.dri_flag_preset_dropdown.addItem("")
        self.horizontalLayout.addWidget(self.dri_flag_preset_dropdown)
        self.dri_flag_input = QtWidgets.QLineEdit(self.dri_flag_area)
        self.dri_flag_input.setObjectName("dri_flag_input")
        self.horizontalLayout.addWidget(self.dri_flag_input)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.dri_flag_area)
        self.dri_exe_label = QtWidgets.QLabel(DriverConfigEditor)
        self.dri_exe_label.setObjectName("dri_exe_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.dri_exe_label)
        self.dri_exe_area = QtWidgets.QWidget(DriverConfigEditor)
        self.dri_exe_area.setObjectName("dri_exe_area")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.dri_exe_area)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.dri_exe_input = QtWidgets.QLineEdit(self.dri_exe_area)
        self.dri_exe_input.setObjectName("dri_exe_input")
        self.horizontalLayout_5.addWidget(self.dri_exe_input)
        self.dri_exe_path_btn = QtWidgets.QToolButton(self.dri_exe_area)
        self.dri_exe_path_btn.setObjectName("dri_exe_path_btn")
        self.horizontalLayout_5.addWidget(self.dri_exe_path_btn)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.dri_exe_area)
        self.verticalLayout_4.addLayout(self.formLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.dri_autoable_label = QtWidgets.QLabel(DriverConfigEditor)
        self.dri_autoable_label.setObjectName("dri_autoable_label")
        self.horizontalLayout_3.addWidget(self.dri_autoable_label)
        self.dri_autoable_checkbox = QtWidgets.QCheckBox(DriverConfigEditor)
        self.dri_autoable_checkbox.setText("")
        self.dri_autoable_checkbox.setObjectName("dri_autoable_checkbox")
        self.horizontalLayout_3.addWidget(self.dri_autoable_checkbox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.del_dri_btn = QtWidgets.QPushButton(DriverConfigEditor)
        self.del_dri_btn.setObjectName("del_dri_btn")
        self.horizontalLayout_3.addWidget(self.del_dri_btn)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.action_btns = QtWidgets.QDialogButtonBox(DriverConfigEditor)
        self.action_btns.setOrientation(QtCore.Qt.Horizontal)
        self.action_btns.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.action_btns.setObjectName("action_btns")
        self.verticalLayout_4.addWidget(self.action_btns)

        self.retranslateUi(DriverConfigEditor)
        self.action_btns.accepted.connect(DriverConfigEditor.accept)
        self.action_btns.rejected.connect(DriverConfigEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(DriverConfigEditor)

    def retranslateUi(self, DriverConfigEditor):
        _translate = QtCore.QCoreApplication.translate
        DriverConfigEditor.setWindowTitle(_translate("DriverConfigEditor", "編輯軀動程式設定"))
        self.dri_name_label.setText(_translate("DriverConfigEditor", "軀動名稱"))
        self.dri_type_label.setText(_translate("DriverConfigEditor", "軀動分類"))
        self.dri_flag_label.setText(_translate("DriverConfigEditor", "安裝參數"))
        self.dri_flag_preset_dropdown.setItemText(0, _translate("DriverConfigEditor", "- 請選擇 -"))
        self.dri_exe_label.setText(_translate("DriverConfigEditor", "軀動路徑"))
        self.dri_exe_path_btn.setText(_translate("DriverConfigEditor", "..."))
        self.dri_autoable_label.setText(_translate("DriverConfigEditor", "可自動安裝"))
        self.del_dri_btn.setText(_translate("DriverConfigEditor", "刪除"))
