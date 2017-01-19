from PyQt4 import QtGui, QtCore
import numpy as np
import cv2
from image_loader_processor import *


class HistogramWidget(QtGui.QWidget):
    def __init__(self):
        super(HistogramWidget, self).__init__()

        self.img_proc = None

        self.averages = None
        self.ranges = None
        self.initUI()

    def initUI(self):
        self.setMinimumSize(300, 70)
        self.setMaximumHeight(70)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def setImage(self, img_proc):
        assert(isinstance(img_proc, ImageLoaderProcessor))
        self.img_proc = img_proc
        self.update()

    def drawWidget(self, qp):
        #font = QtGui.QFont('Serif', 7, QtGui.QFont.Light)
        #qp.setFont(font)

        size = self.size()
        w = size.width()
        h = size.height()

        qp.setRenderHint(QtGui.QPainter.Antialiasing)

        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtGui.QColor(50, 50, 50))
        qp.drawRect(0, 0, w, h)

        if self.img_proc is None:
            return

        hist = self.img_proc.get_histogram()[0]

        # Stretch histogram to fit widget
        trans = QtGui.QTransform()
        trans.scale(w / len(hist), -1)
        trans.translate(0, -h)
        qp.setTransform(trans)

        if self.img_proc is not None:
            qp.setPen(QtCore.Qt.NoPen)
            # qp.setPen(QtGui.QColor(230, 230, 230))
            qp.setBrush(QtGui.QColor(150, 150, 150))

            for idx in range(len(hist)):
                qp.drawRect(QtCore.QRectF(idx, 0, 1.1, hist[idx] * 50))

