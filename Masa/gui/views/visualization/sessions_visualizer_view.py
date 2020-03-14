from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
try:
    from .images_viewer_view import ImagesViewerView
except (ValueError, ImportError, ModuleNotFoundError):
    from images_viewer_view import ImagesViewerView
    import sys;
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent.parent.parent))


class SessionsVisualizerView(qtw.QScrollArea):
    def __init__(self, parent=None,):
        super().__init__(parent=parent)
        self._images_viewers = {}

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

    def _set_widgets(self):
        self.imgs_viewers_widget = qtw.QWidget()

    def _set_layouts(self):
        self.main_layout = qtw.QVBoxLayout()

    def _optimize_widgets(self):
        self.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)

    def _init(self):
        # put layout in each widget
        self.imgs_viewers_widget.setLayout(self.main_layout)
        self.setWidget(self.imgs_viewers_widget)

        # 'connect' each widget
        self.setWidgetResizable(True)

    def _add_images_viewer(self, group: str, img_viewer: ImagesViewerView):
        """Add an ImagesViewerView object."""
        self.main_layout.addWidget(img_viewer)
        self._images_viewers[group] = img_viewer


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    svv = SessionsVisualizerView()
    svv.show()

    for i in range(10):
        svv.add_images_viewer("{i}", ImagesViewerView())

    sys.exit(app.exec_())
