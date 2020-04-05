import queue
import sys
import time
import qdarkstyle
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDir, QObject, pyqtSignal, QThread, QTimer, Qt, QTime, QPoint, QRect, QSize, QEvent
from PyQt5.QtGui import QSurfaceFormat, QPainter, QImage, QOpenGLWindow, QIcon, QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QSizePolicy, QProgressBar, \
    QFileDialog, QRubberBand, QOpenGLWidget, QListWidgetItem, QListWidget, QMessageBox, QMenu, QAction, QWidget, \
    QStatusBar
from audio import Audio
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx import speedx
from moviepy.video.io.VideoFileClip import VideoFileClip

from utils import State, tiktok_effect, MyListWidgetItem, listHeight


# noinspection PyAttributeOutsideInit
class Window(QMainWindow):
    pause = pyqtSignal()
    resume = pyqtSignal()
    stop = pyqtSignal()
    set_video = pyqtSignal(object)
    set_audio = pyqtSignal(object, int, int, int)
    d_changed = pyqtSignal()

    def setupUi(self):
        self.setWindowTitle("VideoEditor")
        self.centralwidget = QWidget(self)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()

        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setRange(0, 0)
        self.horizontalLayout_3.addWidget(self.horizontalSlider)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("")

        self.horizontalLayout_3.addWidget(self.label)

        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)
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
        self.pushButton_9 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_9)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.horizontalLayout.addWidget(self.pushButton_5)
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
        self.pushButton_9.setText("tiktok")
        self.pushButton_5.setText("影流之主")
        self.pushButton_8.setText("原地切分")
        self.pushButton_10.setText("重复")
        self.pushButton_3.setText("生成")
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_9.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)
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
        self.gridLayout.addWidget(self.listWidget_3, 5, 0, 1, 1)

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
        self.gridLayout.addWidget(self.listWidget, 3, 0, 1, 1)

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
        self.gridLayout.addWidget(self.listWidget_2, 4, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 905, 26))
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.statusbar.addPermanentWidget(self.progressBar)
        self.setStatusBar(self.statusbar)

    def setupData(self):
        self.final_clip = None
        self.audio_backend = None
        self.video_backend = None
        self.audio = None
        self.cutter_end = 0
        self.cutter_start = 0
        self.product = ''
        self.cur_listWidget = None
        self.flag = 0
        self.calthread = None
        self.video = None
        self.audio = None
        self.audioThread = None
        self.state = State.IDLE

    def setupSlot(self):
        self.pushButton.clicked.connect(self.openAudio)
        self.pushButton_7.clicked.connect(self.openTarget)
        self.pushButton_6.clicked.connect(self.openBackground)
        self.pushButton_8.clicked.connect(self.cut)
        self.pushButton_10.clicked.connect(self.copySelected)
        # self.pushButton_3.clicked.connect(self.process)
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

    def setStart(self):
        self.cutter_start = self.video.t
        duration = self.video_backend.duration if self.video_backend else self.audio_backend.duration
        currentTime = QTime(int(self.cutter_start/3600) % 60, int(self.cutter_start/60) % 60, self.cutter_start % 60, (self.cutter_start*1000) % 1000)
        format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
        tStr = currentTime.toString(format)
        self.statusbar.showMessage("设置起始时间%s" % tStr, 1000)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.stop.emit()
        if self.calthread:
            self.calthread.quit()
            self.calthread.wait()
        if self.audioThread:
            self.audioThread.quit()
            self.audioThread.wait()
        super().closeEvent(a0)

    def copySelected(self):
        self.cur_listWidget.addItem(self.cur_listWidget.currentItem().copy())

    def cut(self):
        if self.video.t <= self.cutter_start:
            QMessageBox.critical(self, "警告", "请在起始时间之后切分")
        elif self.video.t > self.cutter_start:

            if self.video_backend and self.audio_backend:
                self.video_backend = self.video_backend.subclip(self.cutter_start, self.video.t)
                self.audio_backend = self.video_backend.audio
                self.set_video.emit(self.video_backend)
                self.set_audio.emit(self.audio_backend, self.audio_backend.fps, int(1.0 / self.video_backend.fps * self.audio_backend.fps), 2)
                self.cur_listWidget.currentItem().setClip(self.video_backend ,self.audio_backend)
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


    def getClip(self):
        if self.video_backend:
            return self.video_backend
        else:
            return self.audio_backend

    def fitState(self):
        if self.state == State.PLAYING:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.pushButton_8.setEnabled(False)

        elif self.state in (State.PAUSE, State.IDLE, State.FINISHED):
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.pushButton_8.setEnabled(True)
        elif self.state == State.READY:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_9.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_8.setEnabled(True)
            self.pushButton_10.setEnabled(True)
            self.pushButton_4.setEnabled(True)

    def createContextMenu(self, pos):
        self.cur_listWidget = self.listWidget
        curItem = self.listWidget.itemAt(pos)
        if not curItem:
            return
        popMenu = QMenu(self)
        deleteAction = QAction("删除",self)
        saveAction = QAction("保存本地", self)
        popMenu.addAction(deleteAction)
        popMenu.addAction(saveAction)
        deleteAction.triggered.connect(self.deleteItem)
        saveAction.triggered.connect(self.saveItem)
        popMenu.exec(QCursor.pos())

    def createContextMenu2(self, pos):
        self.cur_listWidget = self.listWidget_2
        curItem = self.listWidget_2.itemAt(pos)
        if not curItem:
            return
        popMenu = QMenu(self)
        deleteAction = QAction("删除",self)
        popMenu.addAction(deleteAction)
        deleteAction.triggered.connect(self.deleteItem)
        popMenu.exec(QCursor.pos())

    def createContextMenu3(self, pos):
        self.cur_listWidget = self.listWidget_3
        curItem = self.listWidget_3.itemAt(pos)
        if not curItem:
            return
        popMenu = QMenu(self)
        deleteAction = QAction("删除",self)
        popMenu.addAction(deleteAction)
        deleteAction.triggered.connect(self.deleteItem)
        popMenu.exec(QCursor.pos())


    def deleteItem(self):
        ditem = self.cur_listWidget.takeItem(self.cur_listWidget.row(self.cur_listWidget.currentItem()))
        del ditem

    def saveItem(self):
        self.cur_listWidget.currentItem().video.write_videofile(f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4')


    def processFinish(self):
        self.state = State.FINISHED
        self.fitState()

    def positionChanged(self, position):
        self.horizontalSlider.setValue(position)
        self.updateDurationInfo(position / 10)

    def durationChanged(self, duration):
        self.horizontalSlider.setRange(0, duration * 10)
        self.updateDurationInfo(0)

    def setPosition(self, position):
        self.video.setT(position / 10)

    def setApos(self, position):
        if self.audio_backend:
            self.audio.setIndex(int(position / 10 * self.audio.fps / self.audio.buffersize))

    def updateDurationInfo(self, currentInfo):
        duration = self.video_backend.duration if self.video_backend else self.audio_backend.duration
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

    def setupTarget(self, item):

        if self.state != State.IDLE:
            self.stop.emit()

        self.setupMedia(item)
        self.fitState()
        self.cur_listWidget = item.listWidget()



    def openTarget(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath(),
                                                  "Video(*.mp4;*.wmv;*.rmvb;*.avi;*.mkv)")

        if fileName != '':
            if self.state != State.IDLE:
                self.stop.emit()

            v = VideoFileClip(fileName)
            item = MyListWidgetItem(fileName.split("/")[-1], v, v.audio)

            self.listWidget.addItem(item)
            self.listWidget.setCurrentItem(item)
            self.cur_listWidget = self.listWidget
            self.setupMedia(item)

    def openBackground(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath(),
                                                  "Video(*.mp4;*.wmv;*.rmvb;*.avi;*.mkv)")
        if fileName != '':
            if self.state != State.IDLE:
                self.stop.emit()

            v = VideoFileClip(fileName)
            item = MyListWidgetItem(fileName.split("/")[-1], v, v.audio)

            self.listWidget_2.addItem(item)
            self.listWidget_2.setCurrentItem(item)
            self.cur_listWidget = self.listWidget_2
            self.setupMedia(item)

    def openAudio(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath(),
                                                  "Audio(*.mp3;*.wav;)")
        if fileName != '':
            if self.state != State.IDLE:
                self.stop.emit()
            a = AudioFileClip(fileName)
            item = MyListWidgetItem(clipName=fileName.split("/")[-1], video=None, audio=a)

            self.listWidget_3.addItem(item)
            self.listWidget_3.setCurrentItem(item)
            self.cur_listWidget = self.listWidget_3
            self.setupMedia(item)


    def setupMedia(self,item):

        duration = item.video.duration if item.video else item.audio.duration
        self.video_backend = item.video
        self.audio_backend = item.audio
        if self.flag == 0:
            self.video = Video(item.video)
            self.durationChanged(duration)
            self.calthread = QThread()
            #self.pushButton_5.clicked.connect(self.video.speed)
            self.video.moveToThread(self.calthread)
            self.video.t_changed.connect(self.positionChanged)
            self.stop.connect(self.video.stop)
            self.pause.connect(self.video.pause)
            self.resume.connect(self.video.resume)
            self.video.finish.connect(self.processFinish)
            self.calthread.started.connect(self.video.work)
            self.pushButton_9.clicked.connect(self.video.tiktok)
            self.set_video.connect(self.video.setClip)
            self.audioThread = QThread()
            if self.audio_backend:
                self.audio = Audio(clip=item.audio, fps=item.audio.fps, buffersize=int(1.0 / self.video.fps * item.audio.fps), nbytes=2)
            else:
                self.audio = Audio(clip=None, fps=0, buffersize=0, nbytes=0)
            self.audio.moveToThread(self.audioThread)
            self.audioThread.started.connect(self.audio.work)
            self.set_audio.connect(self.audio.setClip)

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

    def play(self):
        self.flag += 1
        if self.state in (State.FINISHED, State.READY):
            self.state = State.PLAYING
            self.fitState()
            if self.flag == 1:
                print("Start")
                self.calthread.start()
                self.audioThread.start()
            else:
                print("Running")
                self.resume.emit()

        elif self.state == State.PLAYING:
            print("Pause")
            self.state = State.PAUSE
            self.pause.emit()
            self.fitState()
        elif self.state == State.PAUSE:
            print("Resume")
            self.resume.emit()
            self.state = State.PLAYING
            self.fitState()


class MyOpenGLWidget(QOpenGLWidget):

    def __init__(self, parent=None):
        super(MyOpenGLWidget, self).__init__(parent)

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


class Video(QObject):
    finish = pyqtSignal()
    t_changed = pyqtSignal(int)

    def __init__(self, clip):
        super(Video, self).__init__()
        self.clip = clip
        self.t = 0
        self.fps = self.clip.fps if self.clip else 30
        self.stride = 1 / self.fps
        self.duration = self.clip.duration if self.clip else ui.audio_backend.duration


    def work(self):
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        if self.clip:
            self.timer.timeout.connect(ui.openGLWidget.update)
        self.timer.timeout.connect(self.updatetime)
        self.timer.timeout.connect(ui.audio.update)
        self.timer.setInterval(1000*self.stride)
        self.timer.start()


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

    def resume(self):
        self.timer.start(1000*self.stride)

    def speed(self):
        self.clip = speedx.speedx(self.clip, 2)

    def stop(self):
        self.setT(0)
        q.queue.clear()
        self.timer.stop()

    def tiktok(self):
        if isinstance(self.clip,VideoFileClip):
            self.clip = self.clip.fl_image(tiktok_effect)
            ui.cur_listWidget.currentItem().setClip(self.clip, self.clip.audio)


    def setClip(self, clip):
        self.clip = clip
        self.setT(0)
        self.fps = self.clip.fps if self.clip else 30
        self.stride = 1 / self.fps
        self.duration = self.clip.duration if self.clip else ui.audio_backend.duration
        del self.timer
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        if self.clip:
            self.timer.timeout.connect(ui.openGLWidget.update)
        self.timer.timeout.connect(self.updatetime)
        self.timer.timeout.connect(ui.audio.update)
        self.timer.setInterval(1000 * self.stride)

    def setT(self, t):
        self.t = t
        self.t_changed.emit(self.t * 10)


q = queue.Queue()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)
    ui = Window()
    ui.resize(800, 800)
    ui.show()

    sys.exit(app.exec_())





