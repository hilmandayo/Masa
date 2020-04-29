from collections import defaultdict
from typing import List, Tuple, Union
from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

import numpy as np

from Masa.core.data import Instance, TrackedObject
from Masa.models import Buffer
# TODO: Make `SessionsVisualizerView` or `SessionVisualizerView`?
from ..views.sessions_visualizer_view import SessionsVisualizerView
from ..views.images_viewer_view import ImagesViewerView
from ..dialog.instance_editor_dialog import InstanceEditorDialog

from Masa.models import DataHandler
from Masa.core.utils import SignalPacket, DataUpdateInfo


class SessionVisualizer(qtw.QWidget):
    req_frames = qtc.Signal(SignalPacket)
    req_datainfo = qtc.Signal(SignalPacket)
    prop_data_change = qtc.Signal(SignalPacket)
    jump_to_frame = qtc.Signal(SignalPacket)

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
        

    def init_data(self, data_handler: DataHandler):
        # Signal must be connected for image acquisitions.
        tobjs = data_handler[:]
        obj_cls_tobjs = defaultdict(list)

        for tobj in tobjs:
            obj_cls_tobjs[tobj.object_class].append(tobj)

        for oc in data_handler.object_classes:
            imv = ImagesViewerView(name=oc)
            imv.req_instance.connect(self.request_data_sl)
            imv.req_frames.connect(self.request_frames_sl)
            imv.jump_to_frame.connect(self._jump_to_frame_sl)
            self.view._add_images_viewer(oc, imv)

        for name, images_viewer in self.view._images_viewers.items():
            images_viewer.init_data(obj_cls_tobjs[name])

        self.req_frames.emit(
            SignalPacket(sender=[self.__class__.__name__], data=self.frame_ids)
        )

    def _jump_to_frame_sl(self, packet: SignalPacket):
        self.jump_to_frame.emit(
            SignalPacket(sender=[*packet.sender, self.__class__.__name__],
                         data=packet.data)
        )

    def request_frames_sl(self, packet: SignalPacket):
        self.req_frames.emit(
            SignalPacket(sender=[*packet.sender, self.__class__.__name__],
                         data=packet.data)
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
            SignalPacket(sender=[self.__class__.__name__], data=pos)
        )

    @property
    def tags(self):
        tags = defaultdict(set)
        for iv in self.view._images_viewers.values():
            for tag_key, tag_value in iv.tags.items():
                tags[tag_key] = tags[tag_key].union(tag_value)

        return {k: list(v) for k, v in tags.items()}

    def receive_datainfo_sl(self, packet: SignalPacket):
        if self.__class__.__name__ in packet.sender:
            di = packet.data
            if di.tobj is not None:
                raise ValueError(f"Support for `TrackedObject` is not implemented yet.")

            ied = InstanceEditorDialog(di.instance, di.obj_classes, di.tags)
            ied.prop_data_change.connect(self._propogate_data_change_sl)
            ied.exec_()

    def _propogate_data_change_sl(self, packet: SignalPacket):
        self.prop_data_change.emit(
            SignalPacket(sender=[*packet.sender, self.__class__.__name__],
                         data=packet.data)
        )

    def data_update_sl(self, packet: SignalPacket):
        dui: DataUpdateInfo = packet.data
        if dui.added:
            self._add(dui.added)
        elif dui.deleted:
            self._delete(*dui.deleted)
        elif dui.replaced:
            if not isinstance(dui.replaced, Instance):
                return ValueError(f"Only support replacing an Instance.")
            self._add(dui.replaced)
            self._delete(dui.replaced.track_id, dui.replaced.instance_id + 1,
                         update_others=False)
        elif dui.moved:
            self._delete(*dui.moved[0])
            self._add(dui.moved[1])

    def _replace(self, new_instance):
        for iv in self:
            lbl = iv.labels_mapping(new_instance.track_id)
            if lbl is not None:
                # iv.replace()
                iv._delete_col(
                    new_instance.track_id, new_instance.instance_id, update=False
                )
                iv._add(new_instance)

    def _delete(self, t_id, ins_id, update_others=True):
        for iv in self:
            lbl = iv.labels_mapping(t_id)
            if lbl is not None:
                # print("before:", iv.labels_mapping())
                deleted = iv.delete(lbl, ins_id) # CONT: solve weather deleted row or not
                object_class = iv.name
                # print("after:", iv.labels_mapping())

        # Update tracked_object
        if update_others and deleted == "deleted_row":
            for iv in self:
                if iv.name != object_class:
                    lm = iv.labels_mapping()
                    del_lbl = None
                    for nlbl, nt_id in lm:
                        if nt_id >= t_id:
                            del_lbl = nlbl
                            break
                    if del_lbl is not None:
                        iv._update(label_keep=del_lbl - 1,
                                    mode=-1)

    def _add(self, obj: Union[TrackedObject, Instance]):
        if isinstance(obj, Instance):
            for iv in self:
                out = iv.labels_mapping(obj.track_id)
                # print(iv.name, obj.track_id, out)
                if out is not None:
                    iv.add(obj)
        elif isinstance(obj, TrackedObject):
            t_id = obj.track_id
            for iv in self:
                if iv.name == obj.object_class:
                    iv.add(obj)

            # Update tracked_object
            for iv in self:
                if iv.name != obj.object_class:
                    lm = iv.labels_mapping()
                    # Assuming `lm` is 0,1,..n
                    add_lbl = None
                    for lbl, t_id in lm:
                        if t_id >= obj.track_id:
                            add_lbl = lbl
                            break
                    if add_lbl is not None:
                        iv._update(label_keep=add_lbl - 1,
                                mode=1)
        else:
            raise ValueError(f"Do not support data {obj}")
        

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
