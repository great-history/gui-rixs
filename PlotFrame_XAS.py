import sys
import json
import numpy as np
from DataManager import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui

import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import ConnectionPatch

class PlotFrame_XAS:
    def __init__(self):
        self._setupDataVariable()
        self.setup_mainframe()
        self.setup_mainwindow()

    def _setupDataVariable(self):
        self.data = None
        self.which = None
        self.dpi = 100
        self.name_present = ""
        self.plt_collections = {}
        self.datalist = {}
        self.SpectraDataKeys = ["name", "poltype", "thin", "thout", "phi", "ominc", "eloss", "gamma_c", "gamma_f",
                                "scattering_axis", "eval_i", "eval_n", "trans_op", "gs_list", "temperature", "spectra"]
        self.message = ""
        self.axis_origin_present = [0,0,0,0]

    def setup_mainframe(self):
        self.mainWindow = QMainWindow()
        self.mainWindow.setMinimumHeight(840)
        self.mainWindow.setFixedWidth(960)
        self.mainWindow.setWindowTitle('XAS_MAP')
        self.main_frame = QWidget()

        self.button_Load_File = QPushButton('Load', self.main_frame)
        self.button_Load_File.clicked.connect(self._handleOn_LoadFile)
        self.button_Load_File.setFixedSize(80, 32)

        self.File_Path_text = QLineEdit('', self.main_frame)
        self.File_Path_text.setToolTip("show the file path")
        self.File_Path_text.setFixedSize(200, 32)

        self.combo = QComboBox(self.main_frame)
        self.combo.setFixedSize(160, 32)
        self.combo.addItem("xas_1v1c_python_ed")
        self.combo.addItem("xas_1v1c_fortan_ed")
        self.combo.addItem("xas_2v1c_fortan_ed")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.combo.setFont(font)

        self.button_draw = QPushButton("Draw")
        self.button_draw.setFixedSize(120, 32)
        self.button_draw.clicked.connect(self._handleOn_Draw)

        self.grid_check_box = QCheckBox("Grid")
        self.grid_check_box.setChecked(False)
        self.grid_check_box.stateChanged.connect(self._handleOn_AddGrid)

        self.button_remove_all = QPushButton("Remove_All")
        self.button_remove_all.setFixedSize(120, 32)
        self.button_remove_all.clicked.connect(self._handleOn_Remove_All)

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.button_Load_File)
        hbox_top.addWidget(self.File_Path_text)
        hbox_top.addWidget(self.combo)
        hbox_top.addWidget(self.button_draw)
        hbox_top.addWidget(self.grid_check_box)
        hbox_top.addWidget(self.button_remove_all)

        self.fig_origin = plt.figure(figsize=(16, 10), dpi=self.dpi)
        self.axes_origin = self.fig_origin.add_subplot(111)
        self.canvas_origin = FigureCanvas(self.fig_origin)
        self.canvas_origin.setParent(self.main_frame)

        self.mpl_toolbar_origin = NavigationToolbar(self.canvas_origin, self.main_frame)

        self.data_QList = QListWidget(self.main_frame)
        self.data_QList.setFixedSize(120, 660)
        self.data_QList.itemDoubleClicked.connect(self._handleOnImportFigureFromDataList)

        self.data_QList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        data_QList_menu = QMenu(self.data_QList)
        self.data_QList_menu_import_figure_action = QAction(data_QList_menu)
        self.data_QList_menu_delete_data_action = QAction(data_QList_menu)
        self.data_QList_menu_hide_figure_action = QAction(data_QList_menu)

        self.data_QList_menu_import_figure_action.triggered.connect(self._handleOnImportFigureFromDataList)
        self.data_QList_menu_delete_data_action.triggered.connect(self._handleOnDeleteDataFromDataList)
        self.data_QList_menu_hide_figure_action.triggered.connect(self._handleOnHideFigureFromDataList)

        data_QList_menu.addAction(self.data_QList_menu_import_figure_action)
        data_QList_menu.addAction(self.data_QList_menu_delete_data_action)
        data_QList_menu.addAction(self.data_QList_menu_hide_figure_action)

        self.data_QList_menu_import_figure_action.setText("import figure")
        self.data_QList_menu_delete_data_action.setText("delete item")
        self.data_QList_menu_hide_figure_action.setText("hide figure")

        def data_QList_menu_show():
            if self.data_QList.currentItem() is None:
                return
            data_QList_menu.exec_(QtGui.QCursor.pos())

        self.data_QList.customContextMenuRequested.connect(data_QList_menu_show)

        main_frame_layout = QGridLayout(self.main_frame)
        main_frame_layout.setAlignment(QtCore.Qt.AlignTop)
        main_frame_layout.addLayout(hbox_top, 0, 1, QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.mpl_toolbar_origin, 1, 1, QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.canvas_origin, 2, 1, QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.data_QList, 2, 0, QtCore.Qt.AlignTop)
        # main_frame_layout.addLayout(hbox_bottom, 3, 1, QtCore.Qt.AlignTop)

        self.main_frame.setLayout(main_frame_layout)
        self.mainWindow.setCentralWidget(self.main_frame)

    def setup_mainwindow(self):
        # mainWindow的menuBar的设置
        def create_action(text, slot=None, shortcut=None,
                          icon=None, tip=None, checkable=False,
                          signal="triggered()"):  # 创建一个动作,
            action = QAction(text, self.mainWindow)
            if icon is not None:
                action.setIcon(QIcon(":/%s.png" % icon))
            if shortcut is not None:
                action.setShortcut(shortcut)
            if tip is not None:
                action.setToolTip(tip)
                action.setStatusTip(tip)
            if slot is not None:
                action.triggered.connect(slot)
            if checkable:
                action.setCheckable(True)
            return action

        def add_actions(target, actions):
            for action in actions:
                if action is None:
                    target.addSeparator()  # 两个动作之间画一条横线
                else:
                    target.addAction(action)

        def save_plot(): # file_menu的功能之一,用来保存当前的图像,并在statusBar中显示保存的路径
            file_choices = "PNG (*.png)|*.png"

            path, filetype = QFileDialog.getSaveFileName(self.mainWindow,
                                                         'Save file', '',
                                                         file_choices)
            if path:
                self.canvas_origin.print_figure(path, dpi=self.dpi)
                self.mainWindow.statusBar().showMessage('Saved to %s' % path, 8000) # 8000是指message显示的时间长度为8000毫秒

        file_menu = self.mainWindow.menuBar().addMenu("File")  # 在menuBar上添加File菜单
        save_file_action = create_action("Save plot", slot=save_plot, shortcut="Ctrl+S", tip="Save the plot")
        quit_action = create_action("Quit", slot=self.mainWindow.close, shortcut="Ctrl+Q", tip="Close the application")
        add_actions(file_menu,(save_file_action, None, quit_action))

        def on_about():  # help_menu中的功能,用来介绍该界面已经实现的功能
            msg = """ A demo of using PyQt with matplotlib:

             * Use the matplotlib navigation bar
             * Add values to the text box and press Enter (or click "Draw")
             * Show or hide the grid
             * Drag the slider to modify the width of the bars
             * Save the plot to a file using the File menu
             * Click on a bar to receive an informative message
            """
            QMessageBox.about(self.mainWindow, "About the demo", msg.strip()) # #

        help_menu = self.mainWindow.menuBar().addMenu("Help")
        about_action = create_action("About", slot=on_about, shortcut='F1', tip='About the demo')
        add_actions(help_menu, (about_action,))

        # mainWindow的status Bar的设定
        self.mainWindow.statusBar().showMessage("")

