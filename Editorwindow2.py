import sys
import threading
import time
from enum import Enum

import qdarkstyle
import torch
from PyQt5.QtCore import QDir, QUrl, QObject, pyqtSignal, QThread, QTime
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QSlider, QLabel, QSizePolicy, QProgressBar, \
    QFileDialog, QMessageBox
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from proglog import ProgressBarLogger

from projects.PointRend.point_rend.config import add_pointrend_config
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from visualize import custom_show1, process
from window2 import Ui_MainWindow


cfg = get_cfg()
# Add PointRend-specific config
add_pointrend_config(cfg)
# Load a config from file
cfg.merge_from_file("projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
cfg.MODEL.WEIGHTS = "datasets/model_final_3c3198.pkl"
if not torch.cuda.is_available():
    cfg.MODEL.DEVICE = 'cpu'

predictor = DefaultPredictor(cfg)


class Window(QMainWindow, Ui_MainWindow):
    final_duration = 0
    final_clip = None
    video_backend = None
    video_forend = None
    bgm = None
    current_clip = None
    cutter_start = 0
    withaudio = True
    product_filename = None

    def __init__(self):
        super(Window, self).__init__()

        self.setupUi(self)

        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.setVideoOutput(self.widget)

        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)
        self.pushButton_8.setEnabled(False)
        self.pushButton_9.setEnabled(False)
        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.horizontalSlider.setRange(0, 0)
        self.horizontalSlider.sliderMoved.connect(self.setPosition)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.statusbar.addPermanentWidget(self.progressBar)
        self.horizontalSlider.setTickPosition(QSlider.TicksBothSides)

        self.connecctSignals()

    def connecctSignals(self):
        self.pushButton_2.clicked.connect(self.play)
        self.pushButton_4.clicked.connect(self.setStart)
        self.pushButton_5.clicked.connect(self.changeChannel)
        self.pushButton.clicked.connect(self.openFore)
        self.pushButton_7.clicked.connect(self.openBack)
        self.pushButton_6.clicked.connect(self.openBgm)
        self.pushButton_3.clicked.connect(self.process)
        self.pushButton_8.clicked.connect(self.cut)
        self.pushButton_9.clicked.connect(self.tiktok)
        # self.pushButton_10.clicked.connect(self.triple)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def cut(self):
        end = self.mediaPlayer.position() / 1000
        if end <= Window.cutter_start:
            QMessageBox.critical(self, "警告", "请在起始时间之后切分")
        else:
            Window.cutter_end = end
            self.progressBar.setVisible(True)
            self.threadObject = ProcessObject()
            self.subThread = QThread()
            self.threadObject.moveToThread(self.subThread)
            self.subThread.started.connect(self.threadObject.process_cut)
            self.threadObject.finish_cut.connect(self.finishCut)
            self.threadObject.message.connect(self.thread_message)
            self.threadObject.progress.connect(self.thread_progress)

            self.subThread.start()
            self.blockCommand()

    def fitState(self, state):
        if state == State.Audio_loaded:
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_8.setEnabled(True)
            self.pushButton_5.setEnabled(False)
            self.pushButton_9.setEnabled(False)
        elif state == State.Video_loaded:
            self.pushButton_5.setEnabled(True)
            self.pushButton_9.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_8.setEnabled(True)



    def refreshCommand(self):
        self.progressBar.setVisible(False)
        self.pushButton_3.setEnabled(True)
        self.pushButton_8.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)
        self.pushButton_9.setEnabled(True)

    def blockCommand(self):
        if self.subThread.isRunning():
            self.pushButton_3.setEnabled(False)
            self.pushButton_8.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            self.pushButton_9.setEnabled(False)


    def changeChannel(self):
        Window.withaudio = not Window.withaudio

        self.pushButton_5.setText("有声") if Window.withaudio else self.pushButton_5.setText("无声")

    def setStart(self):
        start = self.mediaPlayer.position()/1000
        Window.cutter_start = start
        currentTime = QTime((start/3600) % 60, (start/60) % 60,
                    start % 60, (start*1000) % 1000)
        format = 'hh:mm:ss' if self.mediaPlayer.duration()/1000 > 3600 else 'mm:ss'
        tStr = currentTime.toString(format)
        self.statusbar.showMessage("设置起始时间%s" % tStr)

    def process(self):
        if Window.video_forend is not None and Window.video_backend is not None and Window.bgm is not None:
            self.progressBar.setVisible(True)
            self.threadObject = ProcessObject()
            self.subThread = QThread()
            self.threadObject.moveToThread(self.subThread)
            self.subThread.started.connect(self.threadObject.process_work)
            self.threadObject.finish_process.connect(self.finishProcess)
            self.threadObject.message.connect(self.thread_message)
            self.threadObject.progress.connect(self.thread_progress)

            self.subThread.start()
            self.blockCommand()

    def finishProcess(self):
        self.cutter_start = 0
        self.refreshCommand()
        self.subThread.exit(0)
        self.initiateTime()


    def thread_message(self, value):
        self.statusbar.showMessage(value)

    def thread_progress(self, value):
        self.progressBar.setValue(value)

    def finishCut(self):
        self.cutter_start = 0
        self.refreshCommand()
        self.subThread.exit(0)

    def openFore(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath(),"Video(*.mp4;*.wmv;*.rmvb;*.avi)")
        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            Window.video_forend = VideoFileClip(fileName)
            Window.current_clip = Window.video_forend
            self.fitState(State.Video_loaded)
            self.initiateTime()

    def openBack(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                      QDir.homePath(), "Video(*.mp4;*.wmv;*.rmvb;*.avi)")
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            Window.video_backend = VideoFileClip(fileName)
            Window.current_clip = Window.video_backend
            self.fitState(State.Video_loaded)
            self.initiateTime()

    def openBgm(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Audio",
                                                  QDir.homePath(), "Audio(*.mp3;*.wav)")
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            Window.bgm = AudioFileClip(fileName)
            Window.current_clip = Window.bgm
            self.fitState(State.Audio_loaded)
            self.initiateTime()

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

    def initiateTime(self):

        duration = self.current_clip.duration
        currentTime = QTime(0,0,0,0)
        totalTime = QTime((duration / 3600) % 60, (duration / 60) % 60,
                          duration % 60, (duration * 1000) % 1000)

        format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
        tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        self.label.setText(tStr)
        self.mediaPlayer.pause()


    def positionChanged(self, position):
        self.horizontalSlider.setValue(position)
        self.updateDurationInfo(position / 1000)

    def durationChanged(self, duration):
        self.horizontalSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def updateDurationInfo(self, currentInfo):
        duration = self.mediaPlayer.duration()/1000
        if currentInfo or duration:
            currentTime = QTime((currentInfo/3600) % 60, (currentInfo/60) % 60,
                    currentInfo % 60, (currentInfo*1000) % 1000)
            totalTime = QTime((duration/3600) % 60, (duration/60) % 60,
                    duration % 60, (duration*1000) % 1000)

            format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        else:
            tStr = ""

        self.label.setText(tStr)

    def tiktok(self):
        if isinstance(self.current_clip,VideoFileClip):
            if self.current_clip == Window.video_forend:
                Window.current_clip = Window.current_clip.fl_image(tiktok_effect)
                Window.video_forend = Window.current_clip
            elif self.current_clip == Window.video_backend:
                Window.current_clip = Window.current_clip.fl_image(tiktok_effect)
                Window.video_backend = Window.current_clip
            print("success")

    def handleError(self):
        self.statusbar.showMessage(self.mediaPlayer.errorString())


