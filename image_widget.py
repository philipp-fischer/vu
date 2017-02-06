from PyQt4 import QtGui, QtCore, Qt
import numpy as np
import cv2
from image_loader_processor import *


def transformToArray(transf):
    assert(isinstance(transf, QtGui.QTransform))
    return np.array([[transf.m11(), transf.m12(), transf.m13()],
                     [transf.m21(), transf.m22(), transf.m23()],
                     [transf.m31(), transf.m32(), transf.m33()]])


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
        self.fit_img_transform = None
        self.full_transform = None

        self.down_pos = None

        self.img_proc = None
        self.setMouseTracking(True)

    def initUI(self):
        self.setMinimumSize(800, 800)

    def setImage(self, img_proc):
        assert(isinstance(img_proc, ImageLoaderProcessor))
        self.img_proc = img_proc
        self.trans = QtGui.QTransform()
        self.fit_img_transform = None
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
        if not isinstance(self.full_transform, QtGui.QTransform):
            return

        mousepos = np.array([e.pos().x(), e.pos().y()])
        img_pos = self.full_transform.inverted()[0].map(float(e.pos().x()), float(e.pos().y()))

        if self.img_proc is None:
            return

        if e.buttons() != QtCore.Qt.NoButton:
            if self.down_pos is not None:
                inv_fulltrans = self.full_transform.inverted()[0]
                mouse_pos_delta = np.array(inv_fulltrans.map(*mousepos)) - np.array(inv_fulltrans.map(*self.down_pos))

                tmp_trans = QtGui.QTransform().translate(*mouse_pos_delta)
                self.trans = tmp_trans * self.down_trans
                self.update()
        else:
            x = int(img_pos[0])
            y = int(img_pos[1])
            if 0 <= x < self.img_proc.get_width() and 0 <= y < self.img_proc.get_height():
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
        inv_imgtrans = self.fit_img_transform.inverted()[0]
        mouse_pos_notfit = np.array(inv_imgtrans.map(*mousepos))

        tmp_trans = \
        QtGui.QTransform().translate(*(mouse_pos_notfit)).scale(additional_scale, additional_scale).translate(*(-mouse_pos_notfit))

        self.trans *= tmp_trans
        self.update()

    def updateTranform(self):
        size = self.size()
        w = size.width()
        h = size.height()
        curimage = self.img_proc.get_processed_image()

        if h / w > curimage.height() / curimage.width():
            fit_img_scale = w / curimage.width()
            fit_img_offset = (0, (h - fit_img_scale * curimage.height()) / 2)
        else:
            fit_img_scale = h / curimage.height()
            fit_img_offset = ((w - fit_img_scale * curimage.width()) / 2, 0)

        self.fit_img_transform = QtGui.QTransform().translate(*fit_img_offset).scale(fit_img_scale, fit_img_scale)
        self.full_transform = self.trans * self.fit_img_transform

    def resizeEvent(self, e):
        assert(isinstance(e, QtGui.QResizeEvent))
        self.fit_img_transform = None

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

            if self.fit_img_transform is None:
                self.updateTranform()

            self.full_transform = self.trans * self.fit_img_transform
            qp.setTransform(self.full_transform)

            qp.drawImage(QtCore.QPointF(0, 0), curimage)

        else:
            text = "Drop image here"
            qp.setFont(QtGui.QFont("Arial", 14))
            fm = QtGui.QFontMetrics(qp.font())
            pixelsWide = fm.width(text)
            qp.setPen(QtGui.QColor(255, 255, 255))
            qp.drawText((w-pixelsWide)//2, (h+fm.height())//2, text)
