# Qt5 version 5.15.2
# PyQt5 version 5.15.2
# python version 3.8

from OwnFrame import *
from PlotFrame_XAS import *
from PlotFrame_RIXS import *
from DataManager import *
import json
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from edrixs.solvers import *
from edrixs.plot_spectrum import *


class SecondFrame(OwnFrame):
    def __init__(self, parent=None, width=None, height=None): # parent来自于OwnApplication
        OwnFrame.__init__(self, parent, width, height) # 获得父类中的实例变量
        self.frame = super().getFrame()
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        # self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame.setMinimumHeight(height - 20)
        self.frame.setMinimumWidth(width - 36)
        self.plotframes_xas = []
        self.num_of_plotframe_xas = 0
        self.plotframes_rixs = []
        self.num_of_plotframe_rixs = 0

        self._setupDataVariable()
        self._arrangeUI()
        self._retranslateAll()

        self._textInputRestrict()
        self._arrangeDataInWidgets()

    def _setupDataVariable(self):
        self.dataManager_spectra = DataManager_spectra()
        self.eval_i_fromFirstFrame = None
        self.eval_n_fromFirstFrame = None
        self.trans_op_fromFirstFrame = None
        self.gs_list_fromFirstFrame = None

        self.eval_i_present = None
        self.eval_n_present = None
        self.trans_op_present = None
        self.gs_list_present = None  # 这几个用来存放第一个页面计算的结果或者load的结果
        self.spectra_name_present = None
        self.spectra_data_present = None

        self.SpectraDataKeys = ["name", "poltype", "thin", "thout", "phi", "ominc", "eloss", "gamma_c", "gamma_f",
                                "scattering_axis", "eval_i", "eval_n", "trans_op", "gs_list", "temperature", "spectra"]

    def getFrame(self):  # 属于SecondFrame的getFrame,父类OwnFrame中也含有一个getFrame
        return self.scrollForSecondFrame

