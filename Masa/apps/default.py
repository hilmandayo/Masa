from PySide2 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
from Masa.gui.widgets.video_player import VideoPlayer
from Masa.gui.widgets.session_visualizer import SessionVisualizer
from Masa.models.datahandler import DataHandler

class ImageExtractorApp(qtw.QMainWindow):
    def __init__(self, root_dataid, parent=None):
        super().__init__()

        video_path = list((root_dataid / "data").glob("*.mp4"))
        if len(video_path) == 0:
            video_path = list((root_dataid / "data").glob("*.MOV"))
        if len(video_path) > 1:
            raise ValueError("Do not support multiple videos")
        video_path = str(video_path[0])

        dh_path = (root_dataid / "annotations" / "annotations.csv")
        data_handler = DataHandler(dh_path)

        self.video_player = VideoPlayer(video_path, data_handler, width=640)
        self.setCentralWidget(self.video_player)

        self.session_vis = SessionVisualizer()
        dock = qtw.QDockWidget("Show")
        dock.setWidget(self.session_vis)
        dock.setFeatures(
            qtw.QDockWidget.DockWidgetMovable |
            qtw.QDockWidget.DockWidgetFloatable
        )
        dock.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)

        self.addDockWidget(qtc.Qt.RightDockWidgetArea, dock)

        self.session_vis.req_frames.connect(self.video_player.buff.get_frames_sl)
        self.video_player.buff.pass_frames.connect(self.session_vis.set_frames_sl)

        self.session_vis.req_datainfo.connect(data_handler.get_datainfo_sl)
        data_handler.pass_datainfo.connect(self.session_vis.receive_datainfo_sl)

        self.session_vis.prop_data_change.connect(data_handler.data_update_sl)
        data_handler.data_updated.connect(self.session_vis.data_update_sl)

        self.session_vis.jump_to_frame.connect(self.video_player.jump_frame_sl)

        self.session_vis.init_data(data_handler)

        self.debugger = qtw.QTextEdit(readOnly=True)
        data_handler.print_data.connect(self._update_data)
        self.set_shortcuts()

    def set_shortcuts(self):
        factor = 4
        fforward = qtw.QAction("Fast Forward", self)
        fforward.setShortcut(qtg.QKeySequence("f"))
        # XXX: Why below do not works? Because of shortcut? Because of bugs?
        # fforward.triggered.connect(lambda _, f=factor: self.video_player.buff.increase_fps(f))

        # XXX: This will not be garbage collected because of reference to self???
        fforward.triggered.connect(lambda: self.video_player.buff.increase_fps(factor))

        sdown = qtw.QAction("Slow Down", self)
        sdown.setShortcut(qtg.QKeySequence("d"))
        sdown.triggered.connect(lambda: self.video_player.buff.decrease_fps(factor))

        reset = qtw.QAction("Reset", self)
        reset.setShortcut(qtg.QKeySequence("r"))
        reset.triggered.connect(self.video_player.buff.reset_fps)

        pause_play = qtw.QAction("Pause/Play", self)
        pause_play.setShortcut(qtg.QKeySequence(qtg.Qt.Key_Space))
        pause_play.triggered.connect(self.video_player.view.start_pause_btn.click)

        forw1f = qtw.QAction("Forward 1 Frame", self)
        forw1f.setShortcut(qtg.QKeySequence("x"))
        forw1f.triggered.connect(self.video_player.forward_one)

        back1f = qtw.QAction("Forward 1 Frame", self)
        back1f.setShortcut(qtg.QKeySequence("z"))
        back1f.triggered.connect(self.video_player.backward_one)

        menubar = self.menuBar()
        vid_menu = menubar.addMenu("Video")
        vid_menu.addAction(pause_play)
        vid_menu.addAction(fforward)
        vid_menu.addAction(sdown)
        vid_menu.addAction(reset)
        vid_menu.addAction(forw1f)
        vid_menu.addAction(back1f)

    def _update_data(self, packet):
        self.debugger.setText(packet.data)

    def show(self):
        super().show()
        self.debugger.show()

