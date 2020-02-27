from PySide2 import QtWidgets as qtw

try:
    from ..views.video_player_view import VideoPlayerView
    from Masa.models import Buffer
    from Masa.core.utils import resize_calculator
except ValueError:
    import sys
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent / "views"))
    from video_player_view import VideoPlayerView


class VideoPlayer(qtw.QWidget):
    def __init__(self, video, parent=None,
                 width=None, height=None, ratio=True, fps=30):
        super().__init__(parent=parent)

        self.buffer = Buffer(video, target_width=width, target_height=height, ratio=ratio, fps=fps)
        self.buffer.start()

        self.layout_grid_main = qtw.QGridLayout()
        self.view = VideoPlayerView(width=self.buffer.width, height=self.buffer.height)
        self.layout_grid_main.addWidget(self.view, 0, 0)
        self.setLayout(self.layout_grid_main)

        self.view.slider.setMaximum(self.buffer.n_frames - 1) # 0-indexed
        self.view.slider.sliderMoved.connect(self.buffer.get_frame)  # TODO: Pause automatically

        self.view.play_pause.connect(self.buffer.play_pause_toggle)
        # self.buff.video_ended.connect(viewer.toggle_btn)
        # # pass the frame and rect to viewer
        self.buffer.run_result.connect(self.view.set_data)
