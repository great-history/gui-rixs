# Qt5 version 5.15.2
# PyQt5 version 5.15.2
# python version 3.8

from FirstFrame import *
import sys


class OwnApplication:
    def __init__(self):
        self.dataManager = DataManager_atom() # 似乎没用
        self.widgetsWithData = {}  # 以一个名字(str)为key，value为(控件,解析方式)，可以从控件中获取输入
        self.app = QApplication(sys.argv)
        self.mainWindow = QWidget()  # main window
        self.frames = []  # 存放各个页面
        self.curFrameIndex = 0  # 当前页面索引
        QtGui.QFontDatabase.addApplicationFont("./resource/*.otf")
        self._setFont()

        self._arrangeUI()
        self.mainWindow.show()

    def _arrangeUI(self):
        self._setupMainWindow()
        self._retranslateAll()

        self.topLayout = QGridLayout(self.mainWindow)
        self.topLayout.setAlignment(QtCore.Qt.AlignTop)

        self.frameContain = QHBoxLayout()  # 存放一个页面
        self.topLayout.addLayout(self.frameContain, 0, 0, 1, 10)
        self.topLayout.addWidget(self.goToNextFrameBtn, 1, 0, 1, 10, QtCore.Qt.AlignCenter)
        self.topLayout.setRowStretch(0, 10)
        self.topLayout.setRowStretch(1, 1)

        self.mainWindow.setLayout(self.topLayout)
        self.curFrameIndex = 0  # 当前页面是第一页
        self._addFrameToMainWindow(self.frames[self.curFrameIndex].getFrame())

    def _setupMainWindow(self):
        self.mainWindow.setMinimumHeight(720)
        self.mainWindow.setFixedWidth(1280)

        self.frames.append(FirstFrame(self.mainWindow, width=1280))
        # TODO:加入第二个页面

        self.goToNextFrameBtn = QPushButton(self.mainWindow)
        self.goToNextFrameBtn.setStyleSheet(  # test
            '''
            QPushButton{
                height: 64px;
                width: 64px;
                border-width: 0px;
                border-radius: 10px;
                color: #57579C;
                background-color: #E9EBAE;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F1B99A;
            }
            QPushButton:pressed {
                background-color: #79CDEB;
            }
            QPushButton#cancel{
                background-color: gray ;
            }
            ''')
        self.goToNextFrameBtn.clicked.connect(self._handleOnGotoNextPage)

    def _setFont(self):
        self.mainWindow.setFont(QtGui.QFont("SourceHanSansSC-Medium"))

    def _retranslateAll(self):
        self._retranslateTips()
        self._retranslateNames()

    def _retranslateTips(self):
        _translate = QtCore.QCoreApplication.translate

        self.goToNextFrameBtn.setToolTip(
            _translate("FirstFrame_goToNextFrameBtn_tip", "next page"))

    def _retranslateNames(self):
        _translate = QtCore.QCoreApplication.translate
        self.mainWindow.setWindowTitle(
            _translate("MainWindow_title", "pro"))  # title
        self.goToNextFrameBtn.setText(
            _translate("FirstFrame_goToNextFrameBtn_label", "next"))

    def _addFrameToMainWindow(self, frame):
        self.frameContain.addWidget(self.frames[0].getFrame())  # 在主界面加入一个页面

    def _removeFrameFromMainWindow(self, frame):
        self.frameContain.removeWidget(self.frames[0].getFrame())

    def _handleOnGotoNextPage(self):
        next_p = self.curFrameIndex+1
        if next_p >= len(self.frames):  # 没有下一页了
            return
        self._removeFrameFromMainWindow(self.frames[self.curFrameIndex].getFrame())
        self._addFrameToMainWindow(self.frames[next_p].getFrame())

    def informMsg(self, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("inform")
        msgBox.setText(msg)
        msgBox.exec_()  # 模态

    def run(self):
        # start
        self.app.exec()


if __name__ == '__main__':
    OwnApplication().run()
