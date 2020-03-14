from PySide2 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc
import numpy as np

# For local testing.
try:
    from Masa.core.utils import convert_np
except ModuleNotFoundError:
    import sys;
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent / "core" / "utils"))
    from utils import convert_np

class ImageButton(qtw.QPushButton):
    def __init__(self, parent=None,
                 image: np.ndarray = None,
                 width=320, height=320):
        super().__init__(parent=parent)
        if image is None:
            image = np.zeros([height, width, 3], dtype=np.uint8)
        self.set_np(image)
        self.setIconSize(qtc.QSize(width, height))
        self.setFixedSize(width, height)

    def set_np(self, image: np.ndarray):
        image = convert_np(image, to="qpixmap")
        frame_icon = qtg.QIcon()
        frame_icon.addPixmap(image)
        self.setIcon(frame_icon)
        return self


        


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    img_btn = ImageButton(np.zeros([250, 250, 3], np.uint8))
    img_btn.show()

    sys.exit(app.exec_())
