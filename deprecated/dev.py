import queue
import sys
import threading
import time
from enum import Enum

import numpy as np
import sounddevice as sd
import qdarkstyle
from PyQt5.QtCore import QDir, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QSizePolicy, QProgressBar, \
    QFileDialog
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from proglog import ProgressBarLogger
from utils import State
from window3 import Ui_MainWindow



class Window(QMainWindow, Ui_MainWindow):
    final_clip = None
    audio_backend = None
    cutter_end = 0
    cutter_start = 0
    product = ''
    state_change = pyqtSignal()
    index = 0
    def __init__(self):
        super(Window, self).__init__()

        self.setupUi(self)
        self.pushButton.clicked.connect(self.openFile)
        self.pushButton_3.clicked.connect(self.process)
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_2.clicked.connect(self.play)

        self.horizontalSlider.setRange(0,0)
        self.horizontalSlider.sliderMoved.connect(self.setPosition)
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Fixed)
        self.statusbar.addPermanentWidget(self.progressBar)

        self.state_change.connect(self.fitState)
        self.state = State.IDLE
        self.playObject = None
        self.playThread = None




    def fitState(self):
        if self.state == State.PLAYING:
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        elif self.state in (State.PAUSE,State.IDLE,State.FINISHED):
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


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
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Audio",
                                                  QDir.homePath(), "Audio(*.mp3;*.wav)")

        if fileName != '':
            self.pushButton_2.setEnabled(True)
            Window.audio_backend = AudioFileClip(fileName)
            self.pushButton_3.setEnabled(True)


    def play(self):

        if self.state in (State.IDLE,State.PAUSE,State.FINISHED):

            self.playObject = PlayObject()

            if self.playThread is None:
                self.playThread = QThread()
            self.playObject.moveToThread(self.playThread)
            self.playThread.started.connect(self.playObject.play)
            self.playThread.start()
            self.state = State.PLAYING
            self.state_change.emit()

        else:
            self.playObject.pause()
            self.state = State.PAUSE
            self.state_change.emit()
            self.playThread.quit()







    def positionChanged(self, position):
        self.horizontalSlider.setValue(position)

    def durationChanged(self, duration):

        self.horizontalSlider.setRange(0, duration)


    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.pushButton_3.setEnabled(False)
        self.pushButton_1.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.statusbar.showMessage("Error: %s" % self.mediaPlayer.errorString())


class ProcessObject(QObject):  # 用于子线程的类
    finish_process = pyqtSignal()  # 处理图片结束的信号
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    def __init__(self, parent=None):
        super(ProcessObject, self).__init__(parent)  # 显式调用父类构造函数

    def process_work(self):

        my_logger = MyBarLogger(self.message, self.progress)

        Window.final_clip = Window.video_backend.subclip(Window.cutter_start,Window.cutter_end)

        Window.product = f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4'
        Window.final_clip.write_videofile(
            Window.product,
            fps=30,
            codec='mpeg4',
            bitrate="8000k",
            audio_codec="libmp3lame",
            threads=4,
            logger=my_logger
        )

        self.finish_process.emit()  # 处理图片结束信号发射


class PlayObject(QObject):
    terminate = pyqtSignal()
    finish = pyqtSignal()
    def __init__(self):
        super(PlayObject, self).__init__()
        self.stream = None
        self.buffersize = 1000
        self.n_buffer = 1
        self.fps = Window.audio_backend.fps
        self.duration = Window.audio_backend.duration
        self.totalsize = int(self.fps * self.duration)
        self.pospos = np.array(list(range(0, self.totalsize, self.buffersize)) + [self.totalsize])
        self.index = Window.index





    def pause(self):
        '''
        if self.stream is not None and self.stream.active:
            Window.index = self.index+1
            print(Window.index)
            self.stream.stop()
            self.terminate.emit()
        '''
        if self.stream is not None and self.stream.active:
            self.state = State.PAUSE

            Window.index = self.index + 1
            print("Window %d" % Window.index)
    def play(self):

        self.state = State.PLAYING

        q = queue.Queue(maxsize=self.n_buffer)
        event = threading.Event()
        def callback(outdata, frames, time, status):

            if status.output_underflow:
                print('Output underflow: increase blocksize?', file=sys.stderr)
                raise sd.CallbackAbort
            assert not status

            try:
                data = q.get_nowait()

            except queue.Empty:
                print('Buffer is empty: increase buffersize?', file=sys.stderr)
                raise sd.CallbackAbort
            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = 0 * (len(outdata) - len(data))
                raise sd.CallbackStop
            else:
                outdata[:] = data

        self.stream = sd.OutputStream(
            samplerate=self.fps, blocksize=self.buffersize,
            dtype='int16',
            callback=callback, finished_callback=event.set)
        with self.stream:
            while self.state == State.PLAYING and self.index < len(self.pospos) - 1:
                Window.tt = (1.0 / self.fps) * np.arange(self.pospos[self.index], self.pospos[self.index + 1])
                data = Window.audio_backend.to_soundarray(Window.tt, nbytes=2, quantize=True)
                q.put(data)
                print(self.index)
                self.index += 1
            event.wait()

        if self.index == len(self.pospos)-1:
            ui.index = 0
            ui.state = State.FINISHED
        else:
            ui.state = State.PAUSE
        ui.state_change.emit()






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
    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)
    ui = Window()
    ui.resize(800, 600)
    ui.show()

    sys.exit(app.exec_())