# 与所有控件都相关的函数
    def _arrangeUI(self):

        needToSaveStyleSheet = 'color:rgb(160,60,60)'
        #控件组合模板:self.boxSpectraPara electron_lifetime_box
        self.boxSpectraPara = QGroupBox(self.frame)

        self.spectra_name_label = QLabel(self.boxSpectraPara)
        self.spectra_name_label.setFixedHeight(32)
        self.spectra_name_label.setAlignment(QtCore.Qt.AlignCenter)

        self.spectra_name_text = QLineEdit(self.boxSpectraPara)
        self.spectra_name_text.setFixedSize(200, 32)
        self.spectra_name_text.setAlignment(QtCore.Qt.AlignCenter)

        self.poltype_label = QLabel(self.boxSpectraPara)
        self.poltype_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.poltype_label.setStyleSheet(needToSaveStyleSheet)
        self.poltype_label.setFixedHeight(32)

        self.poltype_text = QLineEdit(self.boxSpectraPara)  # str
        # self.poltype_text.setStyleSheet(needToSaveStyleSheet)
        self.poltype_text.setFixedSize(275, 32)

        self.thin_label = QLabel(self.boxSpectraPara)
        self.thin_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.thin_label.setStyleSheet(needToSaveStyleSheet)
        self.thin_label.setFixedHeight(32)

        self.thin_text = QLineEdit(self.boxSpectraPara)  # str
        # self.thin_text.setStyleSheet(needToSaveStyleSheet)
        self.thin_text.setFixedSize(62, 32)

        self.thout_label = QLabel(self.boxSpectraPara)
        self.thout_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.thout_label.setStyleSheet(needToSaveStyleSheet)
        self.thout_label.setFixedHeight(32)

        self.thout_text = QLineEdit(self.boxSpectraPara)  # str
        # self.thout_text.setStyleSheet(needToSaveStyleSheet)
        self.thout_text.setFixedSize(62, 32)

        self.phi_label = QLabel(self.boxSpectraPara)
        self.phi_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.phi_label.setStyleSheet(needToSaveStyleSheet)
        self.phi_label.setFixedHeight(32)

        self.phi_text = QLineEdit(self.boxSpectraPara)  # str
        # self.phi_text.setStyleSheet(needToSaveStyleSheet)
        self.phi_text.setFixedSize(62, 32)
                                 # ominc和eloss都允许用户有两种输入形式,一种是::另一种是;;
        self.ominc_label = QLabel(self.boxSpectraPara)
        self.ominc_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ominc_label.setStyleSheet(needToSaveStyleSheet)
        self.ominc_label.setFixedHeight(32)

        self.ominc_text = QLineEdit(self.boxSpectraPara)  # str
        self.ominc_text.setStyleSheet(needToSaveStyleSheet)
        self.ominc_text.setFixedSize(126, 32)

        self.eloss_label = QLabel(self.boxSpectraPara)
        self.eloss_label.setAlignment(QtCore.Qt.AlignCenter)
        self.eloss_label.setStyleSheet(needToSaveStyleSheet)
        self.eloss_label.setFixedHeight(32)

        self.eloss_text = QLineEdit(self.boxSpectraPara)  # str
        self.eloss_text.setStyleSheet(needToSaveStyleSheet)
        self.eloss_text.setFixedSize(126, 32)

        self.buttonAddToSpectraList = QPushButton(self.boxSpectraPara)
        self.buttonAddToSpectraList.setStyleSheet(needToSaveStyleSheet)
        self.buttonAddToSpectraList.setFixedSize(126, 32)
        self.buttonAddToSpectraList.clicked.connect(self._handleOnAddToSpectraList)

        # 控件组合模板:electron_lifetime_box
        self.lifetime_box = QGroupBox(self.frame)
        self.gamma_c_label = QLabel(self.lifetime_box)
        self.gamma_c_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.gamma_c_label.setStyleSheet(needToSaveStyleSheet)
        self.gamma_c_label.setFixedHeight(32)

        self.gamma_c_text = QLineEdit(self.lifetime_box)  # str
        # self.gamma_c_text.setStyleSheet(needToSaveStyleSheet)
        self.gamma_c_text.setFixedSize(126, 32)

        self.gamma_f_label = QLabel(self.lifetime_box)
        self.gamma_f_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.gamma_f_label.setStyleSheet(needToSaveStyleSheet)
        self.gamma_f_label.setFixedHeight(32)

        self.gamma_f_text = QLineEdit(self.lifetime_box)  # str
        # self.gamma_f_text.setStyleSheet(needToSaveStyleSheet)
        self.gamma_f_text.setFixedSize(126, 32)

        lifetime_box_Layout = QGridLayout(self.lifetime_box)
        lifetime_box_Layout.setAlignment(QtCore.Qt.AlignTop)
        lifetime_box_Layout.addWidget(self.gamma_c_label, 0, 0, QtCore.Qt.AlignTop)
        lifetime_box_Layout.addWidget(self.gamma_c_text, 0, 1, QtCore.Qt.AlignTop)
        lifetime_box_Layout.addWidget(self.gamma_f_label, 0, 2, QtCore.Qt.AlignTop)
        lifetime_box_Layout.addWidget(self.gamma_f_text, 0, 3, QtCore.Qt.AlignTop)

        self.lifetime_box.setLayout(lifetime_box_Layout)

        self.temperature_label = QLabel(self.boxSpectraPara)
        self.temperature_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.temperature_label.setStyleSheet(needToSaveStyleSheet)
        self.temperature_label.setFixedHeight(32)

        self.temperature_text = QLineEdit(self.boxSpectraPara)
        # self.temperature_text.setStyleSheet(needToSaveStyleSheet)
        self.temperature_text.setFixedSize(62, 32)

        boxSpectraParaLayout = QGridLayout(self.boxSpectraPara)
        boxSpectraParaLayout.setAlignment(QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.spectra_name_label, 0, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.spectra_name_text, 0, 1, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.poltype_label, 1, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.poltype_text, 1, 1, 1, 3, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.thin_label, 2, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.thin_text, 2, 1, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.thout_label, 3, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.thout_text, 3, 1, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.phi_label, 4, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.phi_text, 4, 1, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.ominc_label, 5, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.ominc_text, 5, 1, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.eloss_label, 6, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.eloss_text, 6, 1, 1, 1, QtCore.Qt.AlignTop)
        # boxSpectraParaLayout.addWidget(self.lifetime_box, 4, 0, 1, 4, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.temperature_label, 7, 0, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.temperature_text, 7, 1, 1, 1, QtCore.Qt.AlignTop)
        boxSpectraParaLayout.addWidget(self.buttonAddToSpectraList, 7, 2, 1, 1, QtCore.Qt.AlignTop)

        self.boxSpectraPara.setLayout(boxSpectraParaLayout)

        # 控件组合模板:self.boxSpectraList
        self.boxSpectraList = QGroupBox(self.frame)

        self.spectra_list = QListWidget(self.boxSpectraList)
        self.spectra_list.setFixedWidth(200)
        self.spectra_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        def spectra_list_menu_show():
            if self.spectra_list.currentItem() is None:
                return
            self.spectra_list_menu.exec_(QtGui.QCursor.pos())

        self.spectra_list.customContextMenuRequested.connect(spectra_list_menu_show)
        self.spectra_list.itemDoubleClicked.connect(self._handleOnImportSpectraFromList)

        self.spectra_list_menu = QMenu(self.spectra_list)

        def spectra_list_import_action():
            self._handleOnImportSpectraFromList(self.spectra_list.CurrentItem())
        self.spectra_list_menu_import_action = QAction(self.spectra_list_menu)
        self.spectra_list_menu_import_action.triggered.connect(spectra_list_import_action)
        self.spectra_list_menu_delete_action = QAction(self.spectra_list_menu)
        self.spectra_list_menu_delete_action.triggered.connect(self._handleOnDeleteFromSpectraList)
        self.spectra_list_menu.addAction(self.spectra_list_menu_import_action)
        self.spectra_list_menu.addAction(self.spectra_list_menu_delete_action)

        self.spectra_list_save_button = QPushButton(self.spectra_list)
        self.spectra_list_save_button.setFixedSize(62, 32)
        self.spectra_list_save_button.clicked.connect(self._handleOnSaveSpectraList)

        self.spectra_list_load_button = QPushButton(self.spectra_list)
        self.spectra_list_load_button.setFixedSize(62, 32)
        self.spectra_list_load_button.clicked.connect(self._handleOnLoadSpectraList)

        boxSpectraListParaLayout = QGridLayout(self.boxSpectraList)
        boxSpectraListParaLayout.setAlignment(QtCore.Qt.AlignTop)
        boxSpectraListParaLayout.addWidget(self.spectra_list, 2, 0, 2, 2, QtCore.Qt.AlignTop)
        boxSpectraListParaLayout.addWidget(self.spectra_list_save_button, 4, 0, QtCore.Qt.AlignTop)
        boxSpectraListParaLayout.addWidget(self.spectra_list_load_button, 4, 1, QtCore.Qt.AlignTop)

        self.boxSpectraList.setLayout(boxSpectraListParaLayout)

        # 控件组合模板:scattering_axis_box
        self.scattering_axis_box = QGroupBox(self.frame)
        # 3*3的矩阵
        self.scattering_axis_texts = [[QLineEdit(self.scattering_axis_box) for _ in range(3)] for _ in range(3)]
        for row in self.scattering_axis_texts:
            for LineEdit in row:
                LineEdit.setFixedSize(62, 32)

        scattering_axis_box_layout = QGridLayout(self.scattering_axis_box)
        scattering_axis_box_layout.setAlignment(QtCore.Qt.AlignTop)

        def arrange_matrix_on_box(grid_layout, widgets):
            for row_i in range(len(widgets)):
                one_row = widgets[row_i]
                for col_j in range(len(one_row)):
                    grid_layout.addWidget(one_row[col_j], row_i, col_j, QtCore.Qt.AlignTop)

        arrange_matrix_on_box(scattering_axis_box_layout, self.scattering_axis_texts)
        self.scattering_axis_box.setLayout(scattering_axis_box_layout)

        # 控件组合模板:channel_box
        self.channel_box = QGroupBox(self.frame)

        self.combo = QComboBox(self.channel_box)
        self.combo.addItem("xas_1v1c_python_ed")  # 当选用某些频道但没有实现进行精确对角化则会报错,让用户先去进行相应的精确对角化
        self.combo.addItem("xas_1v1c_fortran_ed")
        self.combo.addItem("rixs_1v1c_python_ed")
        self.combo.addItem("rixs_1v1c_fortran_ed")
        self.combo.addItem("xas_2v1c_fortran_ed")
        self.combo.addItem("rixs_2v1c_fortran_ed")
        self.combo.setCurrentText("xas_1v1c_python_ed")
        self.combo.setFixedSize(225, 32)

        self.spectrum_calculation_button = QPushButton(self.channel_box)
        self.spectrum_calculation_button.clicked.connect(self._handleOnSpectrumCalculation)
        self.spectrum_calculation_button.setFixedSize(200, 32)

        self.plot_button = QPushButton(self.channel_box)
        self.plot_button.setFixedSize(175, 32)
        self.plot_button.clicked.connect(self._handleOnPlotSpectrum)

        self.plotframe_xas_label = QLabel(self.channel_box)
        self.plotframe_xas_label.setAlignment(QtCore.Qt.AlignCenter)
        self.plotframe_xas_label.setFixedHeight(32)
        self.plotframe_xas_combo = QComboBox(self.channel_box)
        self.plotframe_xas_combo.setFixedSize(62, 32)

        self.plotframe_rixs_label = QLabel(self.channel_box)
        self.plotframe_rixs_label.setAlignment(QtCore.Qt.AlignCenter)
        self.plotframe_rixs_label.setFixedHeight(32)
        self.plotframe_rixs_combo = QComboBox(self.channel_box)
        self.plotframe_rixs_combo.setFixedSize(62, 32)

        channel_box_layout = QGridLayout()
        channel_box_layout.setAlignment(QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.combo,0,0,QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.spectrum_calculation_button,1,0,QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.plot_button,2,0,QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.plotframe_xas_label,3,0,QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.plotframe_xas_combo,3,1,QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.plotframe_rixs_label,3,2,QtCore.Qt.AlignTop)
        channel_box_layout.addWidget(self.plotframe_rixs_combo,3,3,QtCore.Qt.AlignTop)
        self.channel_box.setLayout(channel_box_layout)

        # frame的布局
        mainLayout = QGridLayout(self.frame)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        # mainLayout中的布局
        mainLayout.setSpacing(2)

        mainLayout.addWidget(self.boxSpectraPara, 0, 0, 8, 1, QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.lifetime_box, 8, 0, 1, 1, QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.boxSpectraList, 0, 1, 10, 1, QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.scattering_axis_box, 9, 0, 3, 1, QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.channel_box, 12, 0, 1, 1, QtCore.Qt.AlignTop)
