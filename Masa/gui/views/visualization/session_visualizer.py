from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
try:
    from .images_viewer_view import ImagesViewerView
except ModuleNotFoundError:
    from images_viewer_view import ImagesViewerView
    import sys;
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent.parent.parent))
from Masa.core.datahandler import DataHandler

class SessionVisualizerView(qtw.QWidget):
    def __init__(self, data_handler: DataHandler, parent=None,):
        super().__init__(parent=parent)

        self.object_class = set()

if __name__ == '__main__':
    pass
