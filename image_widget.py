from PyQt4 import QtGui, QtCore, Qt
import numpy as np
import cv2
from image_loader_processor import *


class ImageWidget(QtGui.QWidget):

    signalNewPixelInfo = pyqtSignal(dict)

    def __init__(self):
        super(ImageWidget, self).__init__()

        self.curimage = None
        self.initUI()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.translation = np.array([0, 0], dtype=np.float32)
        self.scaling = 1.0

        self.trans = QtGui.QTransform()
        self.down_pos = None

        self.img_proc = None
        self.setMouseTracking(True)

    def initUI(self):
        self.setMinimumSize(800, 800)

    def setImage(self, img_proc):
        assert(isinstance(img_proc, ImageLoaderProcessor))
        self.img_proc = img_proc
        self.update()

    def paintEvent(self, e):
        assert(isinstance(e, QtGui.QPaintEvent))
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def mouseReleaseEvent(self, e):
        assert (isinstance(e, QtGui.QMouseEvent))
        self.down_pos = None

    def mousePressEvent(self, e):
        assert (isinstance(e, QtGui.QMouseEvent))
        if e.button() == QtCore.Qt.LeftButton:
            self.down_pos = np.array([e.pos().x(), e.pos().y()])
            self.down_trans = self.trans
        elif e.button() == QtCore.Qt.RightButton:
            # self.ndimage[:,:,:] = (self.ndimage * 0.7).astype(np.uint8)
            self.img_proc.set_modifiers({'level_upper': 100})

        self.update()

    def mouseMoveEvent(self, e):
        assert(isinstance(e, QtGui.QMouseEvent))
        mousepos = np.array([e.pos().x(), e.pos().y()])

        if self.img_proc is None:
            return

        if e.buttons() != QtCore.Qt.NoButton:
            if self.down_pos is not None:
                tmp_trans = QtGui.QTransform().translate(*(mousepos - self.down_pos))
                self.trans = self.down_trans * tmp_trans
                self.update()
        else:
            assert(isinstance(self.trans, QtGui.QTransform))
            img_pos = self.trans.inverted()[0].map(mousepos[0], mousepos[1])
            x = int(img_pos[0])
            y = int(img_pos[1])
            self.signalNewPixelInfo.emit({
                'img_pos': (x,y),
                'color': self.img_proc.get_original_image()[y, x]
            })

    def wheelEvent(self, e):
        assert(isinstance(e, QtGui.QWheelEvent))
        additional_scale = 1.1 ** (e.delta() / 50)

        if self.img_proc is None:
            return

        mousepos = np.array([e.pos().x(), e.pos().y()])

        tmp_trans = \
        QtGui.QTransform().translate(*(mousepos)).scale(additional_scale, additional_scale).translate(*(-mousepos))

        self.trans *= tmp_trans

        self.update()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        # qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setBrush(QtGui.QColor(30, 30, 30))
        qp.drawRect(0, 0, w-1, h-1)

        if self.img_proc is not None:
            curimage = self.img_proc.get_processed_image()
            assert(isinstance(curimage, QtGui.QImage))
            qp.setTransform(self.trans)

            qp.drawImage(QtCore.QPointF(0, 0), curimage)

        else:
            text = "Drop image here"
            qp.setFont(QtGui.QFont("Arial", 14))
            fm = QtGui.QFontMetrics(qp.font())
            pixelsWide = fm.width(text)
            qp.setPen(QtGui.QColor(255, 255, 255))
            qp.drawText((w-pixelsWide)//2, (h+fm.height())//2, text)
