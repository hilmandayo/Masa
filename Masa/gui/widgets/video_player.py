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

        # Our main components.
        self.dh = data_handler
        self.buff = Buffer(video, target_width=width, target_height=height, ratio=ratio, fps=fps)
        self.buff.start()

        # Setting up layout.
        self.layout_grid_main = qtw.QGridLayout()
        self.view = VideoPlayerView(width=self.buff.width, height=self.buff.height,
                                    frame_max=self.buff.n_frames - 1,
                                    fps=self.buff.fps
        )
        self.layout_grid_main.addWidget(self.view, 0, 0)
        self.setLayout(self.layout_grid_main)


        # Request, receive and update continues phase of data between
        # `DataHandler` and the `VideoPlayer`
        self.view.req_datahandler_info.connect(self.dh.get_datainfo_sl)
        self.dh.pass_datainfo.connect(self.view.receive_datainfo_sl)
        self.view.prop_data_change.connect(self.dh.data_update_sl)
        self.view.rect_changed.connect(self.dh.data_update_sl)

        # Setting up slider and button.
        self.view.slider.setMaximum(self.buff.n_frames - 1) # 0-indexed
        self.view.slider.sliderMoved.connect(self.buff.get_frame)  # TODO: Pause automatically
        self.view.play_pause.connect(self.buff.play_pause_toggle)

        # fps information
        self.buff.fps_changed.connect(self.view.set_fps_sl)

        # Getting all new info from our `Buffer` engine.
        self.buff.curr_frame.connect(self.curr_frame_sl)

        # Getting info from `DataHandler` based on `Buffer` engine.
        self.dh.curr_frame_data.connect(self.view.view.set_frame_data_sl)

    def curr_frame_sl(self, packet):
        self.dh.propogate_curr_frame_data_sl(packet)
        self.view.slider.setValue(packet.data[1])

    def jump_frame_sl(self, packet):
        self.jump_frame(packet.data)

    def jump_frame(self, frame_id):
        self.buff.get_frame(frame_id, straight_jump=True)

    def pause(self):
        if self.view.start_pause_btn.isChecked():
            self.view.start_pause_btn.click()

    def forward_one(self):
        self.pause()
        self.buff.get_frame(self.buff.idx + 1, straight_jump=True)

    def backward_one(self):
        self.pause()
        self.buff.get_frame(self.buff.idx - 1, straight_jump=True)
