import queue
import sys
import qdarkstyle
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDir, QObject, pyqtSignal, QThread, QTimer, Qt, QTime, QRect, QSize
from PyQt5.QtGui import QSurfaceFormat, QPainter, QImage, QCursor, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QSizePolicy, QProgressBar, \
    QFileDialog, QOpenGLWidget, QListWidget, QMessageBox, QMenu, QAction, QWidget, \
    QStatusBar, QDialogButtonBox
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from audio import Audio
from utils import State, MyListWidgetItem, listHeight, CompositeObject, SaveTemp
from visualize import tiktok_effect


# noinspection PyAttributeOutsideInit
class Window(QMainWindow):
    # 播放控制信号
    pause = pyqtSignal()
    resume = pyqtSignal()
    stop = pyqtSignal()
    # 传递片段到已移动到子线程的视频、音频对象的信号
    set_video = pyqtSignal(object)
    set_audio = pyqtSignal(object, int, int, int)

    # 界面设定
    def setupUi(self):
        self.setWindowTitle("VideoGenerator")
        self.centralwidget = QWidget(self)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()

        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setRange(0, 0)
        self.horizontalLayout_2.addWidget(self.horizontalSlider)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("")
        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.label_target = QtWidgets.QLabel(self.centralwidget)
        self.label_target.setText("目标")
        self.label_target.setSizePolicy(sizePolicy)
        self.horizontalLayout_3.addWidget(self.label_target)
        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 0, 1, 1)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.label_background = QtWidgets.QLabel(self.centralwidget)
        self.label_background.setSizePolicy(sizePolicy)
        self.label_background.setText("背景")
        self.horizontalLayout_4.addWidget(self.label_background)
        self.gridLayout.addLayout(self.horizontalLayout_4, 4, 0, 1, 1)

        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.label_audio = QtWidgets.QLabel(self.centralwidget)
        self.label_audio.setSizePolicy(sizePolicy)
        self.label_audio.setText("音频")
        self.horizontalLayout_5.addWidget(self.label_audio)
        self.gridLayout.addLayout(self.horizontalLayout_5, 5, 0, 1, 1)

        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_7)
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_6)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setText("")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_8 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_8)
        self.pushButton_10 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_10)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)

        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_6.setText("打开背景")
        self.pushButton_7.setText("打开目标")
        self.pushButton.setText("打开音频")
        self.pushButton_4.setText("设置切分起始时间")
        self.pushButton_8.setText("原地切分")
        self.pushButton_10.setText("重复")
        self.pushButton_3.setText("生成")
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_10.setEnabled(False)
        self.pushButton_8.setEnabled(False)

        self.openGLWidget = MyOpenGLWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openGLWidget.sizePolicy().hasHeightForWidth())
        self.openGLWidget.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.openGLWidget, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.listWidget_3 = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_3.sizePolicy().hasHeightForWidth())
        self.listWidget_3.setSizePolicy(sizePolicy)
        self.listWidget_3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget_3.setDragEnabled(True)
        self.listWidget_3.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.listWidget_3.setDefaultDropAction(Qt.MoveAction)
        self.listWidget_3.setFlow(QtWidgets.QListView.LeftToRight)
        self.listWidget_3.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_3.setFixedHeight(listHeight)
        self.listWidget_3.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.horizontalLayout_5.addWidget(self.listWidget_3)

        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.setDragEnabled(True)
        self.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.listWidget.setDefaultDropAction(Qt.MoveAction)
        self.listWidget.setFlow(QtWidgets.QListView.LeftToRight)
        self.listWidget.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.listWidget.setFixedHeight(listHeight)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.horizontalLayout_3.addWidget(self.listWidget)

        self.listWidget_2 = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_2.sizePolicy().hasHeightForWidth())
        self.listWidget_2.setSizePolicy(sizePolicy)
        self.listWidget_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.listWidget_2.setDragEnabled(True)
        self.listWidget_2.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.listWidget_2.setDefaultDropAction(Qt.MoveAction)
        self.listWidget_2.setFlow(QtWidgets.QListView.LeftToRight)
        self.listWidget_2.setFixedHeight(listHeight)
        self.listWidget_2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_2.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.horizontalLayout_4.addWidget(self.listWidget_2)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 905, 26))
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progressBar.setFixedHeight(20)
        self.statusbar.addPermanentWidget(self.progressBar)
        self.setStatusBar(self.statusbar)

    # 保存该片段到本地
    def saveItem(self):
        self.returnIDLE()
        item = self.cur_listWidget.currentItem()
        self.saveitem = item
        if item.video:
            self.saveObject = SaveTemp(item.video.copy())
        else:
            self.saveObject = SaveTemp(item.audio.copy())
        item.setFlags(item.flags() & ((Qt.ItemIsSelectable | Qt.ItemIsEnabled) ^ 0xff))
        self.saveThread = QThread()
        self.saveObject.moveToThread(self.saveThread)
        self.saveObject.finish_process.connect(self.finishSave)
        self.saveObject.message.connect(self.thread_message)
        self.saveObject.progress.connect(self.thread_progress)
        self.saveThread.started.connect(self.saveObject.process)
        self.progressBar.setVisible(True)
        self.saveThread.start()

    def setupData(self):
        # 记录当前播放视频、音频
        self.audio_backend = None
        self.video_backend = None
        # 切分起始结束时刻
        self.cutter_end = 0
        self.cutter_start = 0
        # 当前选中的行
        self.cur_listWidget = None

        # 播放、处理音视频的子线程及相应对象
        self.video = None
        self.audio = None
        self.calthread = None
        self.audioThread = None
        self.compositeObject = None
        self.compositeThread = None
        # 状态变量
        self.flag = 0
        self.state = State.IDLE
        self.saveObject = None
        self.saveThread = None

        # 要处理的所有片段
        self.items, self.items_2, self.items_3 = [], [], []
        self.saveitem = None

    # 各信号与触发的相应函数绑定
    def setupSlot(self):
        self.pushButton.clicked.connect(self.openAudio)
        self.pushButton_7.clicked.connect(self.openTarget)
        self.pushButton_6.clicked.connect(self.openBackground)
        self.pushButton_8.clicked.connect(self.cut)
        self.pushButton_10.clicked.connect(self.copySelected)
        self.pushButton_3.clicked.connect(self.setupPara)
        self.pushButton_2.clicked.connect(self.play)
        self.pushButton_4.clicked.connect(self.setStart)
        self.horizontalSlider.sliderMoved.connect(self.setPosition)
        self.horizontalSlider.sliderMoved.connect(self.setApos)
        self.horizontalSlider.sliderReleased.connect(self.openGLWidget.update)
        self.listWidget.itemDoubleClicked.connect(self.setupTarget)
        self.listWidget_2.itemDoubleClicked.connect(self.setupTarget)
        self.listWidget_3.itemDoubleClicked.connect(self.setupTarget)
        self.listWidget.customContextMenuRequested.connect(self.createContextMenu)
        self.listWidget_2.customContextMenuRequested.connect(self.createContextMenu2)
        self.listWidget_3.customContextMenuRequested.connect(self.createContextMenu3)

    def __init__(self):
        super(Window, self).__init__()
        self.setupData()
        self.setupUi()
        self.setupSlot()

    # 设置切分起始时间并显示
    def setStart(self):
        self.cutter_start = self.video.t
        duration = self.video_backend.duration if self.video_backend else self.audio_backend.duration
        currentTime = QTime(int(self.cutter_start/3600) % 60, int(self.cutter_start/60) % 60, self.cutter_start % 60, (self.cutter_start*1000) % 1000)
        format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
        tStr = currentTime.toString(format)
        self.statusbar.showMessage("设置起始时间%s" % tStr, 1000)

    # 关闭窗口前清理子线程
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.stop.emit()
        if self.calthread:
            self.calthread.quit()
            self.calthread.wait()
        if self.audioThread:
            self.audioThread.quit()
            self.audioThread.wait()
        super().closeEvent(a0)

    # 重复添加选中的item
    def copySelected(self):
        self.cur_listWidget.addItem(self.cur_listWidget.currentItem().copy())

    # 在对话框里设置处理参数
    def setupPara(self):

        def choose():
            if self.gauss.isChecked():
                self.gauss_target.setEnabled(True)
                self.gauss_background.setEnabled(True)
            else:
                self.gauss_target.setEnabled(False)
                self.gauss_background.setEnabled(False)

        # 至少选择了目标和背景才能在对话框里设置处理参数
        if self.listWidget.count() and self.listWidget_2.count():
            self.dialog = QtWidgets.QDialog(self)
            self.dialog.setAttribute(Qt.WA_DeleteOnClose)
            self.dialog.setWindowModality(Qt.WindowModal)
            self.dialog.setWindowTitle("准备合成")
            gridLayout = QtWidgets.QGridLayout(self.dialog)
            self.dialog.setLayout(gridLayout)
            self.check = QtWidgets.QCheckBox("全局分身效果", self.dialog)
            self.gauss = QtWidgets.QCheckBox("高斯模糊", self.dialog)
            self.gauss_target = QtWidgets.QCheckBox("目标", self.dialog)
            self.gauss_background = QtWidgets.QCheckBox("背景", self.dialog)
            self.tiktok = QtWidgets.QCheckBox("抖音效果", self.dialog)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

            self.gauss_target.setSizePolicy(sizePolicy)
            self.gauss_background.setSizePolicy(sizePolicy)
            self.check.setSizePolicy(sizePolicy)
            self.gauss.setSizePolicy(sizePolicy)
            self.tiktok.setSizePolicy(sizePolicy)
            self.gauss.stateChanged.connect(choose)
            self.gauss_target.setEnabled(False)
            self.gauss_background.setEnabled(False)
            dialogbtns = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
            dialogbtns.button(QDialogButtonBox.Cancel).setText("取消")
            dialogbtns.button(QDialogButtonBox.Ok).setText("开始")
            dialogbtns.rejected.connect(self.dialog.reject)
            dialogbtns.accepted.connect(self.dialog.accept)
            dialogbtns.accepted.connect(self.composite)
            dialogbtns.setSizePolicy(sizePolicy)
            label = QtWidgets.QLabel(self.dialog)
            label.setText("默认分辨率 1280x720")

            gridLayout.addWidget(self.check, 0, 0, 1, 1)
            gridLayout.addWidget(dialogbtns, 4, 0, 1, 3)
            gridLayout.addWidget(label, 3, 0, 1, 1)
            gridLayout.addWidget(self.gauss, 1, 0, 1, 1)
            gridLayout.addWidget(self.tiktok, 2, 0, 1, 1)
            gridLayout.addWidget(self.gauss_target, 1, 1, 1, 1)
            gridLayout.addWidget(self.gauss_background, 1, 2, 1, 1)

            self.dialog.resize(400, 300)
            self.dialog.show()

    def finishSave(self):
        self.progressBar.setVisible(False)
        self.saveitem.setFlags(self.saveitem.flags()|Qt.ItemIsEnabled|Qt.ItemIsSelectable)
        self.saveThread.quit()
        self.saveThread.wait()

    # 若当前进度大于切分起始时间，则对当前播放片段原地切分
    def cut(self):
        if self.video.t <= self.cutter_start:
            QMessageBox.critical(self, "警告", "请在起始时间之后切分")
        elif self.video.t > self.cutter_start:

            if self.video_backend and self.audio_backend:
                self.video_backend = self.video_backend.subclip(self.cutter_start, self.video.t)
                self.audio_backend = self.video_backend.audio
                self.set_video.emit(self.video_backend)
                self.set_audio.emit(self.audio_backend, self.audio_backend.fps, int(1.0 / self.video_backend.fps * self.audio_backend.fps), 2)
                self.cur_listWidget.currentItem().setClip(self.video_backend, self.audio_backend)
                self.durationChanged(self.video_backend.duration)
            elif self.video_backend and not self.audio_backend:
                self.video_backend = self.video_backend.subclip(self.cutter_start, self.video.t)
                self.set_video.emit(self.video_backend)
                self.cur_listWidget.currentItem().setClip(self.video_backend, self.audio_backend)
                self.durationChanged(self.video_backend.duration)
            elif not self.video_backend and self.audio_backend:
                self.audio_backend = self.audio_backend.subclip(self.cutter_start, self.video.t)
                self.set_video.emit(self.video_backend)
                self.set_audio.emit(self.audio_backend, self.audio_backend.fps, int(1.0 / self.video.fps * self.audio_backend.fps), 2)
                self.cur_listWidget.currentItem().setClip(self.video_backend, self.audio_backend)
                self.durationChanged(self.audio_backend.duration)

        self.cutter_start = 0

    # 准备生成
    def composite(self):
        # 为防止读写冲突，保护所有待处理片段，先重置回初始状态
        self.returnIDLE()
        targets, backgrounds, audios = [], [], []
        # 将所有待处理片段的item置为不可选中且不可用，并存储这些片段准备让子线程处理
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            targets.append(item.video)
            self.items.append(item)
            item.setFlags(item.flags() & ( (Qt.ItemIsSelectable|Qt.ItemIsEnabled)^0xff))
        for i in range(self.listWidget_2.count()):
            item_2 = self.listWidget_2.item(i)
            backgrounds.append(item_2.video)
            self.items_2.append(item_2)
            item_2.setFlags(item.flags() & ((Qt.ItemIsSelectable | Qt.ItemIsEnabled) ^ 0xff))
        for i in range(self.listWidget_3.count()):
            item_3 = self.listWidget_3.item(i)
            audios.append(item_3.audio)
            self.items_3.append(item_3)
            item_3.setFlags(item.flags() & ((Qt.ItemIsSelectable | Qt.ItemIsEnabled) ^ 0xff))

        # 传递待处理片段及相关参数，绑定开始、结束、处理进度的函数
        self.compositeObject = CompositeObject(targets, backgrounds, audios, triple=self.check.isChecked(),
                                               gauss=self.gauss.isChecked(), tiktok=self.tiktok.isChecked(),
                                               gauss_target=self.gauss_target.isChecked(), gauss_background=self.gauss_background.isChecked())
        self.compositeThread = QThread()
        self.compositeObject.moveToThread(self.compositeThread)
        self.compositeThread.started.connect(self.compositeObject.process)
        self.compositeObject.message.connect(self.thread_message)
        self.compositeObject.progress.connect(self.thread_progress)
        self.progressBar.setVisible(True)
        self.compositeObject.finish_process.connect(self.finishComposite)
        self.compositeThread.start()

    # 显示消息和进度
    def thread_message(self, value):
        self.statusbar.showMessage(value)

    def thread_progress(self, value):
        self.progressBar.setValue(value)

    # 状态改变时需要的操作
    def fitState(self):
        if self.state == State.PLAYING:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.pushButton_8.setEnabled(False)
        elif self.state == State.FINISHED:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.state == State.PAUSE:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.pushButton_8.setEnabled(True)
        elif self.state == State.READY:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_8.setEnabled(True)
            self.pushButton_10.setEnabled(True)
            self.pushButton_4.setEnabled(True)
        elif self.state == State.IDLE:
            self.audio_backend = None
            self.video_backend = None
            self.horizontalSlider.setRange(0, 0)
            self.updateDurationInfo(0)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_10.setEnabled(False)
            self.pushButton_8.setEnabled(False)

    # 各片段右键菜单所能进行的简单预处理
    def createContextMenu(self, pos):
        self.cur_listWidget = self.listWidget
        curItem = self.listWidget.itemAt(pos)
        if not curItem or self.state == State.PLAYING:
            return
        popMenu = QMenu(self)
        deleteAction = QAction("删除", self)
        titokAction = QAction("tiktok效果", self)
        popMenu.addAction(deleteAction)
        popMenu.addAction(titokAction)
        deleteAction.triggered.connect(self.deleteItem)
        titokAction.triggered.connect(self.video.tiktok)
        saveAction = QAction("保存本地", self)
        popMenu.addAction(saveAction)
        saveAction.triggered.connect(self.saveItem)
        if curItem.audio:
            AddMusic = QAction("提取音频")
            popMenu.addAction(AddMusic)
            AddMusic.triggered.connect(self.addToAudio)
        popMenu.exec(QCursor.pos())

    def createContextMenu2(self, pos):
        self.cur_listWidget = self.listWidget_2
        curItem = self.listWidget_2.itemAt(pos)
        if not curItem or self.state == State.PLAYING:
            return
        popMenu = QMenu(self)
        deleteAction = QAction("删除", self)
        titokAction = QAction("tiktok效果", self)
        popMenu.addAction(deleteAction)
        popMenu.addAction(titokAction)
        deleteAction.triggered.connect(self.deleteItem)
        titokAction.triggered.connect(self.video.tiktok)
        saveAction = QAction("保存本地", self)
        popMenu.addAction(saveAction)
        saveAction.triggered.connect(self.saveItem)
        if curItem.audio:
            AddMusic = QAction("提取音频")
            popMenu.addAction(AddMusic)
            AddMusic.triggered.connect(self.addToAudio)
        popMenu.exec(QCursor.pos())

    def createContextMenu3(self, pos):
        self.cur_listWidget = self.listWidget_3
        curItem = self.listWidget_3.itemAt(pos)
        if not curItem or self.state == State.PLAYING:
            return
        popMenu = QMenu(self)
        deleteAction = QAction("删除", self)
        popMenu.addAction(deleteAction)
        saveAction = QAction("保存本地", self)
        popMenu.addAction(saveAction)
        saveAction.triggered.connect(self.saveItem)
        deleteAction.triggered.connect(self.deleteItem)
        popMenu.exec(QCursor.pos())

    # 回退到初始状态
    def returnIDLE(self):
        if self.calthread.isRunning()and self.video.timer.isActive():
            self.stop.emit()
        self.state = State.IDLE
        self.fitState()

    # 删除item，若删除的是现在正在播放的，回退到初始状态以防止错误
    def deleteItem(self):
        if self.video_backend:
            if self.cur_listWidget.currentItem().video == self.video_backend:
                self.returnIDLE()
        elif self.audio_backend:
            if self.cur_listWidget.currentItem().audio == self.audio_backend:
                self.returnIDLE()
        ditem = self.cur_listWidget.takeItem(self.cur_listWidget.row(self.cur_listWidget.currentItem()))
        del ditem

    # 将目标或背景的音频添加为音频行的item
    def addToAudio(self):
        newName = "(Audio)"+self.cur_listWidget.currentItem().text
        item = MyListWidgetItem(clipName=newName, video=None, audio=self.cur_listWidget.currentItem().audio)
        self.listWidget_3.addItem(item)
        self.setupMedia(item)

    # 结束生成后，使相关item重新可交互并清除工作线程
    def finishComposite(self):
        self.progressBar.setVisible(False)
        for item in self.items:
            item.setFlags(item.flags()|Qt.ItemIsEnabled|Qt.ItemIsSelectable)
        for item in self.items_2:
            item.setFlags(item.flags()|Qt.ItemIsEnabled|Qt.ItemIsSelectable)
        for item in self.items_3:
            item.setFlags(item.flags()|Qt.ItemIsEnabled|Qt.ItemIsSelectable)
        self.compositeThread.quit()
        self.compositeThread.wait()

    # 播放结束
    def processFinish(self):
        self.state = State.FINISHED
        self.fitState()

    # 播放进度改变时移动进度条滑块并记录时间
    def positionChanged(self, position):
        self.horizontalSlider.setValue(position)
        self.updateDurationInfo(position / 10)

    # 播放对象改变时重设时间信息
    def durationChanged(self, duration):
        self.horizontalSlider.setRange(0, duration * 10)
        self.updateDurationInfo(0)

    # 控制视频播放进度
    def setPosition(self, position):
        self.video.setT(position / 10)

    # 控制音频播放进度
    def setApos(self, position):
        if self.audio_backend:
            self.audio.setIndex(int(position / 10 * self.audio.fps / self.audio.buffersize))

    # 更新时间信息
    def updateDurationInfo(self, currentInfo):
        # 正确计算时长
        if self.video_backend:
            duration = self.video_backend.duration
        elif self.audio_backend:
            duration = self.audio_backend.duration
        else:
            duration = 0
        # 计算当前时间和总时间并显示
        if currentInfo or duration:
            currentTime = QTime((currentInfo / 3600) % 60, (currentInfo / 60) % 60,
                                currentInfo % 60, (currentInfo * 1000) % 1000)
            totalTime = QTime((duration / 3600) % 60, (duration / 60) % 60,
                              duration % 60, (duration * 1000) % 1000)

            format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        else:
            tStr = ""
        self.label.setText(tStr)

    # 切换要播放的item
    def setupTarget(self, item):
        if self.state != State.IDLE:
            self.stop.emit()
        self.setupMedia(item)
        self.fitState()
        self.cur_listWidget = item.listWidget()

    # 打开目标文件
    def openTarget(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath(),
                                                  "Video(*.mp4;*.wmv;*.rmvb;*.avi;*.mkv;*.mov;*.mpeg;*.flv;*.rm;*.mpeg;*.mpg)")
        if fileName != '':
            if self.state != State.IDLE:
                self.stop.emit()

            v = VideoFileClip(fileName)

            item = MyListWidgetItem(fileName.split("/")[-1], v, v.audio)
            self.listWidget.addItem(item)
            self.listWidget.setCurrentItem(item)
            self.cur_listWidget = self.listWidget
            self.setupMedia(item)

    # 打开背景文件
    def openBackground(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath(),
                                                  "Video(*.mp4;*.wmv;*.rmvb;*.avi;*.mkv;*.mov;*.mpeg;*.flv;*.rm;*.mpeg;*.mpg)")
        if fileName != '':
            if self.state != State.IDLE:
                self.stop.emit()

            v = VideoFileClip(fileName)
            item = MyListWidgetItem(fileName.split("/")[-1], v, v.audio)

            self.listWidget_2.addItem(item)
            self.listWidget_2.setCurrentItem(item)
            self.cur_listWidget = self.listWidget_2
            self.setupMedia(item)

    # 打开音频文件
    def openAudio(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Audio", QDir.homePath(),
                                                  "Audio(*.mp3;*.wav;*.ogg;*.wma;)")
        if fileName != '':
            if self.state != State.IDLE:
                self.stop.emit()
            a = AudioFileClip(fileName)
            item = MyListWidgetItem(clipName=fileName.split("/")[-1], video=None, audio=a)

            self.listWidget_3.addItem(item)
            self.listWidget_3.setCurrentItem(item)
            self.cur_listWidget = self.listWidget_3
            self.setupMedia(item)

    # 设置要播放的视频、音频信息
    def setupMedia(self, item):
        duration = item.video.duration if item.video else item.audio.duration
        self.video_backend = item.video
        self.audio_backend = item.audio
        # 还没有播放过片段，建立子线程并初始化相应对象
        if self.flag == 0:
            self.video = Video(item.video)
            self.durationChanged(duration)
            self.calthread = QThread()
            self.video.moveToThread(self.calthread)
            self.video.t_changed.connect(self.positionChanged)
            self.stop.connect(self.video.stop)
            self.pause.connect(self.video.pause)
            self.resume.connect(self.video.resume)
            self.video.finish.connect(self.processFinish)
            self.calthread.started.connect(self.video.work)
            self.set_video.connect(self.video.setClip)
            self.audioThread = QThread()
            if self.audio_backend:
                self.audio = Audio(clip=item.audio, fps=item.audio.fps, buffersize=int(1.0 / self.video.fps * item.audio. fps), nbytes=2)
            else:
                self.audio = Audio(clip=None, fps=0, buffersize=0, nbytes=0)
            self.audio.moveToThread(self.audioThread)
            self.audioThread.started.connect(self.audio.work)
            self.set_audio.connect(self.audio.setClip)
        # 已经播放过，此时视频线程与音频线程均存在，设置相应对象信息即可
        else:
            v_fps = item.video.fps if item.video else 30

            if item.video and item.audio:
                self.durationChanged(duration)
                self.set_video.emit(item.video)
                self.set_audio.emit(item.audio, item.audio.fps,
                                    int(1.0 / v_fps * item.audio.fps), 2)
            elif item.video and not item.audio:
                self.set_video.emit(item.video)
                self.set_audio.emit(None, 44100, 0, 2)
                self.durationChanged(duration)
            else:
                self.set_video.emit(item.video)
                self.durationChanged(item.audio.duration)
                self.set_audio.emit(item.audio, item.audio.fps,
                                    int(1.0 / v_fps * item.audio.fps), 2)

        self.state = State.READY
        self.fitState()

    # 点击播放键时根据状态实施相应行为
    def play(self):
        self.flag += 1
        if self.state in (State.FINISHED, State.READY):
            self.state = State.PLAYING
            self.fitState()
            if self.flag == 1:
                self.calthread.start()
                self.audioThread.start()
            else:
                self.resume.emit()

        elif self.state == State.PLAYING:
            self.state = State.PAUSE
            self.pause.emit()
            self.fitState()
        elif self.state == State.PAUSE:
            self.resume.emit()
            self.state = State.PLAYING
            self.fitState()


