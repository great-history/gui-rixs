import sys, os, random
import json
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import ConnectionPatch


class PlotFrame:
    def __init__(self, data=None):
        self.data = data if data is not None else {}
        self.dpi = 100

        self.setup_mainframe()
        self.setup_mainwindow()

        self._handleOn_draw()

    def setup_mainframe(self):
        self.mainWindow = QMainWindow()  # 在Qt中所有的类都有一个共同的基类QObject, QWidget直接继承与QPaintDevice类,
        # QDialog、QMainWindow、QFrame直接继承QWidget 类
        self.mainWindow.setWindowTitle('Demo: PyQt with matplotlib')
        self.main_frame = QWidget()

        self.button_Load_File = QPushButton('加载文本文件', self.main_frame)
        self.button_Load_File.clicked.connect(self._handleOn_LoadFile)
        self.button_Load_File.setFixedSize(120,32)

        self.File_Path_text = QLineEdit('', self.main_frame)
        self.File_Path_text.setToolTip("显示文件路径")
        self.File_Path_text.setFixedSize(286, 32)
        self.File_Path_text.editingFinished.connect(self._handleOn_draw)

        self.combo = QComboBox(self.main_frame)
        self.combo.setFixedSize(104, 32)
        self.combo.addItem("xas_plot")
        self.combo.addItem("rixs_plot")

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.button_Load_File)
        hbox_top.addWidget(self.File_Path_text)
        hbox_top.addWidget(self.combo)

        # create the mpl Figure and FigCanvas objects
        # 第一个画布
        # 在matplotlib中，整个图像为一个Figure对象。在Figure对象中可以包含一个或者多个Axes对象。
        # 每个Axes(ax)对象都是一个拥有自己坐标系统的绘图区域
        self.fig_origin = plt.figure(figsize=(16,8), dpi=self.dpi) # 最大的Artist容器, 它包括组成图表的所有元素
        self.axes_origin = self.fig_origin.add_subplot(111)  # 创建fig中的坐标轴
        # 另一种创建方式是fig, ax = plt.subplots(形参)
        self.canvas_origin = FigureCanvas(self.fig_origin)  # 创建图表的绘制领域,用来放fig
        self.canvas_origin.setParent(self.main_frame) # 该画布又被放在main_frame中
        self.mpl_toolbar_origin = NavigationToolbar(self.canvas_origin, self.main_frame)   # Create the navigation toolbar,
                                                                             # tied to the canvas
        # 定义一些函数,会用到第一个画布中
        self.message = ""
        self.rect = np.zeros((2, 2))
        def onselect(eclick, erelease):
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            self.rect[0][0] = x1
            self.rect[0][1] = y1
            self.rect[1][0] = x2
            self.rect[1][1] = y2

        RectSelector = RectangleSelector(self.axes_origin, onselect, drawtype='box', useblit=True, button=[1],  # 只能用鼠标左键
                                         minspanx=5, minspany=5, spancoords='pixels', interactive=True)
        RectSelector.set_active(False)  # 一开始处于未激活状态

        def toggle_selector(event):
            if event.key == 'i':
                if RectSelector.active:
                    RectSelector.set_active(False) # 此时区域选取完毕
                    print(f"({self.rect[0][0]:3.2f}, {self.rect[0][1]:3.2f}) --> ({self.rect[1][0]:3.2f}, {self.rect[1][1]:3.2f})")
                    self.mainWindow.statusBar().showMessage(self.message, 8000)
                    # to do list:还要添加如何画出放大的图
                else:
                    RectSelector.set_active(True) # 此时准备选区域
                    self.message = ""
                    self.mainWindow.statusBar().showMessage(self.message, 8000)

        self.fig_origin.canvas.mpl_connect('key_press_event', toggle_selector) # 绑定键盘事件，实现切换矩形选区激活状态功能

        # 第二个画布
        self.fig_local_enlarge = plt.figure(figsize=(16,8), dpi=self.dpi)
        self.axes_local_enlarge = self.fig_local_enlarge.add_subplot(111)
        self.canvas_local_enlarge = FigureCanvas(self.fig_local_enlarge)
        self.canvas_local_enlarge.setParent(self.main_frame)
        self.mpl_toolbar_local_enlarge = NavigationToolbar(self.canvas_local_enlarge, self.main_frame)

        # 底下的一些控件
        self.button_draw = QPushButton("Draw")
        self.button_draw.setFixedSize(120,32)
        self.button_draw.clicked.connect(self._handleOn_draw)

        self.grid_check_box = QCheckBox("Grid")
        self.grid_check_box.setToolTip("show the grid or not")
        self.grid_check_box.setChecked(False)
        self.grid_check_box.stateChanged.connect(self._handleOn_draw)  # int

        self.same_check_box = QCheckBox("Same")
        self.same_check_box.setToolTip("show on the same canvas or not")
        self.same_check_box.setChecked(False)
        self.same_check_box.stateChanged.connect(self._handleOn_Show_On_Same_Canvas)  # int

        hbox_bottom = QHBoxLayout()
        hbox_bottom.addWidget(self.button_draw)
        hbox_bottom.addWidget(self.grid_check_box)
        hbox_bottom.addWidget(self.same_check_box)

        main_frame_layout = QGridLayout(self.main_frame)
        main_frame_layout.setAlignment(QtCore.Qt.AlignTop)
        main_frame_layout.addLayout(hbox_top,0,0,QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.mpl_toolbar_origin, 1, 0, QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.mpl_toolbar_local_enlarge, 1, 2, QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.canvas_origin, 2, 0, QtCore.Qt.AlignTop)
        main_frame_layout.addWidget(self.canvas_local_enlarge, 2, 2, QtCore.Qt.AlignTop)
        main_frame_layout.addLayout(hbox_bottom,3,0,QtCore.Qt.AlignTop)

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

    def _handleOn_LoadFile(self):
        fileName, fileType = QFileDialog.getOpenFileName(self.main_frame, r'Load json', r'.', r'json Files(*.json)')
        if fileName == None:
            return

        with open(fileName, 'r') as f:
            temp = json.loads(f.read())
        if temp == None:
            self.informMsg("空文件")
            return
        if "spectra" not in temp.keys():
            self.informMsg("该文件中不含有spectra_data")
            return
        combo_current = self.combo.currentText()
        if temp["spectra"][combo_current] == None:
            self.informMsg("该文件没有关于"+combo_current+"的spectra数据")
            return

        if combo_current == "xas":
            ominc_mesh = temp['ominc']
            ominc_mesh = np.array(ominc_mesh)
            # eloss_mesh = temp['eloss']
            # eloss_mesh = np.array(eloss_mesh)
            xas_data = temp['spectra']['xas']
            xas_data = np.array(xas_data)  # 一般xas_data已经是array,这里是为了确保
            # to do list
            self.informMsg("not implemented yet")

        if combo_current == "rixs":
            ominc_mesh = temp['ominc']
            ominc_mesh = np.array(ominc_mesh)
            eloss_mesh = temp['eloss']
            eloss_mesh = np.array(eloss_mesh)
            rixs_data = temp['spectra']['rixs']
            rixs_data = np.array(rixs_data)  # 一般rixs_data已经是array,这里是为了确保
            # to do list
            self.informMsg("not implemented yet")

        self.data[temp["name"]] = temp["spectra"][self.combo.currentText()]

    def _handleOn_draw(self):    # Redraws the figure
        self.data = list(map(int, self.File_Path_text.text().split()))

        x = range(len(self.data))

        # clear the axes
        self.axes_origin.clear() # 清除之前的图像
        self.axes_origin.grid(self.grid_check_box.isChecked())  # 是否显示网格
        self.axes_origin.bar(x= x, height=self.data, align='center', alpha=0.44, picker=5)
        # redraw the plot anew
        self.canvas_origin.draw()  # 将更新之后的图像显示

    def _handleOn_Show_On_Same_Canvas(self):
        '''
        参数解释如下: ax=父坐标系
                    width, height=子坐标系的宽度和高度(百分比形式或者浮点数个数)
                    loc=子坐标系的位置
                    bbox_to_anchor=边界框，四元数组(x0, y0, width, height)
                    bbox_transform=从父坐标系到子坐标系的几何映射
                    axins=子坐标系
        :return: bool
        '''

        return

    def informMsg(self, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("inform")
        msgBox.setText(msg)
        msgBox.exec_()  # 模态


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PlotFrame()
    form.mainWindow.show()
    app.exec_()