# 得到一个QWidgetList的item
    def _getItemFromName(self, parent, name) -> QListWidgetItem:
        item = QListWidgetItem(parent)
        item.setText(name)
        return item

# 数据的传递,两种方式:文件(Load按钮调用的函数)和从secondframe中传递过来
    def _handleOn_LoadFile(self):
        fileName, fileType = QFileDialog.getOpenFileName(self.main_frame, r'Load json',
                                                         r'D:\Users\yg\PycharmProjects\spectra_data',
                                                         r'json Files(*.json)')
        if fileName == "":
            self.informMsg("未选择文件")
            return
        with open(fileName, 'r') as f:
            temp = json.loads(f.read())
        if temp == None:
            self.informMsg("空文件")
            return
        if self.SpectraDataKeys != temp.keys():
            self.informMsg("该文件内容不对")
            return
        which = self.combo.currentText()
        try:
            if which in temp["spectra"].keys():
                data = [temp['poltype'], temp['ominc'], temp['spectra'][which]]
                name = temp['name'] + '_' + which
                self.AddToListByName(name, which, data)
        except:
               if temp["spectra"][which] == None:
                    self.informMsg("该文件没有关于"+which+"的spectra数据")
                    return

    # 用来获取从SecondFrame中传递过来的数据
    def _LoadFromSecondFrame(self, which, spectraData: SpectraBasicData):
        name = spectraData.name + '_' + which
        data = [spectraData.poltype, spectraData.ominc, spectraData.spectra[which]]
        self.AddToListByName(name,which,data)

    def AddToListByName(self, name, which, data):
        row = 0
        while row < self.data_QList.count():
            if self.data_QList.item(row).text() == name:
                break
            row += 1
        if row != self.data_QList.count():
            reply = self.questionMsg("已经存在同名的数据类,是否进行覆盖？")
            if reply == False:
                return
            else:
                if name in self.plt_collections.keys():
                    del self.plt_collections[name]
                    self.data_QList.takeItem(row)

        item = self._getItemFromName(self.data_QList, name)
        self.data_QList.addItem(item)
        self.data_QList.sortItems()
        self.data_QList.setCurrentItem(item)

        poltype = data['poltype']
        ominc_mesh = data['ominc']
        ominc_mesh = np.array(ominc_mesh)
        xas_data = data['spectra'][which]
        xas_data = np.array(xas_data)
        self.name_present = name
        self.datalist[name] = [poltype, ominc_mesh, xas_data]

    # 与作图相关的函数
    def _handleOn_AddGrid(self):
        self.axes_origin.grid(self.grid_check_box.isChecked())
        self.canvas_origin.draw()

    def _handleOn_Draw(self):    # 作一条曲线在原有的基础上,该函数本身并不删除原有的曲线
        if self.name_present == "":
            self.informMsg("未选中item或传入数据")
            return

        data = self.datalist[self.name_present]
        self.origin_canvas_plot_from_data(data)

    def origin_canvas_plot_from_data(self, data):
        ominc_mesh, xas_data = data[1], data[2]
        a, b, c, d = min(ominc_mesh), max(ominc_mesh), min(xas_data), max(xas_data)
        if np.all(self.axis) == 0:
            self.axis = [a, b, c, d]
        else:
            if self.axis_origin_present[0] > a:
                self.axis_origin_present[0] = a
            if self.axis_origin_present[1] < b:
                self.axis_origin_present[1] = b
            if self.axis_origin_present[2] > c:
                self.axis_origin_present[2] = c
            if self.axis_origin_present[3] < d:
                self.axis_origin_present[3] = d
        axis = self.axis_origin_present
        self.axes_origin.axis(axis)  # 设置坐标轴的范围(xmin, xmax, ymin, ymax)
        color = QColorDialog.getColor()
        self.plt_collections[self.name_present], = self.axes_origin.plot(ominc_mesh, xas_data,
                                                                         linestyle='-',
                                                                         color=color.name(),
                                                                         label=self.name_present,
                                                                         linewidth=2)
        self.canvas_origin.draw()  # 将更新之后的图像显示

    # to do list:ConnectionPatch

