# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QPicture, QPixmap
from PyQt5.QtWidgets import QWidget, QRubberBand, QApplication, QLabel, QPushButton


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label = Mylabel(Form)
        self.label.setText("")
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

class test(Ui_Form,QWidget):
    def __init__(self):
        super(test,self).__init__()
        self.setupUi(self)
        self.label.setFixedSize(1080,720)
        self.label.setScaledContents(True)
        self.picture = QPixmap()
        self.picture.load("apple.jpg")
        self.label.setPixmap(self.picture)
        self.button = QPushButton()
        self.button.setText("选择")
        self.button.clicked.connect(self.custom)
        self.gridLayout.addWidget(self.button, 1, 0, 1, 1)

    def custom(self):
        print(self.label.rubber.geometry())


class Mylabel(QLabel):
    def __init__(self,parent=None):
        super(Mylabel,self).__init__(parent)
        self.rubber = None
        self.origin = None
        self.parent = parent


    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(a0)
        self.origin = a0.pos()
        print(self.origin)

        if self.rubber is None:
            self.rubber = QRubberBand(QRubberBand.Line, self)
        self.rubber.setGeometry(QRect(self.origin, QSize()))
        self.rubber.show()


    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(a0)
        if self.rubber:
            self.rubber.setGeometry(QRect(self.origin, a0.pos()).normalized())


    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(a0)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ui = test()
    ui.resize(800, 600)
    ui.show()

    sys.exit(app.exec_())



