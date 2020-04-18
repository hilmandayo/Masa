from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
import numpy as np

from .buffer_render_view import BufferRenderView
from Masa.core.utils import SignalPacket


class VideoPlayerView(qtw.QWidget):
    """The interface to a set of video player.

    This class act as a wrapper and proxy around some basic elements of what
    (ideally) a video player should has -- play-pause button, slider etc.
    """
    pass_rect_coords = qtc.Signal(tuple)
    play_pause = qtc.Signal(bool)
    # run_result = qtc.Signal(FrameData)
    run_result = qtc.Signal()
    set_slider_length = qtc.Signal()
    backwarded = qtc.Signal(bool)
    rect_changed = qtc.Signal(SignalPacket)
    req_datahandler_info = qtc.Signal(SignalPacket)

    def __init__(self, parent=None, width: int = None, height: int = None):
        super().__init__(parent)

        self.width = width
        self.height = height

        self._set_widgets()
        self._optimize_widgets()
        self._set_layouts()
        self._init()

    def _set_widgets(self):
        self.view = BufferRenderView(width=self.width, height=self.height,
                                     video_player=self)
        self.view.rect_changed.connect(lambda x: print(x))

        self.view.req_datahandler_info.connect(lambda packet: self.req_datahandler_info.emit(
            SignalPacket(sender=packet.data.append(self.__class__.__main__),
                         data=(None, None))
        ))

        self.frames_label = qtw.QLabel()
        self.backward_btn = qtw.QPushButton()
        self.slider = qtw.QSlider(qtc.Qt.Horizontal)
        self.start_pause_btn = qtw.QToolButton()

        self.req_datahandler_info.connect()

    def _optimize_widgets(self):
        self.start_pause_btn.setCheckable(True)
        self.start_pause_btn.setChecked(False)
        self.start_pause_btn.clicked.connect(self.update_btn)
        self.update_btn()

        self.backward_btn.setCheckable(True)
        self.backward_btn.setChecked(True)
        self.backward_btn.clicked.connect(self.toggle_btn)
        self.toggle_btn()

        self.view.pass_rect_coords.connect(self.pass_rect_coords)
        self.start_pause_btn.setSizePolicy(
            qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum
            )

    def _set_layouts(self):
        self.layout = qtw.QGridLayout()

    def _init(self):
        # Adding widgets... We work backwards...
        self.layout.addWidget(self.view, 0, 0, 1, 4)
        self.layout.addWidget(self.frames_label, 1, 1, 1, 1)
        self.layout.addWidget(self.backward_btn, 1, 2, 1, 1)
        self.layout.addWidget(self.slider, 2, 0, 1, 3)
        self.layout.addWidget(self.start_pause_btn, 2, 3, 1, 1)
        self.setLayout(self.layout)

    def _on_rect_change(self, track_id, instance_id, x1, y1, x2, y2):
        print("emit")

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

    def receive_tracked_objects(self, tobjs: SignalPacket):
        pass

    def set_data(self, f_data):
        """Set data based on data withing `f_data` for current frame.

        This function will do some needed pre-process to the f_info
        before:
        1. Push it to the `BufferRenderView` by calling `BufferRenderView.set_data`.
        2. Emit the data by emitting signal `run_result` (basically, this
        expose result by buffer.).
        """
        frame, idx = f_data.frame, f_data.frame_id
        rect = []
        to_int = ["x1", "y1", "x2", "y2"]
        height, width = frame.shape[:2]
        for d in f_data.data:
            for key in to_int:
                attr = getattr(d, key)
                if isinstance(attr, float):
                    if "x" in key:
                        setattr(d, key, int(attr * width))
                    else:
                        setattr(d, key, int(attr * height))

        self.view.set_data(f_data)
        self.run_result.emit(f_data)

if __name__ == "__main__":
    import sys
    sys.path.append("../../tests/utils")

    app = qtw.QApplication(sys.argv)
    view = VideoPlayerView()

    view.set_data(np.zeros([300, 300, 3], np.uint8))

    view.show()

    sys.exit(app.exec_())