# 与数据的使用/处理有关
# data_QList中调用的函数
    def _handleOnImportFigureFromDataList(self):
        # 如果该函数被调用,则一定是选中对象了,这说明List中至少有一个item
        name = self.data_QList.currentItem()
        if name in self.plt_collections.keys():
            self.informMsg("曲线已存在")
            return
        else:
            data = self.datalist[name]
            self.origin_canvas_plot_from_data(data)

    def _handleOnDeleteDataFromDataList(self): # 图像连同数据全部销毁
        # 如果该函数被调用,则一定是选中对象了,这说明List中至少有一个item
        name = self.data_QList.currentItem()
        if name in self.plt_collections.keys():
            del self.plt_collections[name] # del直接删去键值对
        del self.datalist[name]
        return
    
    def _handleOnHideFigureFromDataList(self): #仅销毁图像保留数据
        # 如果该函数被调用,则一定是选中对象了,这说明List中至少有一个item
        name = self.data_QList.currentItem()
        if name in self.plt_collections.keys():
            del self.plt_collections[name]

# self.button_remove_all的调用函数
    def _handleOn_Remove_All(self):
        try:
            self.axes_origin.cla()
            self.canvas_origin.draw()
            self._handleOn_AddGrid()
            for name in self.plt_collections.keys():
                self.plt_collections[name].remove()
        except:
            return

# 两个信息提示框
    def informMsg(self, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("inform")
        msgBox.setText(msg)
        msgBox.exec_()

    def questionMsg(cls, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("确认框")
        reply = QMessageBox.information(msgBox,
                                        "标题",
                                        msg,
                                        QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        if reply == QMessageBox.No:
            return False
        msgBox.exec_()

# to do list:如何鼠标触碰后显示QWidgetList中的item的名称？？
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PlotFrame_XAS()
    form.mainWindow.show()
    app.exec_()
