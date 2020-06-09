import numpy as np
import sounddevice as sd
from PyQt5.QtCore import QObject


# 播放音频的类，独占一子线程播放音频
class Audio(QObject):

    # 初始化音频片段
    def __init__(self, clip, fps=44100, buffersize=4000, nbytes=2):
        super(Audio, self).__init__()
        self.clip = clip
        self.fps = fps
        self.buffersize = buffersize
        self.nbytes = nbytes
        self.index = 0

        if self.clip:
            self.totalsize = int(self.fps * self.clip.duration)
            self.pospos = np.array(list(range(0, self.totalsize, self.buffersize)) + [self.totalsize])
        else:
            self.totalsize = 0
            self.pospos = None

    # 音频流开启
    def work(self):
        if self.clip:
            self.stream = sd.OutputStream(
                samplerate=self.fps, blocksize=self.buffersize,
                dtype='int16')
            self.stream.start()

    # 一段一段写入音频流至结束
    def update(self):
        if self.clip and self.index < len(self.pospos) - 1:
            t = (1.0 / self.fps) * np.arange(self.pospos[self.index], self.pospos[self.index + 1])
            data = self.clip.to_soundarray(t, nbytes=self.nbytes, quantize=True)
            self.stream.write(data)

            self.index += 1
        else:
            self.index = 0

    # 设置新音频片段
    def setClip(self, clip, fps=44100, buffersize=4000, nbytes=2):

        self.clip = clip
        self.index = 0
        self.fps = fps
        self.buffersize = buffersize
        self.nbytes = nbytes
        if self.clip:
            self.totalsize = int(self.fps * self.clip.duration)
            self.pospos = np.array(list(range(0, self.totalsize, self.buffersize)) + [self.totalsize])
        else:
            self.totalsize = 0
            self.pospos = None
        self.work()

    # 控制音频播放进度
    def setIndex(self, i):
        self.index = i











