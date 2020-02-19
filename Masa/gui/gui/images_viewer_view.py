from typing import Dict
import sys
import numpy as np
import cv2

from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

# For local testing.
try:
    # Prevent circular import
    from .image_button import ImageButton
except (ModuleNotFoundError, ImportError):
    sys.path.append("../../../")
    from image_button import ImageButton
from Masa.core.datahandler import FrameInfo
from Masa.core.utils import convert_np
from Masa.core.utils import resize


class ImagesViewerView(qtw.QWidget):
#     jump_to_frame = qtc.Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.set_widgets()
        self.optimize_widgets()
        self.set_layouts()
        self.init()

        # TEMP: temporary solve
        self._idx: int = None
        self._idx_map: Dict[dict] = {}

    def set_widgets(self):
        self.imgs_viewer_scroll = qtw.QScrollArea()
        self.imgs_viewer_widget = qtw.QWidget()

    def optimize_widgets(self):
        self.imgs_viewer_scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.imgs_viewer_scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)

    def set_layouts(self):
        self.imgs_grid_layout = qtw.QGridLayout()
        self.main_layout = qtw.QVBoxLayout()

    def init(self):
        # put layout in each widget
        self.imgs_viewer_widget.setLayout(self.imgs_grid_layout)
        self.imgs_viewer_scroll.setWidget(self.imgs_viewer_widget)

        # 'connect' each widget
        self.imgs_viewer_scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.imgs_viewer_scroll)
        self.setLayout(self.main_layout)

#     def sizeHint(self):
#         return qtc.QSize(600, 600)

    def add_to_row(self, data: FrameInfo):
        # idx, frame, x1, y1, x2, y2 = args
        # XXX: this is designed to be the same as in the viewer
        cv2.rectangle(data.frame, (data.x1, data.y1), (data.x2, data.y2), (0, 0, 255), 2)
        # frame = imutils.resize(data.frame, width=240)
        frame = resize(data.frame, width=240)

        # if isinstance(data.frame, np.ndarray):
        #     height, width = data.frame.shape[:2]
        #     frame = convert_np(frame)
        #     frame_icon = qtg.QIcon()
        #     frame_icon.addPixmap(frame)

        track_id = str(data.track_id)
        if not track_id in self._idx_map.keys():
            self._make_new_row(track_id)

        # frame_btn = qtw.QPushButton()
        # frame_btn.setIcon(frame_icon)
        # frame_btn.setIconSize(qtc.QSize(width, height))
        # frame_btn.setFixedSize(width, height)
        # frame_btn.clicked.connect(lambda: self.send_info(idx))
        image_btn = ImageButton(data.frame)
        self._append_to_row(track_id, data.tag, image_btn)

    def _make_new_row(self, row_label):
        if self._idx is None:
            self._idx = 0
        else:
            self._idx += 1
        self.imgs_grid_layout.addWidget(qtw.QLabel(row_label), self._idx, 0)

        self._idx_map[row_label] = {"row": self._idx, "length": 1, "tags": []}
        return self._idx

    def _append_to_row(self, label, tag, frame):
        info = self._idx_map[label]
        self.imgs_grid_layout.addWidget(frame, info["row"], info["length"])
        info["length"] += 1
        info["tags"].append(tag)

#     def send_info(self, idx):
#         self.jump_to_frame.emit(idx)

#     def reset(self):
#         count = self.form_layout.rowCount()
#         while self.form_layout.rowCount() > 0:
#             self.form_layout.removeRow(0)

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    imgs_viewer = ImagesViewerView()

    frame_info = FrameInfo(
        frame=np.zeros([69, 121, 3], np.uint8), x1=11, y1=11, x2=22, y2=22,
        object_class="Test", frame_id=1, track_id=0, tag="tekitou"
    )

    imgs_viewer.add_to_row(frame_info)
    imgs_viewer.add_to_row(frame_info)
    imgs_viewer.add_to_row(frame_info)

    frame_info = FrameInfo(
        frame=np.zeros([69, 121, 3], np.uint8), x1=11, y1=11, x2=22, y2=22,
        object_class="Test2", frame_id=1, track_id=1, tag="tekitou"
    )

    imgs_viewer.add_to_row(frame_info)
    imgs_viewer.add_to_row(frame_info)
    imgs_viewer.add_to_row(frame_info)

    imgs_viewer.show()
    sys.exit(app.exec_())
