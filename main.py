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
        self.test_image.read_image(r'C:\Users\phil\Desktop\me-pics\manu-50er.jpg')

        self.image_widget = None
        self.hist_widget = None

        self.initUI()

    def initUI(self):
        vbox = QtGui.QVBoxLayout()

        # Create the widget that displays the video frame
        self.image_widget = ImageWidget()
        self.image_widget.setImage(self.test_image)

        self.hist_widget = HistogramWidget()
        self.hist_widget.setImage(self.test_image)

        # Put everything together and show it
        vbox.addWidget(self.image_widget)
        vbox.addWidget(self.hist_widget)

        vbox.setMargin(0)

        self.setLayout(vbox)
        self.setWindowTitle('vu - Analytical Image Viewer')
        self.setAcceptDrops(True)
        self.show()

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
