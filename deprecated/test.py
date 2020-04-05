import queue
import sys
import threading
import time
from enum import Enum
import pygame as pg
import numpy as np
import sounddevice as sd
import qdarkstyle
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDir, QObject, pyqtSignal, QThread, QTimer, Qt, QBasicTimer
from PyQt5.QtGui import QSurfaceFormat, QPainter, QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QSizePolicy, QProgressBar, \
    QFileDialog, QOpenGLWidget, QWidget
from audio import audio
from moviepy.editor import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from proglog import ProgressBarLogger
from utils import State, tiktok_effect
from window3 import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    state_change = pyqtSignal()


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
        self.generator = None
        self.t = 0
        self.tt = None
        self.setupUi(self)
        self.pushButton.clicked.connect(self.openFile)
        # self.pushButton_3.clicked.connect(self.process)
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_2.clicked.connect(self.play)
        self.pushButton_9.clicked.connect(self.tiktok)
        self.horizontalSlider.setRange(0,0)
        # self.horizontalSlider.sliderMoved.connect(self.setPosition)
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Fixed)
        self.statusbar.addPermanentWidget(self.progressBar)
        self.widget = MyWidget()

        self.state_change.connect(self.fitState)
        self.widget.finish.connect(self.processfinish)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.widget.update)

        self.state = State.IDLE
        self.playObject = None
        self.playThread = None


    def tiktok(self):
        temp = time.time()
        self.video_backend = self.video_backend.fl_image(tiktok_effect)
        print("copy time: %f" % (time.time()-temp))

    def fitState(self):
        if self.state == State.PLAYING:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        elif self.state in (State.PAUSE,State.IDLE,State.FINISHED):
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def processfinish(self):
        self.state = State.FINISHED
        self.t = 0
        self.state_change.emit()

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video",
                                                  QDir.homePath(), "Video(*.mp4;*.wmv;*.rmvb;*.avi)")

        if fileName != '':
            if self.video_backend is not None:
                self.video_backend.close()
            if self.audio_backend is not None:
                self.audio_backend.close()

            self.video_backend = VideoFileClip(fileName)
            # self.video_backend = clip.resize(width=clip.w//2,height=clip.h//2)

            self.audio_backend = self.video_backend.audio
            fps = self.video_backend.fps
            duration = self.video_backend.duration
            self.tt = np.arange(0, duration, 1.0 / fps)
            self.widget.drawFrame(0)
            if self.state != State.IDLE:
                self.audio.stop()
                self.timer.stop()
                self.t = 0
                self.state = State.IDLE
                self.state_change.emit()
            else:
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)






    def play(self):
        if self.state in (State.IDLE,State.FINISHED):
            self.state = State.PLAYING
            self.state_change.emit()
            self.timer.start(1000 / self.video_backend.fps)
            if self.audio_backend is not None:
                blocksize = int(1.0 / self.video_backend.fps * self.audio_backend.fps)
                self.audio = audio(self.audio_backend, self.audio_backend.fps, blocksize, 2)
                self.audio.start()

        elif self.state == State.PLAYING:
            self.state = State.PAUSE
            self.timer.stop()
            self.audio.pause()
            self.state_change.emit()
        elif self.state == State.PAUSE:
            self.audio.resume()
            self.timer.start(1000 / self.video_backend.fps)
            self.state = State.PLAYING
            self.state_change.emit()

class MyWidget(QWidget):
    finish = pyqtSignal()
    def __init__(self):
        super(MyWidget, self).__init__()


        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

    def paintEvent(self, event):
        # print(threading.current_thread())
        if ui.state == State.PLAYING and ui.t<len(ui.tt):
            t = ui.tt[ui.t]

            self.drawFrame(t)
            ui.t += 1
            if ui.t == len(ui.tt):
                self.finish.emit()

    def drawFrame(self, t):
        print(t)
        temp = time.time()
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        im = ui.video_backend.get_frame(t)
        img = QImage(im.data, im.shape[1], im.shape[0], im.shape[1] * 3, QImage.Format_RGB888)
        # pixmap = QPixmap()
        # pixmap.convertFromImage(img)
        # painter.drawPixmap(self.geometry(), pixmap)
        painter.drawImage(self.geometry(), img)
        painter.end()
        print(time.time() - temp)

class MyOpenGL(QOpenGLWidget):
    finish = pyqtSignal()

    def __init__(self):
        super(MyOpenGL, self).__init__()

        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

    def paintEvent(self, event):
        # print(threading.current_thread())
        if ui.state == State.PLAYING and ui.t<len(ui.tt):
            t = ui.tt[ui.t]

            self.drawFrame(t)
            ui.t += 1
            if ui.t == len(ui.tt):
                self.finish.emit()

    def drawFrame(self, t):
        temp = time.time()
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        im = ui.video_backend.get_frame(t)
        img = QImage(im.data, im.shape[1], im.shape[0], im.shape[1] * 3, QImage.Format_RGB888)
        # pixmap = QPixmap()
        # pixmap.convertFromImage(img)
        # painter.drawPixmap(self.geometry(), pixmap)
        painter.drawImage(self.geometry(),img)
        painter.end()
        print(time.time()-temp)


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