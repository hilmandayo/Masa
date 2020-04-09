from typing import List, Dict
from PySide2 import QtWidgets as qtw, QtCore as qtc
try:
    from Masa.core.data import Instance
except (ModuleNotFoundError, ImportError):
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    import sys
    sys.path.append(str(_dir.parent.parent.parent))
from Masa.core.data import Instance
from Masa.core.utils import SignalPacket


class EditorDialogFactory(qtc.QObject):
    changed_tags = qtc.Signal(SignalPacket)
    def __init__(self):
        super().__init__()
        self.max_n_tobjs = None

    def set_max_n_tobjs_sl(self, packet: SignalPacket):
        self.max_n_tobjs = packet.data

    def set_tags_sl(self, packet: SignalPacket):
        self.tags: Dict[str, dict] = packet.data

    def get(self, dialog: str, instance):
        if dialog.lower() == "instance editor":
            ied = InstanceEditorDialog(instance, self.max_n_tobjs, self.tags)
            ied.changed_tags.connect(self._propogate_changed_tags_sl)
            return ied

    def _propogate_changed_tags_sl(self, packet: SignalPacket):
        self.changed_tags.emit(
            SignalPacket(sender=self.__class__.__name__, data=packet.data)
        )

editor_dialog_factory = EditorDialogFactory()


class InstanceEditorDialog(qtw.QDialog):
    changed_instance = qtc.Signal(SignalPacket)
    changed_tags = qtc.Signal(SignalPacket)

    def __init__(self, instance: Instance, max_n_tobjs: int,
                 tags: Dict[str, dict], parent=None):
        super().__init__(parent=parent, modal=True)
        self.instance = instance
        self.max_n_tobjs = max_n_tobjs
        self.tags = tags

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

    def _set_widgets(self):
        self.widget_pairs = {
            "track_id": (qtw.QLabel("Track ID"), qtw.QLabel(str(self.instance.track_id))),
            "instance_id": (qtw.QLabel("Instance ID"), qtw.QLabel(str(self.instance.instance_id))),
        }
        self.combo_boxes = {}
        for tag, vals in self.tags.items():
            combo_box = qtw.QComboBox(editable=True,
                                      insertPolicy=qtw.QComboBox.InsertAtBottom)
            combo_box.addItems(["Add new value...", *vals])
            combo_box.model().item(0).setEnabled(False)
            self.combo_boxes[tag] = (qtw.QLabel(tag), combo_box)

        self.btns = (qtw.QPushButton("Ok", clicked=self.accept),
                     qtw.QPushButton("Cancel", clicked=self.reject))

    def _optimize_widgets(self):
        pass

    def _set_layouts(self):
        self.setLayout(qtw.QFormLayout())

    def _init(self):
        for label, widget in self.widget_pairs.values():
            self.layout().addRow(label, widget)

        for label, widget in self.combo_boxes.values():
            self.layout().addRow(label, widget)

        self.layout().addRow(self.btns[0], self.btns[1])


    def accept(self):
        tags = {}
        for key, row in self.combo_boxes.items():
            tags[key] = row[1].currentText()
        for key, _tags in tags.items():
            if _tags not in self.tags[key]:
                self.tags.update(tags)
                self.changed_instance.emit(
                    SignalPacket(sender=self.__class__.__name__, data=self.tags)
                )

        i = self.instance
        instance = Instance(
            track_id=i.track_id,
            object_class=i.object_class,
            instance_id=i.instance_id,
            x1=i.x1,
            y1=i.y1,
            x2=i.x2,
            y2=i.y2,
            frame_id=i.frame_id,
            tags=tags
        )
        self.changed_instance.emit(
            SignalPacket(sender=self.__class__.__name__, data=instance)
        )
        super().accept()


if __name__ == "__main__":
    import sys

    # CONT: How to handle the tags???
    app = qtw.QApplication(sys.argv)
    edf = EditorDialogFactory()
    edf.max_n_tobjs = 3
    tags = {"view": "small medium big".split(), "time": "day night".split()}
    edf.tags = tags

    i_tags = {"view": "big", "time": "night"}
    instance = Instance(2, "dummy", 0, 1, 2, 1, 2, 3, i_tags)
    ad = edf.get("instance editor", instance)
    ad.show()
    sys.exit(app.exec_())
