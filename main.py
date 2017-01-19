import os
import sys
from PyQt4 import QtGui
from image_widget import *
from histogram_widget import *
from image_loader_processor import *
from folder_accessor import *


# TODO:
# - Do histogram computation in other process (multiprocessing module)
# - R,G,B histograms
# - Support 16 bit images

class VUWidget(QtGui.QWidget):
    def __init__(self):
        super(VUWidget, self).__init__()

        self.folder_accessor = FolderAccessor()

        self.image_widget = None
        self.hist_widget = None
        self.info_label = None

        self.initUI()

    def initUI(self):
        outer_hbox = QtGui.QHBoxLayout()

        vbox = QtGui.QVBoxLayout()

        # Create the widget that displays the video frame
        self.image_widget = ImageWidget()
        self.hist_widget = HistogramWidget()

        self.info_label = QtGui.QLabel()
        info_font = QtGui.QFont()
        info_font.setFamily("Lucida")
        info_font.setFixedPitch(True)
        self.info_label.setText("Info")
        self.info_label.setFont(info_font)
        self.info_label.setMinimumWidth(200)
        self.info_label.setMaximumWidth(200)
        self.info_label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

        # Put everything together and show it
        vbox.addWidget(self.image_widget)
        vbox.addWidget(self.hist_widget)

        vbox.setMargin(0)

        outer_hbox.addLayout(vbox)
        outer_hbox.addWidget(self.info_label)

        outer_hbox.setMargin(0)

        self.setLayout(outer_hbox)
        self.setWindowTitle('vu - Analytical Image Viewer')
        self.setAcceptDrops(True)
        self.show()

        # Connect signals and slots
        self.image_widget.signalNewPixelInfo.connect(self.update_info_label)
        self.folder_accessor.signalFileChanged.connect(self.slotUpdateImageFromAccessor)

    def update_info_label(self, info):
        label_text = "Pos [%4d, %4d]\nColor = %s" % \
                     (info['img_pos'][0], info['img_pos'][1],
                      str(info['color']))
        self.info_label.setText(label_text)

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
            self.folder_accessor.move_position(-1)
        elif e.key() == QtCore.Qt.Key_Right:
            self.folder_accessor.move_position(1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        path = str(url.toLocalFile())
        if os.path.isfile(path):
            self.folder_accessor.load_folder(path)
            print(path)

    def slotUpdateImageFromAccessor(self):
        cur_image = self.folder_accessor.get_current_image()
        self.image_widget.setImage(cur_image)
        self.hist_widget.setImage(cur_image)

    def closeEvent(self, e):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    vu_widget = VUWidget()

    sys.exit(app.exec_())
