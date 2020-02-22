from PySide2 import QtWidgets as qtw

from Masa.gui.gui import VideoPlayerView
from Masa.models import Buffer
from Masa.core.utils import resize_calculator


class VideoPlayer(qtw.QWidget):
    def __init__(self, video, parent=None,
                 width=None, height=None, ratio=True, fps=30):
        super().__init__(parent=parent)

        self.buffer = Buffer(video, target_width=width, target_height=height, ratio=ratio, fps=fps)
        self.buffer.start()
        self.view = VideoPlayerView(width=self.buffer.width, height=self.buffer.height)

        self.view.slider.setMaximum(self.buffer.n_frames - 1)
        self.view.slider.sliderMoved.connect(self.buffer.get_frame)  # TODO: Pause is automatically

        self.view.play_pause.connect(self.buffer.play_pause_toggle)
        # self.buff.video_ended.connect(viewer.toggle_btn)
        # # pass the frame and rect to viewer
        self.buffer.run_result.connect(self.view.set_data)