#
        for t in range(mainLayout.columnCount()):
            mainLayout.setColumnStretch(t,1)

        self.frame.setLayout(mainLayout)
        self.scrollForSecondFrame = QScrollArea(self.frame.parent())
        self.scrollForSecondFrame.setWidget(self.frame)

    def _retranslateAll(self):
        self._retranslateTips()
        self._retranslateNames()

    def _retranslateTips(self):
        _translate = QtCore.QCoreApplication.translate
        # self.boxSpectraPara
        self.poltype_text.setToolTip(
            _translate("SecondFrame_poltype_text_tip", "光子极化状态"))
        self.poltype_text.setPlaceholderText(
            _translate("SecondFrame_poltype_text_sample", "例如:(linear,alpha,left,0)"))
        self.thin_text.setToolTip(
            _translate("SecondFrame_thin_text_tip","光子入射??"))
        self.thin_text.setPlaceholderText(
            _translate("SecondFrame_thin_text_sample","0.0"))
        self.thout_text.setToolTip(
            _translate("SecondFrame_thout_text_tip","光子出射??"))
        self.thout_text.setPlaceholderText(
            _translate("SecondFrame_thin_text_sample","0.0"))
        self.phi_text.setToolTip(
            _translate("SecondFrame_thout_text_tip","光子入射??"))
        self.phi_text.setPlaceholderText(
            _translate("SecondFrame_thin_text_sample","0.0"))
        self.ominc_text.setToolTip(
            _translate("SecondFrame_ominc_text_tip","入射光子能量(eV)"))
        self.ominc_text.setPlaceholderText(
            _translate("SecondFrame_ominc_text_sample","0.1:10:0.1或者0;10;5"))
        self.eloss_text.setToolTip(
            _translate("SecondFrame_eloss_text_tip","光子损失能量(eV)"))
        self.ominc_text.setPlaceholderText(
            _translate("SecondFrame_eloss_text_sample","0.1:10:0.1或者0;10;5"))
        self.temperature_text.setToolTip(
            _translate("SecondFrame_temperature_text_tip","温度"))
        self.temperature_text.setPlaceholderText(
            _translate("SecondFrame_temperature_text_sample","1.0"))

        # self.boxSpectraList
        self.spectra_name_text.setToolTip(
            _translate("SecondFrame_spectra_name_text_tip", "起个名字"))
        self.spectra_name_text.setPlaceholderText(
            _translate("SecondFrame_spectra_name_text", "例:rixs_Cu3d104s2"))
        self.buttonAddToSpectraList.setToolTip(
            _translate("SecondFrame_add_to_spectra_list_button_tip", "添加到列表中"))

        self.spectra_list_menu_import_action.setToolTip(  # 这个好像没用
            _translate("SecondFrame_spectra_list_menu_import_action_tip", "导入选中元素"))
        self.spectra_list_menu_delete_action.setToolTip(  # 这个好像没用
            _translate("SecondFrame_spectra_list_menu_import_action_tip", "删除选中元素"))

        self.spectra_list_save_button.setToolTip(
            _translate("SecondFrame_spectra_list_save_button_tip", "保存列表"))
        self.spectra_list_load_button.setToolTip(
            _translate("SecondFrame_spectra_list_load_button_tip", "加载列表"))

        # scattering_axis_box
        for row in self.scattering_axis_texts:
            for lineEdit in row:
                lineEdit.setToolTip(_translate("SecondFrame_scattering_axis_texts_tip",""))
                lineEdit.setPlaceholderText(_translate("SecondFrame_scattering_axis_texts_sample","例:1.0"))

        # electron_lifetime_box
        self.gamma_c_text.setToolTip(_translate("SecondFrame_gamma_c","寿命"))
        self.gamma_c_text.setPlaceholderText(_translate("SecondFrame_gamma_c","例:0.1"))
        self.gamma_f_text.setToolTip(_translate("SecondFrame_gamma_f","寿命"))
        self.gamma_f_text.setPlaceholderText(_translate("SecondFrame_gamma_f","例:0.1"))

        # channel_box
        self.combo.setToolTip(_translate("SecondFrame_combo_tip","请选择一个频道"))
        self.spectrum_calculation_button.setToolTip(_translate("SecondFrame_spectrum_calculation_button_tip","计算谱型"))
        self.plot_button.setToolTip(_translate("SecondFrame_plot_button_tip","显示谱线"))

    def _retranslateNames(self):
        _translate = QtCore.QCoreApplication.translate
        # self.boxSpectraPara
        self.boxSpectraPara.setTitle(
            _translate("SecondFrame_boxSpectraPara", "photon_para"))
        self.poltype_label.setText(
            _translate("SecondFrame_poltype_label_label", "poltype"))
        self.thin_label.setText(
            _translate("SecondFrame_thin_label_label", "thin"))
        self.thout_label.setText(
            _translate("SecondFrame_thout_label_label", "thout"))
        self.phi_label.setText(
            _translate("SecondFrame_phi_label_label", "phi"))
        self.ominc_label.setText(
            _translate("SecondFrame_ominc_label_label", "ominc"))
        self.eloss_label.setText(
            _translate("SecondFrame_eloss_label_label", "eloss"))
        # electron_lifetime_box
        self.lifetime_box.setTitle(_translate("SecondFrame_lifetime_box", "electron_lifetime"))
        self.gamma_c_label.setText(_translate("SecondFrame_gamma_c_label", "gamma_c"))
        self.gamma_f_label.setText(_translate("SecondFrame_gamma_f_label", "gamma_f"))
        self.temperature_label.setText(_translate("SecondFrame_temperature_label", "temperature"))

        # self.boxSpectraList
        self.boxSpectraList.setTitle(
            _translate("secondFrame_spectra_list_title", "spectra_list"))
        self.spectra_name_label.setText(
            _translate("SecondFrame_spectra_name_label", "spectral_name"))
        self.buttonAddToSpectraList.setText(
            _translate("SecondFrame_add_to_spectra_list_button_label", "add to ->"))

        self.spectra_list_menu_import_action.setText(  # 这个好像没用
            _translate("SecondFrame_spectra_list_menu_import_action_label", "import"))
        self.spectra_list_menu_delete_action.setText(  # 这个好像没用
            _translate("SecondFrame_spectra_list_menu_delete_action_label", "delete"))

        self.spectra_list_save_button.setText(
            _translate("SecondFrame_spectra_list_save_button_label", "save"))
        self.spectra_list_load_button.setText(
            _translate("SecondFrame_spectra_list_load_button_label", "load"))

        # scattering_axis_box
        self.scattering_axis_box.setTitle(_translate("SecondFrame_scattering_axis_title", "scattering_axis"))

        # channel_box
        self.channel_box.setTitle(_translate("SecondFrame_channel_box", "channel_box"))
        self.spectrum_calculation_button.setText(_translate("SecondFrame_spectrum_calculation_button_label", "spectrum_calculation"))
        self.plot_button.setText(_translate("SecondFrame_plot_button_label", "plot spectrum"))
        self.plotframe_rixs_label.setText(_translate("SecondFrame_plotframe_rixs_label","plotframe_rixs"))
        self.plotframe_xas_label.setText(_translate("SecondFrame_plotframe_xas_label","plotframe_xas"))

    def _textInputRestrict(self):
        # to do list: poltype规范输入的正则表达式
        # poltypeRegx = QtCore.QRegExp(r"(linear,0)|(left,0)|(right,0)|(isotropic,0)") #之后还要修改(linear,0)
        # poltypeRegxValidator = QtGui.QRegExpValidator(poltypeRegx, self.frame)
        # self.poltype_text.setValidator(poltypeRegxValidator)
        self.thin_text.setValidator(self.floatRegxValidator)
        self.thout_text.setValidator(self.floatRegxValidator)
        self.phi_text.setValidator(self.floatRegxValidator)
        self.ominc_text.setValidator(self.floatlistRegxValidator)
        self.eloss_text.setValidator(self.floatlistRegxValidator)
        self.gamma_c_text.setValidator(self.floatListRegxValidator)
        self.gamma_f_text.setValidator(self.floatListRegxValidator)

        for row in self.scattering_axis_texts:
            for lineEdit in row:
                lineEdit.setValidator(self.floatRegxValidator)

    def _arrangeDataInWidgets(self):
        super()._bindDataWithWidgets("spectra_name", self.spectra_name_text, self._toSimpleStrFromText)
        super()._bindDataWithWidgets("poltype", self.poltype_text, self._toSimpleStrFromText)
        super()._bindDataWithWidgets("thin", self.thin_text, self._toFloatFromText)
        super()._bindDataWithWidgets("thout", self.thout_text, self._toFloatFromText)
        super()._bindDataWithWidgets("phi", self.phi_text, self._toFloatFromText)
        super()._bindDataWithWidgets("ominc", self.ominc_text, self._toFloatlistByStrFromText)
        super()._bindDataWithWidgets("eloss", self.eloss_text, self._toFloatlistByStrFromText)
        super()._bindDataWithWidgets("gamma_c", self.gamma_c_text, self._toFloatListByStrFromText)
        super()._bindDataWithWidgets("gamma_f", self.gamma_f_text, self._toFloatListByStrFromText)
        super()._bindDataWithWidgets("scattering_axis", self.scattering_axis_texts, self._toFloatListByWidgets_2DFromText)

