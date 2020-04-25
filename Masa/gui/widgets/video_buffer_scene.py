from PySide2 import (QtCore as qtc, QtGui as qtg, QtWidgets as qtw)

try:
    from Masa.core.utils import SignalPacket, DataUpdateInfo
except:
    import sys;

    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent / "core" / "utils"))
    from utils import SignalPacket


class VideoBufferScene(qtw.QGraphicsScene):
    rect_changed = qtc.Signal(SignalPacket)
    def __init__(self, parent=None):
        super().__init__()

    def on_rect_change(self, track_id, instance_id, x1, y1, x2, y2):
        dui = DataUpdateInfo(
            replaced=dict(track_id=track_id, instance_id=instance_id, x1=x1, y1=y1, x2=x2, y2=y2)
        )
        self.rect_changed.emit(
            SignalPacket(sender=[self.__class__.__name__],
                         data=dui)
        )
