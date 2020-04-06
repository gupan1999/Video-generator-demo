#!/usr/bin/env python
# coding: utf-8

from enum import Enum, unique
import time

import torch
from PyQt5.QtCore import QSize, QObject, pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem

# coco数据集的80个类别
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.video.VideoClip import VideoClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from proglog import ProgressBarLogger
from skimage.filters import gaussian
import moviepy.video.fx.all as vfx
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from projects.PointRend.point_rend import add_pointrend_config
from visualize import process, custom_show

class_names = ('person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush')

video_class = ('.mp4', '.wmv', '.rmvb', '.avi')
audio_class = ('.mp3', '.wav')


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


def blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian(image.astype(float), sigma=10)

@unique
class State(Enum):

    IDLE = 0
    READY = 1
    PLAYING = 2
    PAUSE = 3
    FINISHED = 4


listHeight = 60


class MyListWidgetItem(QListWidgetItem):
    def __init__(self, clipName=None, video=None, audio=None, parent=None):
        super(MyListWidgetItem, self).__init__(clipName, parent)
        self.video = video
        self.audio = audio
        self.text = clipName
        self.duration = self.video.duration if self.video else self.audio.duration
        self.setSizeHint(QSize(self.duration*10, listHeight))

    def setClip(self, video=None, audio=None):
        self.video = video
        self.audio = audio
        self.duration = self.video.duration if self.video else self.audio.duration
        self.setSizeHint(QSize(self.duration * 10, listHeight))

    def copy(self):
        return MyListWidgetItem(self.text, self.video, self.audio)


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


class CompositeObject(QObject):
    finish_process = pyqtSignal()
    finish_cut = pyqtSignal()
    progress = pyqtSignal(int)
    message = pyqtSignal(str)

    def __init__(self, targets, backgrounds, audios=None, triple=False, gauss=False, parent=None):
        super(CompositeObject, self).__init__(parent)
        self.targets = targets
        self.backgrounds = backgrounds
        self.audios = audios
        self.triple = triple
        self.gauss = gauss
        self.width = 1280
        self.height = 720

    def triple_effect(self, clip, mask_clip, width, height):
        red_clip = ColorClip(clip.size, (255, 0, 0), duration=clip.duration)
        blue_clip = ColorClip(clip.size, (0, 0, 255), duration=clip.duration)
        person_clip_height = int(height * 0.9)

        center_person_clip = clip.set_mask(mask_clip).fx(vfx.resize, height=person_clip_height).set_pos(("center", "center"))
        left_person_clip = red_clip.set_mask(mask_clip).fx(vfx.resize, height=person_clip_height).set_opacity(0.5)
        right_person_clip = blue_clip.set_mask(mask_clip).fx(vfx.resize, height=person_clip_height).set_opacity(0.5)

        left_person_clip_x = (width / 2 - left_person_clip.w / 2) - int(left_person_clip.w * 0.3)
        right_person_clip_x = (width / 2 - left_person_clip.w / 2) + int(left_person_clip.w * 0.3)
        person_clip_y = height / 2 - left_person_clip.h / 2
        left_person_clip = left_person_clip.set_pos((left_person_clip_x, person_clip_y))
        right_person_clip = right_person_clip.set_pos((right_person_clip_x, person_clip_y))
        return [left_person_clip, right_person_clip, center_person_clip]

    def process(self):
        my_logger = MyBarLogger(self.message, self.progress)
        my_logger(message="Initializing the predictor")
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

        def custom_frame(frame):
            _frame = frame.copy()
            output = predictor(_frame)
            instances = output['instances'].to('cpu')
            data = {'classes': instances.pred_classes.numpy(), 'boxes': instances.pred_boxes.tensor.numpy(),
                    'masks': instances.pred_masks.numpy(), 'scores': instances.scores.numpy()}
            data = process(data, target_class=[0])
            result = custom_show(_frame, data['masks'])
            return result

        if not self.triple:
            for i in range(len(self.targets)):
                self.targets[i] = self.targets[i].fx(vfx.resize, width=self.width, height=self.height)
        for i in range(len(self.backgrounds)):
            self.backgrounds[i] = self.backgrounds[i].fx(vfx.resize, width=self.width, height=self.height)

        target = concatenate_videoclips(self.targets).without_audio()
        background = concatenate_videoclips(self.backgrounds).without_audio()
        audio = None
        duration = min(target.duration, background.duration)
        if self.audios:
            audio = concatenate_audioclips(self.audios)
            duration = min(target.duration, background.duration, audio.duration)
        mask_clip = target.fl_image(custom_frame).to_mask().without_audio()
        if self.triple:
            temp = self.triple_effect(target, mask_clip, width=self.width, height=self.height)
            temp.insert(0, background)
        else:

            target = target.set_mask(mask_clip).set_pos("center", "center")
            temp = [background, target]
        final_clip = CompositeVideoClip(temp).set_audio(audio). \
            set_duration(duration) if audio else CompositeVideoClip(temp)

        if self.gauss:
            final_clip = final_clip.fl_image(blur)

        final_clip.write_videofile(
            f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4',
            fps=30,
            codec='mpeg4',
            bitrate="8000k",
            audio_codec="libmp3lame",
            threads=4,
            logger=my_logger
        )
        self.finish_process.emit()


# class SaveTemp(QObject):
#     finish_process = pyqtSignal()
#     progress = pyqtSignal(int)
#     message = pyqtSignal(str)
#
#     def __init__(self, clip, parent=None):
#         super(SaveTemp, self).__init__(parent)
#         self.clip = clip
#
#     def process(self):
#         if isinstance(self.clip, VideoClip):
#             myLogger = MyBarLogger(self.message, self.progress)
#             self.clip.write_videofile(f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4', codec='mpeg4',
#                 audio_codec="libmp3lame",
#                 bitrate="8000k",
#                 threads=4, logger=myLogger)
#             self.finish_process.emit()