# 以下是与数据处理/传递相关的函数
    def _verifyValidSpectraData(self):
        # 如果验证通过，可以加入到列表中
        verified = True
        # 哪些是必须填的参数
        ominc = super()._getDataFromInupt("ominc")
        eloss = super()._getDataFromInupt("eloss")
        eval_i = self.eval_i_present
        eval_n = self.eval_n_present
        trans_op = self.trans_op_present
        # gs_list = self.gs_list_present
        if ominc is None:
            self.informMsg("请输入规范格式的ominc")
            verified = False
        if eloss is None:
            self.informMsg("请输入规范格式的eloss")
            verified = False
        if eval_i is None:
            self.informMsg("eval_i怎么不存在？")
            verified = False
        if eval_n is None:
            self.informMsg("eval_n怎么不存在？")
            verified = False
        if trans_op is None:
            self.informMsg("trans_op怎么不存在？")
            verified = False
        return verified

    def _getSpectraDataFromInput(self) -> SpectraBasicData or None:
        if not self._verifyValidSpectraData():
            self.informMsg("信息不完整,请检查")
            return None
        spectra_name = super()._getDataFromInupt("spectra_name")
        poltype = super()._getDataFromInupt("poltype")
        thin = super()._getDataFromInupt("thin")
        thout = super()._getDataFromInupt("thout")
        phi = super()._getDataFromInupt("phi")
        ominc = super()._getDataFromInupt("ominc")
        eloss = super()._getDataFromInupt("eloss")
        gamma_c = super()._getDataFromInupt("gamma_c")
        gamma_f = super()._getDataFromInupt("gamma_f")
        scattering_axis = super()._getDataFromInupt("scattering_axis")
        temperature = super()._getDataFromInupt("temperature")

        spectraData = SpectraBasicData(
            name=spectra_name,
            poltype=poltype,
            thin=thin,
            thout=thout,
            phi=phi,
            ominc=ominc,
            eloss=eloss,
            gamma_c=gamma_c,
            gamma_f=gamma_f,
            scattering_axis=scattering_axis,
            eval_i=self.eval_i_present,
            eval_n=self.eval_n_present,
            trans_op=self.trans_op_present,
            gs_list=self.gs_list_present,
            temperature=temperature)
        return spectraData

    def _getItemFromSpectraData(self, parent, spectraData:SpectraBasicData) -> QListWidgetItem:
        item = QListWidgetItem(parent)
        itemName = DataManager_spectra.getNameFromSpectraData(spectraData)
        item.setText(itemName)
        return item

