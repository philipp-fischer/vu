import os
import re
from PyQt4.QtCore import QObject, pyqtSignal
from image_loader_processor import *


class FolderAccessor(QObject):
    supported_extensions = [
        'JPG', 'JPEG', 'BMP', 'PNG', 'TIF', 'GIF'
    ]

    signalFileChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.file_list = []
        self.position = 0
        self.extension_regex = re.compile("\\.(" + '|'.join(FolderAccessor.supported_extensions) + ")$", re.IGNORECASE)

        self.current_image = None

    def load_folder(self, file_or_folder):
        # Check if it is a folder or file. Get the folder.
        if os.path.isdir(file_or_folder):
            folder_path = file_or_folder
        else:
            folder_path = os.path.split(file_or_folder)[0]

        # Scan this folder for images of the supported type (by file extension)
        self.file_list = []
        for entry in os.listdir(folder_path):
            cur_entry_path = os.path.join(folder_path, entry)
            if os.path.isfile(cur_entry_path) and self.extension_regex.search(entry) is not None:
                self.file_list.append(os.path.abspath(cur_entry_path))

        # Sort the files alphabetically
        self.file_list = sorted(self.file_list)

        # If the argument was a file, make sure to start with that file as the current position
        if os.path.isfile(file_or_folder):
            try:
                self.position = self.file_list.index(os.path.abspath(file_or_folder))
            except ValueError:
                self.position = 0
        else:
            self.position = 0

        self.signalFileChanged.emit()

    def get_current_filename(self):
        return self.file_list[self.position]

    def get_current_image(self):
        self.current_image = ImageLoaderProcessor()
        self.current_image.read_image(self.get_current_filename())
        return self.current_image

    def move_position(self, shift_amount):
        self.position = (self.position + shift_amount) % len(self.file_list)

        while self.position < 0:
            self.position += len(self.file_list)

        self.signalFileChanged.emit()


if __name__ == '__main__':
    # Unit Test
    ff = FolderAccessor()
    ff.load_folder(r'C:\Users\phil\Desktop\hp-leipzig.jpg')
    print(ff.file_list)
    print(ff.get_current_filename(), ff.position)
    ff.move_position(-1)
    print(ff.get_current_filename(), ff.position)
