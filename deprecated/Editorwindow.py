import sys

import qdarkstyle
import time
from PyQt5.QtCore import QDir, QUrl, QObject, pyqtSignal, QThread
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QStyle, QSlider, QLabel, QSizePolicy, QProgressBar, \
    QHBoxLayout, QVBoxLayout, QFileDialog, QRubberBand
from moviepy.video.io.VideoFileClip import VideoFileClip
from proglog import ProgressBarLogger
from window import Ui_MainWindow
from window1 import Ui_MainWindow1


class Window(QMainWindow, Ui_MainWindow1):
    final_clip = None
    video_backend = None
    cutter_end = 0
    cutter_start = 0
    withaudio = True

    def __init__(self):
        super(Window, self).__init__()

        self.setupUi(self)
        self.mediaPlayer = QMediaPlayer()
        self.pushButton.clicked.connect(self.openFile)

        self.pushButton_3.clicked.connect(self.process)
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)

        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_2.clicked.connect(self.play)

        self.horizontalSlider.setRange(0,0)
        self.horizontalSlider.setStatusTip("slider")
        self.horizontalSlider.sliderMoved.connect(self.setPosition)

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Fixed)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Fixed)
        self.statusbar.addPermanentWidget(self.label)
        self.statusbar.addPermanentWidget(self.progressBar)

        self.mediaPlayer.setVideoOutput(self.widget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)


    def changeChannel(self):
        Window.withaudio = not Window.withaudio

        self.pushButton_5.setText("有声") if Window.withaudio else self.pushButton_5.setText("无声")

    def setStart(self):
        Window.cutter_start = self.mediaPlayer.position()/1000


    def process(self):

        Window.cutter_end = self.mediaPlayer.position()/1000
        self.progressBar.setVisible(True)
        self.threadObject = ProcessObject()

        self.subThread = QThread()
        self.threadObject.moveToThread(self.subThread)
        self.subThread.started.connect(self.threadObject.process_work)
        self.threadObject.finish_process.connect(self.clearThread)
        self.threadObject.message.connect(self.thread_message)
        self.threadObject.progress.connect(self.thread_progress)

        self.subThread.start()
        if self.subThread.isRunning():
            self.pushButton_3.setEnabled(False)


    def thread_message(self, value):
        self.statusbar.showMessage(value)

    def thread_progress(self, value):
        self.progressBar.setValue(value)

    def clearThread(self):
        self.progressBar.setVisible(False)
        self.pushButton_3.setEnabled(True)
        self.subThread.quit()


    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath(),"Video(*.mp4;*.wmv;*.rmvb;*.avi);;Audio(*.mp3;*.wav)")

        if fileName != '':

            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.pushButton_2.setEnabled(True)
            Window.video_backend = VideoFileClip(fileName)
            self.pushButton_3.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_4.setEnabled(True)



    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.pushButton_2.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.pushButton_2.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.horizontalSlider.setValue(position)
        print(self.horizontalSlider.pageStep())
        print(self.horizontalSlider.singleStep())
    def durationChanged(self, duration):

        self.horizontalSlider.setRange(0, duration)


    def setPosition(self, position):

        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.pushButton.setEnabled(False)
        self.label.setText("Error: %s" % self.mediaPlayer.errorString())


class ProcessObject(QObject):  # 用于子线程的类
    finish_process = pyqtSignal()  # 处理图片结束的信号
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    def __init__(self, parent=None):
        super(ProcessObject, self).__init__(parent)  # 显式调用父类构造函数

    def process_work(self):

        my_logger = MyBarLogger(self.message, self.progress)

        Window.final_clip = Window.video_backend.subclip(Window.cutter_start,Window.cutter_end) \
            if Window.withaudio else Window.video_backend.subclip(Window.cutter_start,Window.cutter_end).without_audio()

        Window.final_clip.write_videofile(
            f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4',
            fps=30,
            codec='mpeg4',
            bitrate="8000k",
            audio_codec="libmp3lame",
            threads=4,
            logger=my_logger
        )

        self.finish_process.emit()  # 处理图片结束信号发射

class MyBarLogger(ProgressBarLogger):

    def __init__(self, message, progress):
        self.message = message
        self.progress = progress
        super(MyBarLogger, self).__init__()

    def callback(self, **changes):
        bars = self.state.get('bars')
        index = len(bars.values()) - 1
        if index > -1:
            bar = list(bars.values())[index]
            progress = int(bar['index'] / bar['total'] * 100)
            self.progress.emit(progress)
        if 'message' in changes: self.message.emit(changes['message'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ui = Window()
    ui.resize(800, 600)
    ui.show()

    sys.exit(app.exec_())