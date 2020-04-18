from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Tuple, Union, Optional
import numpy as np
import uuid
import cv2

from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
from Masa.core.data import Instance, TrackedObject
from Masa.core.utils import convert_np, resize, SignalPacket, DataUpdateInfo
from ..widgets.image_button import ImageButton


# TODO: Can this be considered as `View`?
# TODO: Do not store data here!
class ImagesViewerView(qtw.QWidget):
    """A simple view container for images.

    TrackID - Images.
    """
    req_frames = qtc.Signal(SignalPacket)
    jump_to_frame = qtc.Signal(SignalPacket)
    update_data = qtc.Signal(SignalPacket)
    req_instance = qtc.Signal(SignalPacket)

    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.name = name
        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

        self._grid_map: Dict[dict] = {}

    def _set_widgets(self):
        self.scroll = qtw.QScrollArea()
        self.grid_widget = qtw.QWidget()

    def _optimize_widgets(self):
        self.scroll.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)

    def _set_layouts(self):
        self.layout_main = qtw.QVBoxLayout()
        self.layout_grid = qtw.QBoxLayout(qtw.QBoxLayout.TopToBottom)
        # self.layout_col = qtw.QVBoxLayout()

    def _init(self):
        # put layout in each widget
        self.grid_widget.setLayout(self.layout_grid)
        self.scroll.setWidget(self.grid_widget)

        # 'connect' each widget
        self.scroll.setWidgetResizable(True)
        self.layout_main.addWidget(self.scroll)
        self.setLayout(self.layout_main)

    @property
    def frame_ids(self):
        frame_ids = set()
        for row in self._grid_map.values():
            for img_btn in row["image_buttons"]:
                frame_ids.add(img_btn.frame_id)

        return list(frame_ids)

    def set_frames_sl(self, packet: SignalPacket):
        self.set_frames(packet.data)

    def init_data(self, tobjs: List[TrackedObject]):
        for tobj in tobjs:
            self._add(tobj)

    def request_frames(self):
        self.req_frames.emit(
            SignalPacket(sender=self.__class__.__name__, data=self.frame_ids)
        )

    @property
    def tags(self):
        tags = defaultdict(set)
        for row_info in self._grid_map.values():
            for img_btn in row_info["image_buttons"]:
                for tag_key, tag_value in img_btn.meta.items():
                    tags[tag_key].add(tag_value)

        return {k: list(v) for k, v in tags.items()}

    def __len__(self):
        return len(self._grid_map.keys())

    def _request_instance_sl(self, packet: SignalPacket):
        self._request_instance(packet.data)
        
    def _request_instance(self, pos: Tuple[int, int]):
        self.req_instance.emit(
            SignalPacket(sender=self.__class__.__name__, data=pos)
        )

    def set_frames(self, frames: List[Tuple[int, np.ndarray]]):
        for idx, frame in frames:
            height, width = frame.shape[:2]
            for label, row_info in self._grid_map.items():
                for img_btn in row_info["image_buttons"]:
                    if img_btn.frame_id == idx:
                        x1 = img_btn.x1
                        y1 = img_btn.y1
                        x2 = img_btn.x2
                        y2 = img_btn.y2
                        if isinstance(x1, float):
                            if x1 < 1:
                                x1 = int(x1 * width)
                                y1 = int(y1 * height)
                                x2 = int(x2 * width)
                                y2 = int(y2 * height)
                            else:
                                x1 = int(x1)
                                y1 = int(y1)
                                x2 = int(x2)
                                y2 = int(y2)
                        crop = frame[y1:y2 + 1, x1: x2 + 1]
                        img_btn.set_np(crop)

    def __getitem__(self, idx):
        try:
            return self._grid_map[idx]
        except KeyError:
            raise IndexError(f"Label of {idx} is not created yet.")

    def req_delete(self, label: int, col: int = None):
        dui = DataUpdateInfo(delete=(label, col))
        self.update_data.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

    def replace(self, label, instance: Instance, image=None):
        if image is None:
            image = self._grid_map[label]["image_buttons"][instance.instance_id]
        self._delete_col(label, instance.instance_id)
        self.add(label=label, instance=instance, image=image)

    def move(self, old_pos: Tuple[int, int], new_label, instance: Instance):
        img_btn = self._grid_map[old_pos[0]]["image_buttons"][old_pos[1]]
        self._delete(old_pos[0], old_pos[1])
        img_btn.change(label=new_label,
                       instance_id=instance.instance_id,
                       track_id=instance.track_id
        )
        self._replace(new_label, instance)

    def delete(self, label, col=None):
        if col is None:
            self._delete_row(label)
        else:
            self._delete_col(label, col)

    def _delete_row(self, label: int, update=True):
        while self._grid_map[label]["image_buttons"]:
            # Delete images
            self._delete_col(label, update=False)

        # Take stretch and
        # delete label
        self._grid_map[label]["widget"].layout().takeAt(1)
        self._grid_map[label]["widget"].layout().itemAt(0).widget().deleteLater()
        # self._grid_map[label]["widget"].layout().itemAt(1).widget().deleteLater()
        self.layout_grid.itemAt(label).widget().deleteLater()
        if update:
            self._update(label - 1, "delete")

    def _delete_col(self, label: int, col=None, update=True):
        row_info = self._grid_map[label]
        if col is None:
            col = len(row_info["image_buttons"]) - 1
        # TODO: Is this good thing???
        row_info["widget"].layout().itemAt(col + 2).widget().deleteLater()
        row_info["image_buttons"][col].deleteLater()
        del row_info["image_buttons"][col]
        if update:
            if row_info["image_buttons"]:
                self._update(label)
            else:
                self._delete_row(label, update=True)

    def labels_mapping(self, track_id=None):
        retval = [(label, row_info["image_buttons"][0].track_id)
                  for label, row_info in self._grid_map.items()]
        if track_id is not None:
            try:
                idx = [r[1] for r in retval].index(track_id)
                retval = retval[idx][0]
            except ValueError:
                retval = None

        return retval

    def add(self, obj: Union[Instance, TrackedObject],
            image: Optional[np.ndarray] = None):
        self._add(obj, image)

        if isinstance(obj, TrackedObject):
            frame_ids = [ins.frame_id for ins in obj]
        elif isinstance(obj, Instance):
            frame_ids = [obj.frame_id]

        self.req_frames.emit(
            SignalPacket(sender=self.__class__.__name__, data=frame_ids)
        )

        
    def _add(self, obj: Union[Instance, TrackedObject],
            image: Optional[np.ndarray] = None):
        label = self.labels_mapping(obj.track_id)

        if isinstance(obj, TrackedObject):  # and len(obj) == 1:
            if label is None:
                label = len(self)
            instances = obj[:]
        elif isinstance(obj, Instance):
            if label is None:
                raise ValueError(f"{obj.track_id} is not yet created!")
            instances = [obj]
        else:
                raise ValueError(f"Do not support of data {type(obj)}.")

        image_btns = []
        frame_ids = []
        for ins in instances:
            image_btn = ImageButton(image=image,
                                    frame_id=ins.frame_id,
                                    track_id=ins.track_id,
                                    instance_id=ins.instance_id,
                                    x1=ins.x1, 
                                    y1=ins.y1, 
                                    x2=ins.x2, 
                                    y2=ins.y2, 
                                    meta=ins.tags
                                    # label=label,
            )
            frame_ids.append(ins.frame_id)
            image_btn.right_clicked.connect(
                self._request_instance_sl
            )
            image_btn.left_clicked.connect(
                self._jump_to_frame_sl
            )
            image_btns.append(image_btn)

        if isinstance(obj, TrackedObject):
            self._add_tobj(label, image_btns)
        else:
            self._add_instance(label, image_btns)

    def _jump_to_frame_sl(self, packet: SignalPacket):
        self.jump_to_frame.emit(
            SignalPacket(sender=self.__class__.__name__, data=packet.data)
        )

    def _make_new_row(self, row_label, row_meta=None):
        if row_label in self._grid_map.keys():
            self._update(row_label - 1, "insert")

        row_widget = qtw.QWidget()
        # TODO: Use QListWidget???
        # https://www.qtcentre.org/threads/33443-how-to-insert-one-widget-between-another-two-widgets-ina-a-list-of-widgets)
        row_widget.setLayout(qtw.QBoxLayout(qtw.QBoxLayout.LeftToRight))

        info_widget = qtw.QWidget()
        info_widget.setLayout(qtw.QBoxLayout(qtw.QBoxLayout.TopToBottom))
        info_widget.layout().addWidget(qtw.QLabel(str(row_label)))

        row_widget.layout().addWidget(info_widget)
        row_widget.layout().addStretch()
        self.layout_grid.insertWidget(row_label, row_widget)

        self._grid_map[row_label] = {"widget": row_widget,
                                     "row_meta": row_meta,
                                     "col_meta": [],
                                     "image_buttons": []}


    def _add_tobj(self, label: int, images):
        # if not label in self._grid_map.keys():
        #     raise ValueError(f"No {label} created yet!")

        if label == len(self):
            self._append_tobj(label, images)
        elif label < len(self):
            self._insert_tobj(label, images)
            # self._update(label)
        else:
            raise ValueError(f"Got label of {label}")

        (self._grid_map[label]["widget"].layout().itemAt(0).widget().layout()
         .addWidget(qtw.QLabel(f"<b>Track ID<\b>: {str(images[0].track_id)}")))


    def _append_tobj(self, label, images):
        self._make_new_row(label)
        row = self._grid_map[label]
        for image in images:
            row["widget"].layout().addWidget(image)
            row["image_buttons"].append(image)

    def _insert_tobj(self, label, images):
        self._make_new_row(label)
        row = self._grid_map[label]
        for image in images:
            row["widget"].layout().addWidget(image)
            row["image_buttons"].append(image)


    def _add_instance(self, label: int, images):
        if not label in self._grid_map.keys():
            raise ValueError(f"No {label} created yet!")
        if len(images) != 1:
            raise ValueError(f"Still do not support adding instances of len={len(images)}")

        image = images[0]
        if image.instance_id == len(self._grid_map[label]["image_buttons"]):
            self._append_instance(label, image)
        elif image.instance_id < len(self._grid_map[label]["image_buttons"]):
            self._insert_instance(label, image.instance_id, image)
            self._update(label)
        else:
            raise ValueError(f"Cannot add image of instance_id={image.instance_id}")


    def _append_instance(self, label, image):
        row = self._grid_map[label]
        row["widget"].layout().addWidget(image)
        row["image_buttons"].append(image)

    def _insert_instance(self, label, col, image):
        row = self._grid_map[label]
        row["widget"].layout().insertWidget(col, image)
        row["image_buttons"].insert(col, image)

    def _update(self,
                label_keep: int,
                mode: Optional[Union[str, int]] = None):
        """Handle updating internal `_grid_map`."""

        if mode in ["insert", "delete", 1, -1]:
            if mode == "delete":
                if label_keep == len(self._grid_map) - 2:
                    # We only deleted the end of `self._grid_map`.
                    # Assuming _delete already handle everything.
                    del self._grid_map[label_keep + 1]
                    return

            new_grid_map = {k:self._grid_map[k]
                            for k in self._grid_map
                            if k <= label_keep}

            if mode == "insert":
                new_grid_map[label_keep + 1] = {}
                new_key_start = label_keep + 2
                old_key_start = label_keep + 1
                update_track_id = 1
            elif mode =="delete":
                new_key_start = label_keep + 1
                old_key_start = label_keep + 2
                update_track_id = -1
            else:
                new_key_start = label_keep + 1
                old_key_start = label_keep + 1
                update_track_id = mode

            for new_key, old_key in enumerate(
                    range(old_key_start, len(self._grid_map)), new_key_start):
                row_info = self._grid_map[old_key]

                info_widget = row_info["widget"].layout().itemAt(0).widget() # .deleteLater()


                # row_info["widget"].layout().insertWidget(0, qtw.QLabel(str(new_key)))
                new_grid_map[new_key] = row_info
                self._update_col(row_info, update_track_id=update_track_id)

                new_label = qtw.QLabel(str(new_key))
                new_tid = qtw.QLabel(
                    f'<b>Track ID<\b>: {str(row_info["image_buttons"][0].track_id)}'
                )

                info_widget.layout().itemAt(0).widget().deleteLater()
                info_widget.layout().itemAt(1).widget().deleteLater()
                info_widget.layout().addWidget(new_label)
                info_widget.layout().addWidget(new_tid)

            self._grid_map = new_grid_map

        else:
            row_info = self._grid_map[label_keep]
            self._update_col(row_info)

    def _update_col(self, row_info, update_track_id: Optional[int] = None):
        for idx, img_btn in enumerate(row_info["image_buttons"]):
            img_btn.set_instance_id(idx)
            if isinstance(update_track_id, int):
                img_btn.track_id += update_track_id

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    imgs_viewer = ImagesViewerView("dummy")

    dummy = np.full((320, 320, 3), 144, np.uint8)
    instances = []
    for track_id in range(10):
        r = 3
        if track_id == 2:
            r = 4
        for i, frame_id in enumerate(range(r)):
            instances.append(Instance(
                track_id, "none", i, 0, 0, 320, 320, frame_id,
                {"view": "big", "time": "morning"}
            ))
    imgs_viewer.init_data(instances)
    imgs_viewer.refresh_images([(i, dummy) for i in range(3)])
    imgs_viewer.delete(0, 2)
    imgs_viewer.delete(2, 2)
    imgs_viewer.show()
    sys.exit(app.exec_())
