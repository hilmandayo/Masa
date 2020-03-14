from typing import Dict, List, Tuple
import numpy as np
import cv2

from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

try:
    # relative import to prevent circular import error
    from ...widgets.image_button import ImageButton
except (ValueError, ImportError):
    import sys
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent / "widgets"))
    from image_button import ImageButton
    sys.path.append(str(_dir.parent.parent.parent.parent))
from Masa.core.data import Instance
from Masa.core.utils import convert_np
from Masa.core.utils import resize


class ImagesViewerView(qtw.QWidget):
    """A simple view container for images.

    TrackID - Images.
    """
    get_frames = qtc.Signal(tuple)
    jump_to = qtc.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

        # TEMP: temporary solve
        self._idx: int = None
        self._idx_map: Dict[dict] = {}

    def _set_widgets(self):
        self._scroll = qtw.QScrollArea()
        self.imgs_viewer_widget = qtw.QWidget()

    def _optimize_widgets(self):
        self._scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)

    def _set_layouts(self):
        # self.imgs_grid_layout = qtw.QGridLayout()
        self.layout_main = qtw.QVBoxLayout()
        self.layout_grid = qtw.QVBoxLayout()
        self.layout_grid_row = qtw.QVBoxLayout()
        # self.layout_col = qtw.QVBoxLayout()

    def _init(self):
        # put layout in each widget
        self.imgs_viewer_widget.setLayout(self.layout_main)
        self._scroll.setWidget(self.imgs_viewer_widget)

        # 'connect' each widget
        self._scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self._scroll)
        self.setLayout(self.layout_main)

    def init_data(self, instances: List[Instance]):
        frame_ids = []
        for instance in instances:
            self.add_to_row(instance)
            frame_ids.append(instance.frame_id)

        self.get_frames.emit(frame_ids) # emit list of frames

    def add_to_row(self, instance: Instance, get_image=False):
        track_id = str(instance.track_id)
        if not track_id in self._idx_map.keys():
            self._make_new_row(row_label=track_id,
                               row_meta={"object_class": instance.object_class,
                                     })

        image_btn = ImageButton()
        col_meta = {"frame_id": instance.frame_id,
                    "x1": instance.x1,
                    "y1": instance.y1,
                    "x2": instance.x2,
                    "y2": instance.y2}
        self._append_to_row(track_id, image_btn, col_meta)

        if get_image:
            self.get_frames.emit([instance.frame_id])


    def refresh_images(self, images: List[Tuple[int, np.ndarray]]):
        for idx, image in images:
            height, width = image.shape[:2]
            for row, info in self._idx_map.items():
                for col_meta in info["col_meta"]:
                    if idx == col_meta["frame_id"]:
                        x1 = col_meta["x1"]
                        y1 = col_meta["y1"]
                        x2 = col_meta["x2"]
                        y2 = col_meta["y2"]
                        if isinstance(x1, float):
                            x1 = int(x1 * width)
                            y1 = int(y1 * height)
                            x2 = int(x2 * width)
                            y2 = int(y2 * height)
                        crop = image[y1:y2 + 1, x1: x2 + 1]
                        col_meta["image"].set_np(crop)

    def delete_row(self, label):
        self._idx_map[label]


    def _make_new_row(self, row_label, row_meta):
        if self._idx is None:
            self._idx = 0
        else:
            self._idx += 1
        self.imgs_grid_layout.addWidget(qtw.QLabel(row_label), self._idx, 0)

        self._idx_map[row_label] = {"row": self._idx,
                                    "length": 1,
                                    "row_meta": row_meta,
                                    "col_meta": []}
        return self._idx

    def _append_to_row(self, label, image, col_meta):
        info = self._idx_map[label]
        self.imgs_grid_layout.addWidget(image, info["row"], info["length"])
        info["length"] += 1
        col_meta.update({"image": image})
        info["col_meta"].append(col_meta)

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    imgs_viewer = ImagesViewerView()

    dummy = np.zeros((320, 320, 3), np.uint8)
    instances = []
    i = 0
    for track_id in range(10):
        for frame_id in range(3):
            instances.append(Instance(
                track_id, "none", i, 0, 0, 320, 320, frame_id
            ))
    imgs_viewer.init_data(instances)
    imgs_viewer.refresh_images([(i, dummy) for i in range(3)])
    imgs_viewer.show()
    sys.exit(app.exec_())
