from PySide2 import QtWidgets as qtw
from Masa.gui.widgets import VideoPlayer, SessionVisualizer

class ImageExtractorApp():
    def __init__(self, data_handler, parent=None):
        super().__init__()
        self.video_player = VideoPlayer("/home/hilman_dayo/Documents/youtube_videos/to_seki_with_takumi/IMG_1973.MOV",
                          data_handler,
                          width=640)
        self.session_vis = SessionVisualizer()
        self.session_vis.req_frames.connect(self.video_player.buff.get_frames_sl)
        self.video_player.buff.pass_frames.connect(self.session_vis.set_frames_sl)

        self.session_vis.init_data(data_handler[:])


    def show(self):
        print("showed")
        self.video_player.show()
        self.session_vis.show()

