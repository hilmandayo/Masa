from PySide2 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc
import numpy as np

# For local testing.
try:
    from Masa.core.utils import np_to_pixmap
except ModuleNotFoundError:
    import sys
    sys.path.append("../../../")
    from Masa.core.utils import np_to_pixmap

class ImageButton(qtw.QPushButton):
    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent=parent)
        height, width = image.shape[:2]
        image = np_to_pixmap(image)
        frame_icon = qtg.QIcon()
        frame_icon.addPixmap(image)

        self.setIcon(frame_icon)
        self.setIconSize(qtc.QSize(width, height))
        self.setFixedSize(width, height)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    img_btn = ImageButton(np.zeros([250, 250, 3], np.uint8))
    img_btn.show()

    sys.exit(app.exec_())
