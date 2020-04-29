from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
from .images_viewer_view import ImagesViewerView


class SessionsVisualizerView(qtw.QScrollArea):
    def __init__(self, parent=None, cols=3):
        super().__init__(parent=parent)
        self._images_viewers = {}
        self.cols = cols

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

    def _set_widgets(self):
        self.imgs_viewers_widget = qtw.QWidget()

    def _set_layouts(self):
        self.main_layout = qtw.QVBoxLayout()
        self.main_layout.addLayout(qtw.QHBoxLayout())

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
        count = self.main_layout.count()
        row_layout = self.main_layout.itemAt(count - 1)
        if row_layout.count() >= self.cols:
            row_layout = qtw.QHBoxLayout()
            self.main_layout.addLayout(row_layout)

        row_layout.addWidget(img_viewer)
        # self.main_layout.addWidget(img_viewer)
        # TODO: Check below connections with other classes
        self._images_viewers[group] = img_viewer


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    svv = SessionsVisualizerView()
    svv.show()

    for i in range(10):
        svv.add_images_viewer("{i}", ImagesViewerView())

    sys.exit(app.exec_())
