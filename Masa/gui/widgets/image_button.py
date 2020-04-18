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

class QPushImageButton(qtw.QPushButton):
    right_clicked = qtc.Signal()
    left_clicked = qtc.Signal()
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.RightButton:
            self.right_clicked.emit()
        elif event.button() == qtc.Qt.LeftButton:
            self.left_clicked.emit()


class ImageButton(qtw.QWidget):
    i_id_template = "<b>Instance ID<\b>: {}"
    left_clicked = qtc.Signal(SignalPacket)
    right_clicked = qtc.Signal(SignalPacket)
    def __init__(self,
                 track_id, instance_id, frame_id,
                 x1, y1, x2, y2, meta,
                 parent=None,
                 image: np.ndarray = None,
                 width=320, height=320):
        super().__init__(parent=parent)
        self.track_id = track_id
        self.frame_id = frame_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.meta = meta

        image_btn = QPushImageButton()
        info_label = qtw.QLabel()
        image_btn.left_clicked.connect(self._left_clicked)
        image_btn.right_clicked.connect(self._right_clicked)

        self.setLayout(qtw.QBoxLayout(qtw.QBoxLayout.TopToBottom))
        self.layout().setSpacing(1)
        self.layout().addWidget(image_btn)
        self.layout().addWidget(info_label)

        if image is None:
            image = np.zeros([height, width, 3], dtype=np.uint8)
        self.set_np(image)
        self.set_instance_id(instance_id)

    def _left_clicked(self):
        self.left_clicked.emit(
            SignalPacket(sender=self.__class__.__name__,
                         data=self.frame_id)
        )

    def _right_clicked(self):
        self.right_clicked.emit(
            SignalPacket(sender=self.__class__.__name__,
                         data=(self.track_id, self.instance_id))
        )

    def sizeHint(self):
        ib_size = self.layout().itemAt(0).widget().size()
        il_size = self.layout().itemAt(1).widget().size()

        height = ib_size.height() + il_size.height()
        return qtc.QSize(max(ib_size.width(), il_size.width()), height)

    def set_np(self, image: np.ndarray):
        image_btn = self.layout().itemAt(0).widget()
        height, width = image.shape[:2]
        # XXX: Weird, sometimes, even if `input_bgr` is False, it is still
        #      output OK.
        image = convert_np(image, to="qpixmap")
        frame_icon = qtg.QIcon(image)
        image_btn.setIcon(frame_icon)

        image_btn.setIconSize(qtc.QSize(width, height))
        image_btn.setFixedSize(width, height)

    def set_instance_id(self, instance_id):
        self.instance_id = instance_id
        info_label = self.layout().itemAt(1).widget()
        info_label.setText(self.i_id_template.format(str(self.instance_id)))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    img_btn = ImageButton(np.zeros([250, 250, 3], np.uint8))
    img_btn.show()

    sys.exit(app.exec_())
