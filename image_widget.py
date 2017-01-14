from PyQt4 import QtGui, QtCore, Qt
import numpy as np
import cv2


class ImageWidget(QtGui.QWidget):
    def __init__(self):
        super(ImageWidget, self).__init__()

        self.curimage = None
        self.initUI()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.translation = np.array([0, 0], dtype=np.float32)
        self.scaling = 1.0

        self.trans = QtGui.QTransform()
        self.down_pos = None

        # self.setMouseTracking(True)

    def initUI(self):
        self.setMinimumSize(600, 600)

    def setImage(self, image_filename):
        image = cv2.imread(image_filename)

        total = image[:, :, ::-1].copy()
        w = image.shape[1]
        h = image.shape[0]
        bytes_per_line = w * 3

        self.curimage = QtGui.QImage(total.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.curimage.ndarray = total
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

        self.update()

    def mouseMoveEvent(self, e):
        assert(isinstance(e, QtGui.QMouseEvent))
        if self.down_pos is not None:
            mousepos = np.array([e.pos().x(), e.pos().y()])
            tmp_trans = QtGui.QTransform().translate(*(mousepos - self.down_pos))
            self.trans = self.down_trans * tmp_trans
            self.update()

    def wheelEvent(self, e):
        assert(isinstance(e, QtGui.QWheelEvent))
        additional_scale = 1.1 ** (e.delta() / 50)

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

        if self.curimage is not None:
            assert(isinstance(self.curimage, QtGui.QImage))
            qp.setTransform(self.trans)

            qp.drawImage(QtCore.QPointF(0, 0), self.curimage)

        else:
            text = "Drop image here"
            qp.setFont(QtGui.QFont("Arial", 14))
            fm = QtGui.QFontMetrics(qp.font())
            pixelsWide = fm.width(text)
            qp.setPen(QtGui.QColor(255, 255, 255))
            qp.drawText((w-pixelsWide)//2, (h+fm.height())//2, text)