# spectra数据相关
# self.boxSpectraList的某个调用函数
    def _handleOnImportSpectraFromList(self, item:QListWidgetItem):
        data = self.dataManager_spectra.getSpectraDataByName(item.text())
        if data is None:  # 应该不会到这里，加入列表的时候存在，这个选择又只能选择列表中的，应该不会不存在
            self.informMsg(f"导入数据失败，未找到:{item.text()}")
            return
        # 根据数据设置界面
        self.spectra_name_present = item.text()
        self.spectra_data_present = self.dataManager_spectra.spectraBasicDataList[self.spectra_name_present]
        self.eval_i_present = self.spectra_data_present.eval_i
        self.eval_n_present = self.spectra_data_present.eval_n
        self.trans_op_present = self.spectra_data_present.trans_op
        self.gs_list_present = self.spectra_data_present.gs_list
        self._setInterfaceBySpectraData(data)

    def _setInterfaceBySpectraData(self, data:SpectraBasicData):  # data类型到时候需注明
        if data is None:
            return
        self.spectra_name_text.setText("" if data.name is None else data.name)
        self.poltype_text.setText("" if data.poltype is None else data.poltype)
        self.thin_text.setText("" if data.thin is None else data.thin)
        self.thout_text.setText("" if data.thout is None else data.thout)
        self.phi_text.setText("" if data.phi is None else data.phi)
        self.ominc_text.setText("" if data.ominc is None else data.ominc)
        self.eloss_text.setText("" if data.eloss is None else data.eloss)
        if data.scattering_axis is not None:
            i = 0
            j = 0
            for row in self.scattering_axis_texts:
                for lineEdit in row:
                    lineEdit.setText(data.scattering_axis[i][j])
                    j += 1
                i += 1

