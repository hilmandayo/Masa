from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
try:
    from .buffer_render_view import BufferRenderView
except (ImportError, ModuleNotFoundError):
    from buffer_render_view import BufferRenderView
import numpy as np


class VideoPlayerView(qtw.QWidget):
    """The interface where everything connected together."""

    pass_rect_coords = qtc.Signal(tuple)
    play_pause = qtc.Signal(bool)
    run_result = qtc.Signal(tuple)
    set_slider_length = qtc.Signal()
    backwarded = qtc.Signal(bool)

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent)

        self.width = width
        self.height = height

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

        self.show()

    def _set_widgets(self):
        self.video_view = BufferRenderView(width=self.width, height=self.height)
        self.frames_label = qtw.QLabel()
        self.backward_btn = qtw.QPushButton()
        self.slider = qtw.QSlider(qtc.Qt.Horizontal)
        self.start_pause_btn = qtw.QToolButton()

    def _optimize_widgets(self):
        self.start_pause_btn.setCheckable(True)
        self.start_pause_btn.setChecked(False)
        self.start_pause_btn.clicked.connect(self.update_btn)
        self.update_btn()

        self.backward_btn.setCheckable(True)
        self.backward_btn.setChecked(True)
        self.backward_btn.clicked.connect(self.toggle_btn)
        self.toggle_btn()

        self.video_view.pass_rect_coords.connect(self.pass_rect_coords)
        self.start_pause_btn.setSizePolicy(
            qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum
            )

    def _set_layouts(self):
        self.layout = qtw.QGridLayout()

    def _init(self):
        # Adding widgets... We work backwards...
        self.layout.addWidget(self.video_view, 0, 0, 1, 4)
        self.layout.addWidget(self.frames_label, 1, 1, 1, 1)
        self.layout.addWidget(self.backward_btn, 1, 2, 1, 1)
        self.layout.addWidget(self.slider, 2, 0, 1, 3)
        self.layout.addWidget(self.start_pause_btn, 2, 3, 1, 1)
        self.setLayout(self.layout)

    def update_btn(self):
        is_play = self.start_pause_btn.isChecked()

        if is_play:
            icon = qtw.QStyle.SP_MediaPause
        else:
            icon = qtw.QStyle.SP_MediaPlay

        icon = qtg.QIcon(self.style().standardIcon(icon))
        self.start_pause_btn.setIcon(icon)

        self.play_pause.emit(is_play)

    def toggle_btn(self):
        # TODO: Any better way???
        backward = self.backward_btn.isChecked()

        if backward:
            text = "Backward Mode"
        else:
            text = "Forward Mode"

        self.backward_btn.setText(text)
        self.backwarded.emit(backward)

    def set_data(self, f_info):
        f = f_info
        frame, idx, x1, y1, x2, y2 = f_info.frame, f.frame_id, f.x1, f.y1, f.x2, f.y2
        rect = None
        if isinstance(x1, float):
            height, width = frame.shape[:2]
            x1, y1 =int(x1 * width), int(y1 * height)
            x2, y2 =int(x2 * width), int(y2 * height)
            # f = frame[y1:y2 + 1, x1:x2 + 1]
        self.run_result.emit((idx, frame, x1, y1, x2, y2))
        rect = (x1, y1, x2, y2)
        self.video_view.set_frame(frame, rect=rect)

if __name__ == "__main__":
    import sys
    sys.path.append("../../tests/utils")

    app = qtw.QApplication(sys.argv)
    view = VideoPlayerView()

    view.set_frame(np.zeros([300, 300, 3], np.uint8), 1)

    view.show()

    sys.exit(app.exec_())
