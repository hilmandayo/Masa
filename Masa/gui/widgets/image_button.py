from PySide2 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc
import numpy as np

# For local testing.
try:
    from Masa.core.utils import convert_np, SignalPacket
    # from Masa.gui.dialog import editor_dialog_factory
except ModuleNotFoundError:
    import sys;
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent / "core" / "utils"))
    from utils import convert_np
    # sys.path.append(str(_dir.parent / "dialog" / "instance_editor_dialog"))
    # from instance_editor_dialog import editor_dialog_factory

class ImageButton(qtw.QPushButton):
    image_clicked = qtc.Signal(SignalPacket)
    def __init__(self,
                 track_id, instance_id, frame_id,
                 x1, y1, x2, y2, meta,
                 parent=None,
                 image: np.ndarray = None,
                 width=320, height=320):
        super().__init__(parent=parent)
        self.track_id = track_id
        self.frame_id = frame_id
        self.instance_id = instance_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.meta = meta
        if image is None:
            image = np.zeros([height, width, 3], dtype=np.uint8)
        self.set_np(image)
        self.setIconSize(qtc.QSize(width, height))
        self.setFixedSize(width, height)

        self.clicked.connect(self._image_clicked)

        # TODO: How to connect through _svv directly?
    def _image_clicked(self):
        self.image_clicked.emit(
            SignalPacket(sender=self.__class__.__name__,
                         data=(self.track_id, self.instance_id))
        )
        

    def set_np(self, image: np.ndarray):
        image = convert_np(image, to="qpixmap")
        frame_icon = qtg.QIcon()
        frame_icon.addPixmap(image)
        self.setIcon(frame_icon)
        


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    img_btn = ImageButton(np.zeros([250, 250, 3], np.uint8))
    img_btn.show()

    sys.exit(app.exec_())