# self.boxSpectraList的某个调用函数
    def _handleOnDeleteFromSpectraList(self) -> bool:
        item = self.spectra_list.currentItem()
        if item is None:
            return False
        row = self.spectra_list.row(item)
        if item == self.spectra_name_present: # 恰好删除的是当前的item,即在界面上显示的那个
            self.spectra_list.takeItem(row)
            self.spectra_list.sortItems()
            self.spectra_name_present = None
            self.spectra_data_present = None
            self._retranslateTips()  # 再将界面上的数据抹去
        else: # 删除的不是当前的item
            self.spectra_list.takeItem(row)

        # 把dataManager中的也删了吧
        del self.dataManager_spectra.spectraBasicDataList[item.text()]

        # print(item.text())
        return True

    def _handleOnSaveSpectraList(self):
        item = self.spectra_list.currentItem()
        if item is None:
            self.informMsg("未选中atom_list中的item")
            return False

        fileName = item.text() + ".json"
        SpectraData = self.dataManager_spectra.spectraBasicDataList[item.text()]
        IsNameRight = False
        fileName_choose, filetype = QFileDialog.getSaveFileName(self.frame,
                                                                "文件保存",
                                                                "." + fileName,  # 起始路径
                                                                "Json Files (.json)")
        # PyQt【控件】：QFileDialog.getSaveFileName()的使用
        # 控件作用：打开文件资源管理器，获得你需要保存的文件名，注意：它不会帮你创建文件，只一个返回元组，元组第一项为你的文件路径。

        str_list = fileName_choose.split("/")
        if str_list[-1] == fileName:
            IsNameRight = True
            with open(fileName_choose, 'w') as f:
                json.dump(SpectraData, f, indent=4)  # 若已存在该文件,就覆盖之前

        if IsNameRight == False:
            self.informMsg("文件名不是spectra_name,请重新保存")

        return IsNameRight

    def _handleOnLoadSpectraList(self):
        fileName, fileType = QFileDialog.getOpenFileName(self.frame, r'Load json',
                                               r'D:\Users\yg\PycharmProjects\spectra_data',
                                               r'json Files(*.json)')  # 打开程序文件所在目录是将路径换为.即可
        if fileName == "":
            self.informMsg("未选择文件")
            return
        DataFromFile = self._getSpectraBasicDataFromJsonFile(fileName)
        if DataFromFile == None:
            return
        if DataFromFile.name in self.dataManager_spectra.spectraBasicDataList.keys():
            reply = self.questionMsg("List中已经存在相同名称,是否进行覆盖？")
            if reply == True:
                self.dataManager_spectra.addSpectraData(DataFromFile)  # 这里需要修改,因为spectraData是字典,
                                                                       # 而dataManager_spectra中装的是类
            if reply == False:
                return None
        item = self._getItemFromSpectraData(self.spectra_list, DataFromFile)
        row = 0
        while row < self.spectra_list.count():
            if self.spectra_list.item(row).text() == item.text():
                break
            row += 1
        if row != self.spectra_list.count():
            self.spectra_list.takeItem(row)
        self.spectra_list.addItem(item)
        self.spectra_list.sortItems()
        self.spectra_list.setCurrentItem(item)

        self._handleOnImportSpectraFromList(item)

    def _getSpectraBasicDataFromJsonFile(self, fileName:str) -> SpectraBasicData or None:
        with open(fileName, "r") as f:
            spectraData = json.loads(f.read())  # temp是存放spectra data的数据类

        if self.SpectraDataKeys != list(spectraData.keys()):
            self.informMsg("打开了错误的文件")
            return None

        DataFromFile = SpectraBasicData()
        for key in self.SpectraDataKeys:
            DataFromFile.key = spectraData[key]

        return DataFromFile

