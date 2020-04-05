import queue
import sys
import time

import qdarkstyle
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDir, QObject, pyqtSignal, QThread, QTimer, Qt, QTime
from PyQt5.QtGui import QSurfaceFormat, QPainter, QImage, QOpenGLWindow
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QSizePolicy, QProgressBar, \
    QFileDialog
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx import speedx
from moviepy.video.io.VideoFileClip import VideoFileClip

from audio import Audio
from utils import State, tiktok_effect
from window3 import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):

    pause = pyqtSignal()
    resume = pyqtSignal()
    stop = pyqtSignal()
    set_video = pyqtSignal(VideoFileClip)
    set_audio = pyqtSignal(AudioFileClip,int,int,int)
    d_changed = pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        self.final_clip = None
        self.audio_backend = None
        self.video_backend = None
        self.audio = None
        self.cutter_end = 0
        self.cutter_start = 0
        self.product = ''
        self.index = 0
        self.calthread = None
        self.video = None
        self.audio = None
        self.audioThread = None
        self.setupUi(self)
        self.pushButton.clicked.connect(self.openFile)

        # self.pushButton_3.clicked.connect(self.process)
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_9.setEnabled(False)
        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_2.clicked.connect(self.play)

        self.horizontalSlider.setRange(0,0)
        self.horizontalSlider.sliderMoved.connect(self.setPosition)
        self.horizontalSlider.sliderMoved.connect(self.setApos)
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Fixed)
        self.statusbar.addPermanentWidget(self.progressBar)

        self.openGLWindow = MyWindow()
        self.container = self.createWindowContainer(self.openGLWindow)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.container.sizePolicy().hasHeightForWidth())
        self.container.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.container, 0, 0, 1, 1)

        self.state = State.IDLE
        self.playObject = None
        self.playThread = None



    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)


    def fitState(self):
        if self.state == State.PLAYING:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        elif self.state in (State.PAUSE,State.IDLE,State.FINISHED):
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def processFinish(self):
        self.state = State.FINISHED
        self.fitState()

    def positionChanged(self, position):
        self.horizontalSlider.setValue(position)
        self.updateDurationInfo(position/10)

    def durationChanged(self, duration):
        self.horizontalSlider.setRange(0, duration*10)

    def setPosition(self, position):

        self.video.setT(position/10)

    def setApos(self, position):

        self.audio.setIndex(int(position/10*self.audio.fps/self.audio.buffersize))

    def updateDurationInfo(self, currentInfo):
        duration = self.video_backend.duration
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

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video",QDir.homePath(), "Video(*.mp4;*.wmv;*.rmvb;*.avi;*.mkv)")

        if fileName != '':

            if self.audio_backend is not None:
                self.audio_backend.close()

            if self.state != State.IDLE:

                self.stop.emit()
                self.state = State.IDLE
                self.fitState()
            else:
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                self.pushButton_9.setEnabled(True)

            self.video_backend = VideoFileClip(fileName)
            self.audio_backend = self.video_backend.audio
            self.durationChanged(self.video_backend.duration)
            # self.video_backend = clip.resize(width=clip.w//2,height=clip.h//2)
            if self.video is None:

                self.video = Video(self.video_backend)
                self.calthread = QThread()
                self.pushButton_5.clicked.connect(self.video.speed)
                self.video.moveToThread(self.calthread)
                self.video.t_changed.connect(self.positionChanged)
                self.stop.connect(self.video.stop)
                self.pause.connect(self.video.pause)
                self.resume.connect(self.video.resume)
                self.video.finish.connect(self.processFinish)
                self.calthread.started.connect(self.video.work)
                self.pushButton_9.clicked.connect(self.video.tiktok)
                self.set_video.connect(self.video.setClip)
            else:
                self.set_video.emit(self.video_backend)

            if self.audio is None:
                self.audioThread = QThread()
                self.audio = Audio(self.audio_backend, self.audio_backend.fps, int(1.0 / self.video_backend.fps * self.audio_backend.fps), 2)
                self.audio.moveToThread(self.audioThread)
                self.audioThread.started.connect(self.audio.work)
                self.set_audio.connect(self.audio.setClip)
            else:
                self.set_audio.emit(self.audio_backend, self.audio_backend.fps, int(1.0 / self.video_backend.fps * self.audio_backend.fps), 2)



            # self.openGLWindow.drawFrame(1)

    def play(self):
        if self.state in (State.IDLE,State.FINISHED):
            self.state = State.PLAYING
            self.fitState()
            if self.calthread.isRunning():
                self.resume.emit()
            else:
                self.calthread.start()
                self.audioThread.start()


        elif self.state == State.PLAYING:
            self.state = State.PAUSE
            self.pause.emit()

            self.fitState()
        elif self.state == State.PAUSE:

            self.resume.emit()
            self.state = State.PLAYING
            self.fitState()


class MyWindow(QOpenGLWindow):

    def __init__(self):
        super(MyWindow, self).__init__()

    def initializeGL(self) -> None:
        pass

    def resizeGL(self, w: int, h: int) -> None:
        super().resizeGL(w, h)

    def paintGL(self):
        temp = time.time()
        # print(threading.active_count())
        if not q.empty():
            painter = QPainter()
            painter.begin(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            painter.drawImage(self.geometry(), q.get())
            painter.end()
        #print(time.time()-temp)
    '''
    def drawFrame(self, t):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        im = ui.video_backend.get_frame(t)
        img = QImage(im.data, im.shape[1], im.shape[0], im.shape[1] * 3, QImage.Format_RGB888)
        painter.drawImage(self.geometry(), img)
        painter.end()
        
    '''


class Video(QObject):
    finish = pyqtSignal()
    t_changed = pyqtSignal(int)
    def __init__(self, clip):
        super(Video, self).__init__()
        self.clip = clip
        self.t = 0
        self.stride = 1/self.clip.fps

    def work(self):
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(ui.openGLWindow.update)
        self.timer.timeout.connect(self.updatetime)
        self.timer.timeout.connect(ui.audio.update)
        self.timer.setInterval(1000/self.clip.fps)
        self.timer.start()

    def updatetime(self):
        #print(threading.current_thread())
        if self.t < self.clip.duration:
            im = self.clip.get_frame(self.t)
            print(self.t)
            img = QImage(im.data, im.shape[1], im.shape[0], im.shape[1] * 3, QImage.Format_RGB888)
            q.put(img)
            self.setT(self.t+self.stride)

        else:
            self.stop()
            self.finish.emit()

    def pause(self):
        self.timer.stop()

    def resume(self):
        self.timer.start(1000/self.clip.fps)

    def speed(self):
        self.clip = speedx.speedx(self.clip,2)
    def stop(self):
        self.setT(0)

        q.queue.clear()
        self.timer.stop()

    def tiktok(self):
        self.clip = self.clip.fl_image(tiktok_effect)

    def setClip(self,clip):
        self.clip.close()
        self.clip = clip
        self.setT(0)
        self.stride = 1/self.clip.fps

    def setT(self, t):
        self.t = t
        self.t_changed.emit(self.t*10)

q = queue.Queue(maxsize=30)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
   fmt = QSurfaceFormat()
   fmt.setSamples(4)
   QSurfaceFormat.setDefaultFormat(fmt)
   ui = Window()
   ui.resize(800, 600)
   ui.show()

   sys.exit(app.exec_())

