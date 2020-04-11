from collections import defaultdict
from typing import List, Tuple
from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

import numpy as np

try:
    from Masa.core.data import Instance, TrackedObject
    from Masa.models import Buffer
    # TODO: Make `SessionsVisualizerView` or `SessionVisualizerView`?
    from ..views.visualization.sessions_visualizer_view import SessionsVisualizerView, ImagesViewerView
    from ..dialog.instance_editor_dialog import InstanceEditorDialog
except (ValueError, ImportError, ModuleNotFoundError):
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    import sys

    sys.path.append(str(_dir.parent / "views" / "visualization"))
    from sessions_visualizer_view import SessionsVisualizerView
    from images_viewer_view import ImagesViewerView

    sys.path.append(str(_dir.parent / "dialog"))
    from instance_editor_dialog import InstanceEditorDialog

    # sys.path.append(str(_dir.parent.parent / "core" / "data"))
    # from data import Instance

    # sys.path.append(str(_dir.parent.parent / "models"))
    # from buffer import Buffer

from Masa.models import DataHandler
from Masa.core.utils import SignalPacket, DataUpdateInfo


class SessionVisualizer(qtw.QWidget):
    req_frames = qtc.Signal(SignalPacket)
    req_datainfo = qtc.Signal(SignalPacket)
    prop_data_change = qtc.Signal(SignalPacket)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

    def _set_widgets(self):
        self.view = SessionsVisualizerView()

    def _optimize_widgets(self):
        pass

    def _set_layouts(self):
        self.main_layout = qtw.QVBoxLayout()

    def _init(self):
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.view)

    def __len__(self):
        return len(self.view._images_viewers)

    def __getitem__(self, idxs):
        return list(self.view._images_viewers.values())[idxs]

    def get(self, name):
        return self.view._images_viewers[name]

    def __iter__(self):
        self._iter = iter(self.view._images_viewers)
        self._iter_idx = None
        return self

    def __next__(self):
        try:
            next_key = next(self._iter)
        except StopIteration:
            raise StopIteration()

        next_val = self.view._images_viewers[next_key]
        if self._iter_idx is None:
            self._iter_idx = 0
        else:
            self._iter_idx += 1

        return next_val

    def set_frames(self, frames: List[Tuple[int, np.ndarray]]):
        # TODO: This can be optimized.
        for image_viewer in self:
            image_viewer.set_frames(frames)
        
    def set_frames_sl(self, packet: SignalPacket):
        self.set_frames(packet.data)
        

    def init_data(self, tobjs: List[TrackedObject]):
        # Signal must be connected for image acquisitions.
        obj_cls_tobjs = defaultdict(list)
        for tobj in tobjs:
            obj_cls_tobjs[tobj.object_class].append(tobj)

        for oc in obj_cls_tobjs.keys():
            imv = ImagesViewerView(name=oc)
            imv.req_instance.connect(self.request_data_sl)
            imv.req_frames.connect(self.request_frames_sl)
            self.view._add_images_viewer(oc, imv)

        for name, images_viewer in self.view._images_viewers.items():
            images_viewer.init_data(obj_cls_tobjs[name])

        self.req_frames.emit(
            SignalPacket(sender=self.__class__.__name__, data=self.frame_ids)
        )

    def request_frames_sl(self, packet: SignalPacket):
        self.req_frames.emit(
            SignalPacket(sender=self.__class__.__name__, data=packet.data)
        )
        

    def labels_mappings(self, track_id=None):
        retval = []
        pass
        if track_id is not None:
            try:
                idx = [r[1] for r in retval].index(track_id)
                retval = retval[idx][0]
            except ValueError:
                retval = None

        return retval

    def request_data_sl(self, packet: SignalPacket):
        self.request_data(packet.data)
        
    def request_data(self, pos: Tuple[int, int]):
        self.req_datainfo.emit(
            SignalPacket(sender=self.__class__.__name__, data=pos)
        )

    @property
    def tags(self):
        tags = defaultdict(set)
        for iv in self.view._images_viewers.values():
            for tag_key, tag_value in iv.tags.items():
                tags[tag_key] = tags[tag_key].union(tag_value)

        return {k: list(v) for k, v in tags.items()}

    def receive_datainfo_sl(self, packet: SignalPacket):
        di = packet.data
        if di.tobj is not None:
            raise ValueError(f"Support for `TrackedObject` is not implemented yet.")

        ied = InstanceEditorDialog(di.instance, di.obj_classes, di.tags)
        ied.prop_data_change.connect(self._propogate_data_change_sl)
        ied.exec_()

    def _propogate_data_change_sl(self, packet: SignalPacket):
        # CONT: Propagate this...
        self.prop_data_change.emit(
            SignalPacket(sender=self.__class__.__name__, data=packet.data)
        )

    def data_update_sl(self, packet: SignalPacket):
        dui: DataUpdateInfo = packet.data
        if dui.added:
            if isinstance(dui.added, Instance):
                for iv in self:
                    if iv.labels_mapping(dui.added.track_id) is not None:
                        iv.add(dui.added)
            elif isinstance(dui.added, TrackedObject):
                t_id = dui.added.track_id
                for iv in self:
                    if iv.name == dui.added.object_class:
                        iv.add(dui.added)

                # Update tracked_object
                for iv in self:
                    if iv.name != dui.added.object_class:
                        lm = iv.labels_mapping()
                        for idx in range(len(lm)):
                            if lm[idx][1] >= t_id:
                                break
                        iv._update(label_keep=lm[idx - 1],
                                   update_track_id=1)
            else:
                raise ValueError(f"Do not support data {dui.added}")
            # TODO: Handle repairing all other track_id

        elif dui.deleted:
            for iv in self:
                lbl = iv.labels_mapping(dui.deleted[0])
                if lbl is not None:
                    iv.delete(lbl, dui.deleted[1])

            # Update tracked_object
            for iv in self:
                # CONT: Deleting problem. Solve it. Also, regarding the plus 1 and minus 1 things...
                if iv.name != dui.deleted.object_class:
                    lm = iv.labels_mapping()
                    for idx in range(len(lm)):
                        if lm[idx][1] >= t_id:
                            break
                    iv._update(label_keep=lm[idx - 1],
                                update_track_id=-1)

        elif dui.replaced:
            pass
        elif dui.moved:
            old_pos, obj = dui.moved
            for iv in self:
                lbl = iv.labels_mapping(old_pos[0])
                if lbl is not None:
                    iv.delete(lbl, old_pos[1])
            for iv in self:
                if iv.name == obj.object_class:
                    iv.add(obj)

    @property
    def frame_ids(self):
        frame_ids = set()
        for image_viewer in self:
            frame_ids |= set(image_viewer.frame_ids)

        return list(frame_ids)

    def _get_frames_sl(self, packet: SignalPacket):
        pass

    @property
    def images_viewers(self):
        return list(self.view._images_viewers.values())
        

if __name__ == '__main__':
    sys.path.append(str(_dir.parent.parent / "tests" / "utils"))
    # for some reasons, below does not work although we put the path
    # from tests.utils import DummyAnnotationsFactory
    from annotations.simple_annotations import DummyAnnotationsFactory
    from time import sleep

    app = qtw.QApplication(sys.argv)
    sa = DummyAnnotationsFactory.get_annotations("simple_anno")
    dh = DataHandler(input_str=sa.data_str)

    sv = SessionVisualizer()
    buff = Buffer("/home/hilman_dayo/Documents/youtube_videos/to_seki_with_takumi/IMG_1973.MOV",
                  target_width=640)
    buff.start()
    buff.play()
    sleep(1)

    sv.init_data(dh.instances, buff)
    for iv in sv.images_viewers:
        iv.request_data.connect(dh.instance_requested_sl)
        dh.send_instance.connect(iv.instance_received_sl)

        iv.data_updated.connect(dh.data_center_sl)
        dh.added_instance(dh.data_center_sl)

    sv.show()

    sys.exit(app.exec_())
