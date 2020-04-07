# def terminate(self):
#     self.compositeThread.quit()
#     self.compositeThread.wait(500)

# self.cancelBtn.clicked.connect(self.terminate)

# self.cancelBtn.setEnabled(True)
# self.cancelBtn.setVisible(True)

# def speed(self):
#     self.clip = self.clip.fx(vfx.speedx, self.clip, 2)

# def finishProcess(self):
#   self.progressBar.setVisible(False)
#    self.saveThread.quit()
#    self.saveThread.wait()

# 保存该片段到本地
# def saveItem(self):
#    self.saveObject = SaveTemp(self.cur_listWidget.currentItem().video.copy())
#    self.saveThread = QThread()
#    self.saveObject.moveToThread(self.saveThread)
#    self.saveObject.finish_process.connect(self.finishProcess)
#    self.saveObject.message.connect(self.thread_message)
#    self.saveObject.progress.connect(self.thread_progress)
#    self.saveThread.started.connect(self.saveObject.process)
#    self.progressBar.setVisible(True)
#    self.saveThread.start()


# self.saveObject = None
# saveAction = QAction("保存本地", self)

# popMenu.addAction(saveAction)

# saveAction.triggered.connect(self.saveItem)

# self.cancelBtn = QtWidgets.QPushButton()
# self.cancelBtn.setText("取消")
# self.cancelBtn.setVisible(False)
# self.cancelBtn.setEnabled(False)

# self.statusbar.addPermanentWidget(self.cancelBtn)
# self.processObject = None
#self.saveThread = None
# self.cancelBtn.clicked.connect(self.terminate)

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