def custom_frame1(frame):
    _frame = frame.copy()
    output = predictor(_frame)
    instances = output['instances'].to('cpu')
    data = {'classes': instances.pred_classes.numpy(), 'boxes': instances.pred_boxes.tensor.numpy(), 'masks':instances.pred_masks.numpy() , 'scores': instances.scores.numpy()}
    data = process(data, target_class=[0])
    result = custom_show1(_frame,  data['masks'])
    return result


class ProcessObject(QObject):  # 用于子线程的类
    finish_process = pyqtSignal()
    finish_cut = pyqtSignal()
    progress = pyqtSignal(int)
    message = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ProcessObject, self).__init__(parent)  # 显式调用父类构造函数

    def process_cut(self):
        print(threading.current_thread())
        my_logger = MyBarLogger(self.message, self.progress)
        if isinstance(Window.current_clip,VideoFileClip):
            Window.current_clip = Window.current_clip.subclip(Window.cutter_start, Window.cutter_end) \
                if Window.withaudio else Window.video_backend.subclip(Window.cutter_start,
                                                                      Window.cutter_end).without_audio()
            Window.product_filename = f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4'
            Window.current_clip.write_videofile(
                Window.product_filename,
                codec='mpeg4',
                audio_codec="libmp3lame",
                bitrate="8000k",
                threads=4,
                logger=my_logger
            )
        elif isinstance(Window.current_clip,AudioFileClip):
            Window.current_clip = Window.current_clip.subclip(Window.cutter_start, Window.cutter_end)
            Window.product_filename = f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4'
            Window.current_clip.write_audiofile(
               Window.product_filename,
                codec="libmp3lame",
                logger=my_logger
            )
        self.finish_cut.emit()

    def process_work(self):

        my_logger = MyBarLogger(self.message, self.progress)
        duration = min(Window.video_forend.duration, Window.video_backend.duration, Window.bgm.duration)
        mask_clip = Window.video_forend.fl_image(custom_frame1).to_mask().without_audio()
        Window.video_forend = Window.video_forend.set_mask(mask_clip).set_pos("center", "center")
        Window.final_clip = CompositeVideoClip([Window.video_backend, Window.video_forend]).set_audio(Window.bgm).\
            set_duration(duration)

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


def tiktok_effect(frame):
    # 单独抽取去掉红色通道的图像
    gb_channel_frame = frame.copy()
    gb_channel_frame[:, :, 0].fill(0)

    # 单独抽取红色通道图像
    r_channel_frame = frame.copy()
    r_channel_frame[:, :, 1].fill(0)
    r_channel_frame[:, :, 2].fill(0)

    # 错位合并图像，形成抖音效果
    result = frame.copy()
    result[:-5, :-5, :] = r_channel_frame[:-5, :-5, :] + gb_channel_frame[5:, 5:, :]

    return result


class State(Enum):

    Video_loaded = 0
    Audio_loaded = 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ui = Window()
    ui.resize(800, 600)
    ui.show()

    sys.exit(app.exec_())