# self.buttonAddToSpectraList的调用函数
    def _handleOnAddToSpectraList(self):
        spectraData = self._getSpectraDataFromInput()
        if spectraData is None:
            return
        if self.dataManager_spectra.addSpectraData(spectraData) is False:
            self.informMsg("信息不完整或有误,请检查")
            return
        item = self._getItemFromSpectraData(self.spectra_list, spectraData)
        row = 0
        while row < self.spectra_list.count():
            if self.spectra_list.item(row).text() == item.text():
                break
            row += 1
        if row != self.spectra_list.count():
            reply = self.questionMsg("该名称的文件已存在,是否要覆盖？")
            if reply == True:
                self.spectra_list.takeItem(row)
                self.spectra_list.addItem(item)
                self.spectra_list.sortItems()
                self.spectra_list.setCurrentItem(item)
            if reply == False:
                return
        self.spectra_name_present = spectraData.name
        self.spectra_data_present = spectraData
        self.eval_i_present = self.spectra_data_present.eval_i
        self.eval_n_present = self.spectra_data_present.eval_n
        self.trans_op_present = self.spectra_data_present.trans_op
        self.gs_list_present = self.spectra_data_present.gs_list

# no one use
    def _getSpectraDataFromSpectraList(self, item: QListWidgetItem) -> SpectraBasicData or None:
        return self.dataManager_spectra.getSpectraDataByName(item.text())

