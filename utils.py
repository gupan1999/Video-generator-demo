# coco数据集的80个类别
from enum import Enum, unique

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


@unique
class State(Enum):

    IDLE = 0
    READY = 1
    PLAYING = 2
    PAUSE = 3
    FINISHED = 4














