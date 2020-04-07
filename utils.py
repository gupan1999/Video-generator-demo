#!/usr/bin/env python
# coding: utf-8

import time
from enum import Enum, unique

import moviepy.video.fx.all as vfx
import torch
from PyQt5.QtCore import QSize, QObject, pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem

from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.video.VideoClip import ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from proglog import ProgressBarLogger

from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from projects.PointRend.point_rend import add_pointrend_config
from visualize import process, custom_show, blur, tiktok_effect

# coco数据集的80个类别
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

# 记录应用状态的枚举变量
@unique
class State(Enum):

    IDLE = 0
    READY = 1
    PLAYING = 2
    PAUSE = 3
    FINISHED = 4


listHeight = 60


# 存储界面上各片段音视频信息，与用户交互的item
class MyListWidgetItem(QListWidgetItem):
    def __init__(self, clipName=None, video=None, audio=None, parent=None):
        super(MyListWidgetItem, self).__init__(clipName, parent)
        self.video = video
        self.audio = audio
        self.text = clipName
        self.duration = self.video.duration if self.video else self.audio.duration
        self.setSizeHint(QSize(self.duration * 15, listHeight))

    def setClip(self, video=None, audio=None):
        self.video = video
        self.audio = audio
        self.duration = self.video.duration if self.video else self.audio.duration
        self.setSizeHint(QSize(self.duration * 15, listHeight))

    def copy(self):
        return MyListWidgetItem(self.text, self.video, self.audio)


#  自定义logger传递控制台消息、进度到界面的statusbar
class MyBarLogger(ProgressBarLogger):

    def __init__(self, message, progress):
        self.message = message
        self.progress = progress
        super(MyBarLogger, self).__init__()

    # 计算进度、发射消息的回调函数
    def callback(self, **changes):
        bars = self.state.get('bars')
        index = len(bars.values()) - 1
        if index > -1:
            bar = list(bars.values())[index]
            progress = int(bar['index'] / bar['total'] * 100)
            self.progress.emit(progress)
        if 'message' in changes: self.message.emit(changes['message'])


class CompositeObject(QObject):
    # 结束处理和携带控制台消息、进度的信号
    finish_process = pyqtSignal()
    progress = pyqtSignal(int)
    message = pyqtSignal(str)

    # 处理的片段与参数
    def __init__(self, targets, backgrounds, audios=None, triple=False, gauss=False, tiktok=False,
                 gauss_target=False, gauss_background=False,
                 parent=None):
        super(CompositeObject, self).__init__(parent)
        self.targets = targets
        self.backgrounds = backgrounds
        self.audios = audios
        self.triple = triple
        self.gauss = gauss
        self.tiktok = tiktok
        self.gauss_target = gauss_target
        self.gauss_background = gauss_background
        self.width = 1280
        self.height = 720

    # 分身效果，构造红蓝两种颜色的纯色片段，设置在中央人物的左右两侧，通过mask显示出与人物相同的轮廓
    def triple_effect(self, clip, mask_clip, width, height):
        red_clip = ColorClip(clip.size, (255, 0, 0), duration=clip.duration)
        blue_clip = ColorClip(clip.size, (0, 0, 255), duration=clip.duration)

        center_person_clip = clip.set_mask(mask_clip).set_position("center", "center")
        left_person_clip = red_clip.set_mask(mask_clip).set_opacity(0.5)
        right_person_clip = blue_clip.set_mask(mask_clip).set_opacity(0.5)

        left_person_clip_x = (width / 2 - left_person_clip.w / 2) - int(left_person_clip.w * 0.3)
        right_person_clip_x = (width / 2 - left_person_clip.w / 2) + int(left_person_clip.w * 0.3)
        person_clip_y = height / 2 - left_person_clip.h / 2
        left_person_clip = left_person_clip.set_position((left_person_clip_x, person_clip_y))
        right_person_clip = right_person_clip.set_position((right_person_clip_x, person_clip_y))
        return [left_person_clip, right_person_clip, center_person_clip]

    def process(self):

        my_logger = MyBarLogger(self.message, self.progress)
        my_logger(message="Detectron2 - Initializing the predictor")

        # Detectron2 默认设置
        cfg = get_cfg()
        # PointRend 设置
        add_pointrend_config(cfg)
        # 从该文件读取PointRend的参数设置
        cfg.merge_from_file("projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml")
        # 阈值，若阈值过低推断速度会很慢
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
        # 读取预训练模型的权重参数
        cfg.MODEL.WEIGHTS = "datasets/model_final_3c3198.pkl"
        if not torch.cuda.is_available():
            cfg.MODEL.DEVICE = 'cpu'

        predictor = DefaultPredictor(cfg)

        # 逐帧过滤不需要的类别的数据，为to_mask转换做准备
        def custom_frame(frame):
            _frame = frame.copy()
            output = predictor(_frame)
            instances = output['instances'].to('cpu')
            data = {'classes': instances.pred_classes.numpy(), 'boxes': instances.pred_boxes.tensor.numpy(),
                    'masks': instances.pred_masks.numpy(), 'scores': instances.scores.numpy()}
            # 设定接收人的数据
            data = process(data, target_class=[0])
            result = custom_show(_frame, data['masks'])
            return result

        # 以最终帧高度为准，使所有目标素材的帧高度相同，在concatenate的compose模式下可保证不因拉伸而失真
        for i in range(len(self.targets)):
            self.targets[i] = self.targets[i].fx(vfx.resize, height=self.height)
        for i in range(len(self.backgrounds)):
            self.backgrounds[i] = self.backgrounds[i].fx(vfx.resize, (self.width, self.height))

        # concatenate简单拼接
        target = concatenate_videoclips(self.targets, method="compose").without_audio()

        background = concatenate_videoclips(self.backgrounds).without_audio()

        # 计算总时长，若有音频则拼接音频
        audio = None
        duration = min(target.duration, background.duration)
        if self.audios:
            audio = concatenate_audioclips(self.audios)
            duration = min(target.duration, background.duration, audio.duration)

        # 把目标的识别结果——size为(n,w,h)的ndarray转换为mask，该mask表明它所属的片段哪些部分在背景上可见
        mask_clip = target.fl_image(custom_frame).to_mask().without_audio()

        # 在目标或背景上进行高斯模糊
        if self.gauss_target:
            target = target.fl_image(blur)
        if self.gauss_background:
            background = background.fl_image(blur)
        # 在目标上添加抖音效果
        if self.tiktok:
            target = target.fl_image(tiktok_effect)
        # 分身效果
        if self.triple:
            temp = self.triple_effect(target, mask_clip, width=self.width, height=self.height)
            temp.insert(0, background)
        else:
            # set_mask使得被识别为True的部分在背景上可见
            target = target.set_mask(mask_clip).set_position("center", "center")
            temp = [background, target]

        # 拼接所有目标素材
        final_clip = CompositeVideoClip(temp).set_audio(audio). \
            set_duration(duration) if audio else CompositeVideoClip(temp).set_duration(duration)

        # 导出为文件
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

