# self.spectrum_calculation_button的调用函数(only)
    def _handleOnSpectrumCalculation(self) -> bool:
        SpectraData = self._getSpectraDataFromInput()
        if SpectraData == None:
            return False
        if self.spectra_name_present == None:  # 如果输入的数据没有保存,就报错
            self.informMsg("请先添加到spectra_list之后再进行计算")
            return False

        if self.combo.currentText() == "xas_1v1c_python_ed":
            ominc = SpectraData.ominc
            gamma_c = SpectraData.gamma_c
            if gamma_c is None:
                gamma_c = 0.1
            thin = SpectraData.thin
            if thin is None:
                thin = 1.0
            phi = SpectraData.phi
            if phi is None:
                phi = 0
            poltype = SpectraData.poltype
            gs_list = self.gs_list_present
            temperature = SpectraData.temperature
            if temperature is None:
                temperature = 1.0
            scattering_axis = SpectraData.scattering_axis
            if scattering_axis is not None:
                scattering_axis = np.array(scattering_axis)
            
            if 'xas' in self.dataManager_spectra.spectraBasicDataList[self.spectra_name_present].spectra.keys():
                reply = self.questionMsg("当前数据类中已经含有xas spectra,是否进行覆盖")
                if reply == True:
                    spectra = xas_1v1c_py(eval_i=self.eval_i_present, eval_n=self.eval_n_present, trans_op=self.trans_op_present,
                                          ominc=ominc, gamma_c=gamma_c, thin=thin, phi=phi, pol_type=poltype, gs_list=gs_list,
                                          temperature=temperature, scatter_axis=scattering_axis)
            self.dataManager_spectra.spectraBasicDataList[self.spectra_name_present].spectra['xas_1v1c_python_ed'] = spectra
            return True

        if self.combo.currentText() == "rixs_1v1c_python_ed":
            ominc = SpectraData.ominc
            eloss = SpectraData.eloss
            gamma_c = SpectraData.gamma_c
            if gamma_c is None:
                gamma_c = 0.1
            gamma_f = SpectraData.gamma_f
            if gamma_f is None:
                gamma_f = 0.01
            thin = SpectraData.thin
            if thin is None:
                thin = 1.0
            thout = SpectraData.thout
            if thout is None:
                thout = 1.0
            phi = SpectraData.phi
            if phi is None:
                phi = 0
            poltype = SpectraData.poltype
            gs_list = self.gs_list_present
            temperature = SpectraData.temperature
            if temperature is None:
                temperature = 1.0
            scatter_axis = SpectraData.scattering_axis
            if scatter_axis is not None:
                scatter_axis = np.array(scatter_axis)

            spectra = rixs_1v1c_py(eval_i=self.eval_i_present, eval_n=self.eval_n_present,
                                   trans_op=self.trans_op_present, ominc=ominc, eloss=eloss, gamma_c=gamma_c,
                                   gamma_f=gamma_f, thin=thin, thout=thout, phi=phi, pol_type=poltype, gs_list=gs_list,
                                   temperature=temperature, scatter_axis=scatter_axis)

            self.dataManager_spectra.spectraBasicDataList[self.spectra_name_present].spectra['rixs_1v1c_python_ed'] = spectra
            return True

# self.plot_button的调用函数(only)
    def _handleOnPlotSpectrum(self):
        if self.spectra_name_present == None:
            self.informMsg("无名氏")
            return
        which = self.combo.currentText()
        if self.spectra_data_present["spectra"][which] == None or len(self.spectra_data_present["spectra"][which]) == 0:
            self.informMsg("没有spectra data,请先进行计算")
            return

        self._getPlotFrameByWhich(which, self.spectra_data_present)

    def _getPlotFrameByWhich(self, which, spectraData_present:SpectraBasicData): #调用该函数之前已经确保存在数据
        if "xas" in re.findall("xas", which):
            if self.num_of_plotframe_xas == 0:
                plotframe = PlotFrame_XAS()
                plotframe ._getDataFromSecondFrame(which, spectraData_present)
                self.plotframes_xas.append(plotframe)
                self.num_of_plotframe_xas += 1
                plotframe.mainWindow.show()
                self.plotframe_xas_combo.addItem("1")
            else:
                reply = self.questionMsg("已存在plot frames,仍要新建？")
                if reply is True:  # 新建一个
                    plotframe = PlotFrame_XAS()
                    plotframe._getDataFromSecondFrame(which, spectraData_present)
                    self.plotframes_xas.append(plotframe)
                    plotframe.mainWindow.show()
                    self.num_of_plotframe_xas += 1
                    self.plotframe_xas_combo.addItem(str(self.num_of_plotframe_xas))
                else:
                    curindex = self.plotframe_xas_combo.currentText()
                    curindex = int(curindex)
                    self.plotframes_xas[curindex-1]._getDataFromSecondFrame(which, spectraData_present)

        if "rixs" in re.findall("rixs", which):
            if spectraData_present.spectra['rixs_1v1c_python_ed'] != None:
                self.informMsg("没有spectra data,请先进行计算")
                return
            if self.num_of_plotframe_rixs == 0:
                plotframe = PlotFrame_RIXS()
                plotframe._getDataFromSecondFrame(which, spectraData_present)
                self.plotframes_xas.append(plotframe)
                self.num_of_plotframe_rixs += 1
                plotframe.mainWindow.show()
                self.plotframe_xas_combo.addItem("1")
            else:
                reply = self.questionMsg("已存在plot frames,仍要新建？")
                if reply is True:
                    plotframe = PlotFrame_RIXS()
                    plotframe._getDataFromSecondFrame(which, spectraData_present)
                    self.plotframes_rixs.append(plotframe)
                    self.num_of_plotframe_rixs += 1
                    self.plotframe_xas_combo.addItem(str(self.num_of_plotframe_xas))
                    plotframe.mainWindow.show()
                else:
                    curindex = self.plotframe_xas_combo.currentText()
                    curindex = int(curindex)
                    self.plotframes_rixs[curindex]._getDataFromSecondFrame(which, spectraData_present)
        return

                
                


