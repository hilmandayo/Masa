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
    def __init__(self, video, data_handler, parent=None,
                 width=None, height=None, ratio=True, fps=30):
        super().__init__(parent=parent)

        self.dh = data_handler
        self.buff = Buffer(video, target_width=width, target_height=height, ratio=ratio, fps=fps)
        self.buff.start()

        self.layout_grid_main = qtw.QGridLayout()
        self.view = VideoPlayerView(width=self.buff.width, height=self.buff.height)

        # CONT: From here
        self.view.req_datahandler_info.connect(self.dh.get_datainfo_sl)

        self.layout_grid_main.addWidget(self.view, 0, 0)
        self.setLayout(self.layout_grid_main)

        self.view.slider.setMaximum(self.buff.n_frames - 1) # 0-indexed
        self.view.slider.sliderMoved.connect(self.buff.get_frame)  # TODO: Pause automatically
        self.view.play_pause.connect(self.buff.play_pause_toggle)

        self.buff.curr_frame.connect(self.dh.propogate_curr_frame_data_sl)
        self.dh.curr_frame_data.connect(self.view.view.set_frame_data_sl)

    def jump_frame_sl(self, packet):
        self.jump_frame(packet.data)

    def jump_frame(self, frame_id):
        self.buff.get_frame(frame_id, straight_jump=True)
