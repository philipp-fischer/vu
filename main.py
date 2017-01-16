import os
import sys
from PyQt4 import QtGui, QtCore
from image_widget import *
from histogram_widget import *
from image_loader_processor import *


# TODO:
# - Do histogram computation in other process (multiprocessing module)
# - R,G,B histograms
# - Support 16 bit images

class VUWidget(QtGui.QWidget):
    def __init__(self):
        super(VUWidget, self).__init__()

        self.test_image = ImageLoaderProcessor()
        self.test_image.read_image(r'C:\Users\Public\Documents\refRotatedBoxedDepth_avg.bmp')

        self.image_widget = None
        self.hist_widget = None
        self.info_label = None

        self.initUI()

    def initUI(self):
        vbox = QtGui.QVBoxLayout()

        # Create the widget that displays the video frame
        self.image_widget = ImageWidget()
        self.image_widget.setImage(self.test_image)

        self.hist_widget = HistogramWidget()
        self.hist_widget.setImage(self.test_image)

        self.info_label = QtGui.QLabel()
        self.info_label.setText("Info")
        self.info_label.setMaximumHeight(50)
        self.info_label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

        # Put everything together and show it
        vbox.addWidget(self.image_widget)
        vbox.addWidget(self.hist_widget)
        vbox.addWidget(self.info_label)

        vbox.setMargin(0)

        self.setLayout(vbox)
        self.setWindowTitle('vu - Analytical Image Viewer')
        self.setAcceptDrops(True)
        self.show()

        # Connect signals and slots
        self.image_widget.signalNewPixelInfo.connect(self.update_info_label)

    def update_info_label(self, info):
        self.info_label.setText(str(info))

    def resizeEvent(self, e):
        super(VUWidget, self).resizeEvent(e)
        assert(isinstance(e, QtGui.QResizeEvent))
        if self.isMaximized():
            self.showFullScreen()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            if self.isMaximized() or self.isFullScreen():
                self.showNormal()
            else:
                self.close()
        elif e.key() == QtCore.Qt.Key_F5:
            self.test_image.reload()
            self.image_widget.update()  # Should later be done by signal/slot
        elif e.key() == QtCore.Qt.Key_Left:
            self.test_image = ImageLoaderProcessor()
            self.test_image.read_image(r'C:\Users\Public\Documents\refRotatedBoxedDepth_avg.bmp')
            self.image_widget.setImage(self.test_image)
        elif e.key() == QtCore.Qt.Key_Right:
            self.test_image = ImageLoaderProcessor()
            self.test_image.read_image(r'C:\Users\Public\Documents\refRotatedBoxedDepth_median.bmp')
            self.image_widget.setImage(self.test_image)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        path = str(url.toLocalFile())
        if os.path.isfile(path):
            # Load image
            pass

    def closeEvent(self, e):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    vu_widget = VUWidget()

    sys.exit(app.exec_())
