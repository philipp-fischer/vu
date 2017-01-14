import cv2
import numpy as np
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject, pyqtSignal


class ImageLoaderProcessor(QObject):
    """Loads and keeps an image file and does all necessary pre-processing like histogram computation etc."""

    signalImageUpdated = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Pointer to the original cv2 numpy image with view on inverted channels (don't modify)
        self.original_ndimage = None

        # Pointer to a copy that will be referenced in the QImage (can be modified)
        self.ndimage = None

        # Histogram
        self.histogram = None

        # Image modifiers
        self.modifiers = {
            'level_lower': 0,
            'level_upper': 255
        }

    def read_image(self, filename):
        image = cv2.imread(filename)

        self.original_ndimage = image[:, :, ::-1]
        self.ndimage = self.original_ndimage.copy()

        self.width = image.shape[1]
        self.height = image.shape[0]

        self.bytes_per_line = self.width * 3

        self.curimage = QtGui.QImage(self.ndimage.data, self.width, self.height,
                                     self.bytes_per_line, QtGui.QImage.Format_RGB888)

        # Set data pointer of QImage to our ndarray
        self.curimage.ndarray = self.ndimage

        self.compute_histogram()

    def set_modifiers(self, modifier_change):
        self.modifiers.update(modifier_change)
        self.update_modified_image()

    def update_modified_image(self):
        # Levels
        lower = self.modifiers['level_lower']
        upper = self.modifiers['level_upper']
        new_image = self.original_ndimage.copy()
        new_image = np.clip((new_image.astype(np.float32) - lower) * 255.0 / (upper - lower), 0, 255)

        # Write into old buffer
        self.ndimage[:, :, :] = new_image.astype(np.uint8)

        self.signalImageUpdated.emit()

    def compute_histogram(self):
        bin_boundaries = range(0, 256)
        self.histogram = list(np.histogram(self.original_ndimage, bin_boundaries))

        # Normalize maximum of histogram to 1
        maxval = np.max(self.histogram[0])
        self.histogram[0] = self.histogram[0].astype(np.float32) / float(maxval)

    def get_histogram(self):
        return self.histogram

    def get_processed_image(self):
        return self.curimage