# 用于播放视频的自定义控件
class MyOpenGLWidget(QOpenGLWidget):

    def __init__(self, parent=None):
        super(MyOpenGLWidget, self).__init__(parent)

    # 播放状态下不断从队列获得要播放的视频数据，而暂停状态下只在需要时重绘当前进度的画面
    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        if not q.empty() and ui.state == State.PLAYING:
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawImage(QRect(0, 0, self.width(), self.height()), q.get())
            painter.end()
        elif ui.state == State.PAUSE and ui.video_backend:
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            im = ui.video.clip.get_frame(ui.video.t)
            img = QImage(im.data, im.shape[1], im.shape[0], im.shape[1] * 3, QImage.Format_RGB888)
            painter.drawImage(QRect(0, 0, self.width(), self.height()), img)
            painter.end()



# 在子线程中定时读取视频数据的对象
class Video(QObject):
    finish = pyqtSignal()
    t_changed = pyqtSignal(int)

    # 初始化视频信息
    def __init__(self, clip):
        super(Video, self).__init__()
        self.clip = clip
        self.t = 0
        self.fps = self.clip.fps if self.clip else 30
        self.stride = 1 / self.fps
        self.duration = self.clip.duration if self.clip else ui.audio_backend.duration

    # 设置定时器，定时画视频帧并提醒音频对象同步读取
    def work(self):
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        if self.clip:
            self.timer.timeout.connect(ui.openGLWidget.update)
        self.timer.timeout.connect(self.updatetime)
        self.timer.timeout.connect(ui.audio.update)
        self.timer.setInterval(1000*self.stride)
        self.timer.start()

    # 根据进度入队新视频数据，若超时长则结束
    def updatetime(self):
        if self.t < self.duration:
            if self.clip:
                im = self.clip.get_frame(self.t)
                img = QImage(im.data, im.shape[1], im.shape[0], im.shape[1] * 3, QImage.Format_RGB888)
                q.put(img)
            self.setT(self.t + self.stride)
        else:
            self.stop()
            self.finish.emit()

    def pause(self):
        self.timer.stop()

        self.t -= (2*self.stride)

    def resume(self):
        self.timer.start(1000*self.stride)

    def stop(self):
        self.timer.stop()
        self.setT(0)


    # 某一片段的抖音效果
    def tiktok(self):
        if isinstance(self.clip, VideoFileClip):
            self.clip = self.clip.fl_image(tiktok_effect)
            ui.cur_listWidget.currentItem().setClip(self.clip, self.clip.audio)
            ui.openGLWidget.update()

    # 设置要播放的新视频
    def setClip(self, clip):
        self.clip = clip
        self.setT(0)
        self.fps = self.clip.fps if self.clip else 30
        self.stride = 1 / self.fps
        self.duration = self.clip.duration if self.clip else ui.audio_backend.duration
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        if self.clip:
            self.timer.timeout.connect(ui.openGLWidget.update)
        self.timer.timeout.connect(self.updatetime)
        self.timer.timeout.connect(ui.audio.update)
        self.timer.setInterval(1000 * self.stride)

    # 调整播放进度
    def setT(self, t):
        self.t = t

        self.t_changed.emit(self.t * 10)


# 应用启动设置
if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei", 8)
    app.setFont(font)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    q = queue.Queue()
    QSurfaceFormat.setDefaultFormat(fmt)
    ui = Window()
    ui.setObjectName("ui")
    ui.resize(800, 800)
    ui.show()

    sys.exit(app.exec_())





