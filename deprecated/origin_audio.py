
# class audio(threading.Thread):
#
#     def __init__(self, clip, fps=22050, buffersize=4000, nbytes=2):
#         super(audio, self).__init__()
#         self.clip = clip
#         self.fps = fps
#         self.buffersize = buffersize
#         self.nbytes = nbytes
#         self.__flag = threading.Event()     # 用于暂停线程的标识
#         self.__flag.set()       # 设置为True
#         self.__running = threading.Event()      # 用于停止线程的标识
#         self.__running.set()      # 将running设置为True
#
#     def run(self):
#         pg.mixer.quit()
#         pg.mixer.init(self.fps, -8 * self.nbytes, self.clip.nchannels, 1024)
#         totalsize = int(self.fps * self.clip.duration)
#         pospos = np.array(list(range(0, totalsize, self.buffersize)) + [totalsize])
#         tt = (1.0 / self.fps) * np.arange(pospos[0], pospos[1])
#         sndarray = self.clip.to_soundarray(tt, nbytes=self.nbytes, quantize=True)
#         chunk = pg.sndarray.make_sound(sndarray)
#         channel = chunk.play()
#         i = 1
#         while self.__running.isSet() and i < len(pospos)-1:
#             self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到self.__flag为True后返回
#             # print(threading.current_thread())
#             tt = (1.0 / self.fps) * np.arange(pospos[i], pospos[i + 1])
#             sndarray = self.clip.to_soundarray(tt, nbytes=self.nbytes, quantize=True)
#             chunk = pg.sndarray.make_sound(sndarray)
#             channel.queue(chunk)
#             while channel.get_queue():
#                 time.sleep(0.08)
#             i += 1
#
#
#     def pause(self):
#         self.__flag.clear()     # 设置为False, 让线程阻塞
#
#     def resume(self):
#         self.__flag.set()    # 设置为True, 让线程停止阻塞
#
#     def stop(self):
#         # self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
#         self.__running.clear()        # 设置为False

# class Audio(QObject):
#
#     def __init__(self, clip, fps=44100, buffersize=4000, nbytes=2):
#         super(Audio, self).__init__()
#         self.clip = clip
#         self.fps = fps
#         self.buffersize = buffersize
#         self.nbytes = nbytes
#         self.index = 0
#         if self.clip:
#             self.totalsize = int(self.fps * self.clip.duration)
#             self.pospos = np.array(list(range(0, self.totalsize, self.buffersize)) + [self.totalsize])
#         else:
#             self.totalsize = 0
#             self.pospos = None
#
#     def work(self):
#         if self.clip:
#             pg.mixer.quit()
#             pg.mixer.init(self.fps, -8 * self.nbytes, self.nbytes, 512)
#             t = (1.0 / self.fps) * np.arange(self.pospos[0], self.pospos[1])
#             data = self.clip.to_soundarray(t, nbytes=self.nbytes, quantize=True)
#             chunk = pg.sndarray.make_sound(data)
#             self.channel = chunk.play()
#
#     def update(self):
#         if self.clip and self.index < len(self.pospos)-1:
#
#             t = (1.0 / self.fps) * np.arange(self.pospos[self.index], self.pospos[self.index + 1])
#             data = self.clip.to_soundarray(t, nbytes=self.nbytes, quantize=True)
#             chunk = pg.sndarray.make_sound(data)
#             self.channel.queue(chunk)
#             print("queue")
#             self.index += 1
#         else:
#             self.index = 0
#
#     def setClip(self, clip, fps=44100, buffersize=4000, nbytes=2):
#
#         self.clip = clip
#         self.index = 0
#         self.fps = fps
#         self.buffersize = buffersize
#         self.nbytes = nbytes
#         if self.clip:
#             self.totalsize = int(self.fps * self.clip.duration)
#             self.pospos = np.array(list(range(0, self.totalsize, self.buffersize)) + [self.totalsize])
#         else:
#             self.totalsize = 0
#             self.pospos = None
#         self.work()
#
#     def setIndex(self, i):
#         self.index = i

# listHeight = 60
#
#
# class MyListWidgetItem(QListWidgetItem):
#     def __init__(self, clipName=None, video=None, audio=None, parent=None):
#         super(MyListWidgetItem, self).__init__(clipName, parent)
#         self.video = video
#         self.audio = audio
#         self.text = clipName
#         self.duration = self.video.duration if self.video else self.audio.duration
#         self.setSizeHint(QSize(self.duration*10, listHeight))
#
#     def setClip(self, video=None, audio=None):
#         self.video = video
#         self.audio = audio
#         self.duration = self.video.duration if self.video else self.audio.duration
#         self.setSizeHint(QSize(self.duration * 10, listHeight))
#
#     def copy(self):
#         return MyListWidgetItem(self.text, self.video, self.audio)
#
#
# class audio(threading.Thread):
#
#     def __init__(self, clip, fps=22050, buffersize=4000, nbytes=2):
#         super(audio, self).__init__()
#         self.clip = clip
#         self.fps = fps
#         self.buffersize = buffersize
#         self.nbytes = nbytes
#         self.__flag = threading.Event()     # 用于暂停线程的标识
#         self.__flag.set()       # 设置为True
#         self.__running = threading.Event()      # 用于停止线程的标识
#         self.__running.set()      # 将running设置为True
#
#     def run(self):
#         pg.mixer.quit()
#         pg.mixer.init(self.fps, -8 * self.nbytes, self.clip.nchannels, 1024)
#         totalsize = int(self.fps * self.clip.duration)
#         pospos = np.array(list(range(0, totalsize, self.buffersize)) + [totalsize])
#         tt = (1.0 / self.fps) * np.arange(pospos[0], pospos[1])
#         sndarray = self.clip.to_soundarray(tt, nbytes=self.nbytes, quantize=True)
#         chunk = pg.sndarray.make_sound(sndarray)
#         channel = chunk.play()
#         i = 1
#         while self.__running.isSet() and i < len(pospos)-1:
#             self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到self.__flag为True后返回
#             # print(threading.current_thread())
#             tt = (1.0 / self.fps) * np.arange(pospos[i], pospos[i + 1])
#             sndarray = self.clip.to_soundarray(tt, nbytes=self.nbytes, quantize=True)
#             chunk = pg.sndarray.make_sound(sndarray)
#             channel.queue(chunk)
#             while channel.get_queue():
#                 time.sleep(0.08)
#             i += 1
#
#
#     def pause(self):
#         self.__flag.clear()     # 设置为False, 让线程阻塞
#
#     def resume(self):
#         self.__flag.set()    # 设置为True, 让线程停止阻塞
#
#     def stop(self):
#         # self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
#         self.__running.clear()        # 设置为False
#
