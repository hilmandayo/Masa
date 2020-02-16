from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
import sys
import numpy as np
import cv2


class ImagesViewer(qtw.QWidget):
    jump_to_frame = qtc.Signal(int)

    def __init__(self, parent=None, window_title: str = "Images Viewer"):
        super().__init__(parent)
        self.window_title = window_title

        self.set_window_attributes()
        self.set_widgets()
        self.optimize_widgets()
        self.set_layouts()
        self.init()

    def set_window_attributes(self):
        self.setWindowTitle(self.window_title)
        self.setFeatures(
            qtw.QDockWidget.DockWidgetMovable |
            qtw.QDockWidget.DockWidgetFloatable
        )

        # XXX: Not good
        self.setSizePolicy(
            qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum
            )

    def set_widgets(self):
        self.scroll_area = qtw.QScrollArea()
        self.form_widget = qtw.QWidget()

    def set_layouts(self):
        self.form_layout = qtw.QFormLayout()

    def init(self):
        # put layout in each widget
        self.form_widget.setLayout(self.form_layout)
        self.scroll_area.setWidget(self.form_widget)

        # 'connect' each widget
        self.scroll_area.setWidgetResizable(True)
        self.setWidget(self.scroll_area)

    def optimize_widgets(self):
        self.scroll_area.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAsNeeded)


    def np_to_pixmap(self, frame: np.ndarray, scale=True):
        # TODO: make this as utility
        # https://stackoverflow.com/questions/34232632/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image
        frame = np.require(frame, np.uint8, "C")
        height, width, channel = frame.shape
        bytes_per_line = width * 3
        frame = qtg.QImage(frame.data, width, height, bytes_per_line, qtg.QImage.Format_RGB888).rgbSwapped()
        frame = qtg.QPixmap.fromImage(frame)
        if scale:
            frame = frame.scaled(width, height)

        return frame

    def add_row(self, args):
        idx, frame, x1, y1, x2, y2 = args
        # XXX: this is designed to be the same as in the viewer
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        frame = imutils.resize(frame, width=240)

        if isinstance(frame, np.ndarray):
            height, width = frame.shape[:2]
            frame = self.np_to_pixmap(frame)
            frame_icon = qtg.QIcon()
            frame_icon.addPixmap(frame)

        label = qtw.QLabel(str(idx))
        frame_btn = qtw.QPushButton()

        frame_btn.setIcon(frame_icon)
        frame_btn.setIconSize(qtc.QSize(width, height))
        frame_btn.setFixedSize(width, height)
        frame_btn.clicked.connect(lambda: self.send_info(idx))
        self.form_layout.addRow(label, frame_btn)

    def send_info(self, idx):
        self.jump_to_frame.emit(idx)

    def reset(self):
        count = self.form_layout.rowCount()
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def sizeHint(self):
        return qtc.QSize(600, 600)


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    main = TemplateDock()

    red = np.zeros([69, 121, 3], np.uint8)
    red[:,:,2] = 1 * 255
    green = np.zeros([299, 299, 3], np.uint8)
    green[:,:,1] = 1 * 255

    for i in range(19):
        main.add_row((red, 3))
        main.add_row((green, 4))

    main.show()
    sys.exit(app.exec_())
