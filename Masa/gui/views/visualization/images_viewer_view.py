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
from Masa.core.utils import convert_np, resize, SignalPacket


class ImagesViewerView(qtw.QWidget):
    """A simple view container for images.

    TrackID - Images.
    """
    get_frames = qtc.Signal(SignalPacket)
    jump_to = qtc.Signal(SignalPacket)
    deleted = qtc.Signal(SignalPacket)  # data=tuple(label: int, col: int)

    def __init__(self, name="ImagesViewerView", parent=None):
        super().__init__(parent)
        self.name = name

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

        # TEMP: temporary solve
        self._idx: int = None
        self._grid_map: Dict[dict] = {}

    def _set_widgets(self):
        self.scroll = qtw.QScrollArea()
        self.grid_widget = qtw.QWidget()

    def _optimize_widgets(self):
        self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)

    def _set_layouts(self):
        self.layout_main = qtw.QVBoxLayout()
        self.layout_grid = qtw.QVBoxLayout()
        # self.layout_col = qtw.QVBoxLayout()

    def _init(self):
        # put layout in each widget
        self.grid_widget.setLayout(self.layout_grid)
        self.scroll.setWidget(self.grid_widget)

        # 'connect' each widget
        self.scroll.setWidgetResizable(True)
        self.layout_main.addWidget(self.scroll)
        self.setLayout(self.layout_main)

    def init_data(self, instances: List[Instance]):
        frame_ids = []
        for instance in instances:
            self.add_to_row(instance)
            frame_ids.append(instance.frame_id)

        self.get_frames.emit(SignalPacket(sender=self.name, data=frame_ids)) # emit list of frames

    def add_to_row(self, instance: Instance, get_image=False):
        track_id = instance.track_id
        if not track_id in self._grid_map.keys():
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
            self.get_frames.emit(SignalPacket(
                sender=self.name, data=[instance.frame_id])
            )

    def __len__(self):
        return len(self._grid_map.keys())

    def refresh_images(self, images: List[Tuple[int, np.ndarray]]):
        for idx, image in images:
            height, width = image.shape[:2]
            for label, row_info in self._grid_map.items():
                for col_meta in row_info["col_meta"]:
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

    def delete(self, label: int, col: int = None):
        if col is None:
            self._delete_row(label)
            self._update_label()
            col = -1
        else:
            self._delete_col(label, col)

        self.deleted.emit(SignalPacket(
            sender=self.name, data=(label, col))
        )

    def _delete_row(self, label: int):
        while self._grid_map[label]["col_meta"]:
            self._delete_col(label)

        self.layout_grid.itemAt(label).widget().deleteLater()
        del self._grid_map[label]

    def _delete_col(self, label: int, col: int = None):
        info = self._grid_map[label]
        # TODO: Is this good thing???
        if col is None:
            col = len(info["col_meta"]) - 1
        info["widget"].layout().itemAt(col + 1).widget().deleteLater()
        info["col_meta"][col]["image"].deleteLater()
        
        del info["col_meta"][col]

    def _make_new_row(self, row_label, row_meta):
        row_widget = qtw.QWidget()
        row_widget.setLayout(qtw.QHBoxLayout())
        row_widget.layout().addWidget(qtw.QLabel(str(row_label)))
        self.layout_grid.addWidget(row_widget)

        self._grid_map[row_label] = {"widget": row_widget,
                                    # "length": 1,
                                    "row_meta": row_meta,
                                    "col_meta": []}

    def _append_to_row(self, label, image, col_meta):
        row = self._grid_map[label]
        row["widget"].layout().addWidget(image)
        # row["length"] += 1
        col_meta.update({"image": image})
        row["col_meta"].append(col_meta)

    def _update_label(self):
        _grid_map = {}
        idx = 0
        for idx, (label, col_info) in enumerate(self._grid_map.items()):
            col_info["widget"].layout().itemAt(0).widget().deleteLater()
            col_info["widget"].layout().insertWidget(0, qtw.QLabel(str(idx)))
            _grid_map.update({idx: col_info})
        self._grid_map = _grid_map

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    imgs_viewer = ImagesViewerView()

    dummy = np.full((320, 320, 3), 144, np.uint8)
    instances = []
    i = 0
    for track_id in range(10):
        r = 3
        if track_id == 2:
            r = 4
        for frame_id in range(r):
            instances.append(Instance(
                track_id, "none", i, 0, 0, 320, 320, frame_id
            ))
    imgs_viewer.init_data(instances)
    imgs_viewer.refresh_images([(i, dummy) for i in range(3)])
    imgs_viewer.show()
    # imgs_viewer.delete(0, 2)
    imgs_viewer.delete(2, 2)
    sys.exit(app.exec_())
