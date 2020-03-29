from pathlib import Path
from typing import Union, List, Tuple
import time

from PySide2 import QtCore as qtc
import cv2
import numpy as np

from Masa.core.utils import resize_calculator, SignalPacket
from Masa.core.data import Instance, TrackedObject
from .session import BBSession


from collections import namedtuple
RunResults = namedtuple("RunResults", "idx new_data")

class Buffer(qtc.QThread):
    """A buffer of images thread.

    This buffer act as the main engine for the video player.

    Signal:
    `run_results`:
    """

    run_results = qtc.Signal(SignalPacket)
    session_initialized = qtc.Signal(SignalPacket)
    video_ended = qtc.Signal(int)
    pass_frames = qtc.Signal(list)
    backwarded = qtc.Signal(bool)
    buffer_rect = qtc.Signal(tuple)
    curr_frame = qtc.Signal(SignalPacket)

    def __init__(self, video: Union[Path, str],
                 target_width=None, target_height=None, parent=None,
                 ratio=True, backward=False, fps=60, **kwargs):
        super().__init__(parent=parent, **kwargs)

        self.video = cv2.VideoCapture(video)
        if not self.video.isOpened():
            raise ValueError(f"Problem in opening file {str(video)}. "
                             "Are you sure the path is valid?")

        self._play = False
        self.n_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.idx = None
        self.prev_idx = -1
        self.prev_idx = None
        # self.session = EpipolarTrack()
        self.backward = backward
        self.run_thread = True
        self.fps = fps
        self._det_width_height(target_width, target_height, ratio)

        # temp
        from Masa.models import DataHandler
        # self.dh = DataHandler("/dayo/sompo/nikaime/all_csvs/ishida/0000000002_20170814_152603_001.csv")
        self.dh = DataHandler("/dayo/sompo/nikaime/results/intermediate_output/intemediate_output_final/0000000004_20181112_150211_001.csv")
        # self.sessions = [BBSession(self.dh)]

    def _det_width_height(self, width, height, ratio):
        """Determine the width and height of the video.

        It is manually checked (instead of using `cv2.VideoCapture.get`)
        to prevent subtle bugs.
        """
        ret, frame = self.video.read()
        if not ret:
            raise ValueError(f"Problem in opening file {str(video)}. "
                             "Are you sure the path is valid?")

        self.orig_height, self.orig_width = frame.shape[:2]
        self.width, self.height = resize_calculator(
            self.orig_width, self.orig_height, width, height, ratio=ratio
        )
        self.ratio = ratio
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def jump_idx(self, idx):
        self.pause()
        self.idx = idx
        self.play()

    def play_pause_toggle(self) -> bool:
        if self._play:
            self.pause()
        else:
            self.play()

        return self._play

    def play(self):
        self._play = True

    def pause(self):
        self._play = False

    def stop(self):
        self.pause()
        self.video_ended.emit(self.idx)


    def get_frame(self, idx):
        self.idx = idx
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.idx)

        return self.next_frame()


    def get_frames(self, idxs: List[int]) -> List[Tuple[int, np.ndarray]]:
        self._play = False
        frames = []
        for idx in idxs:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            _, frame = self.video.read()
            frames.append((idx, frame))

        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.idx)
        self._play = True
        self.pass_frames.emit(frames)


    def set_backward(self, backward: bool):
        """Set the buffer to backward or not.

        Nothing will happen if the state is the same as before.
        """
        if self.backward != backward:
            prev_play_status = self._play
            self._play = False
            if backward:
                self.backward = True
            else:
                self.backward = False

            # self.session = EpipolarTrack(backward=self.backward)
            # Cont from here...
            # How to make more robust backward (tochuu and from start...)
            self.idx = None
            self._play = prev_play_status
            self.backwarded.emit(self.backward)

    def session_init_r(self, packet: SignalPacket):
        self.pause()
        packet = packet.data
        session = packet.session
        # CONT from here
        s = self.SESSIONS[session](packet.s_data)

    def next_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return

        frame = cv2.resize(frame, (self.width,  self.height), interpolation=cv2.INTER_AREA)
        return frame

    def update_idx(self):
        """Update internal buffer index.

        Must be called in every run iteration.
        It will constrain the range of index within the range of video.
        It will also handle the index weather it will be 'moving' forward or
        backward.
        """
        if not self.backward:
            # forward case
            if self.idx is None:
                self.idx = 0
            else:
                self.prev_idx = self.idx
                self.idx += 1

            # we do not want the index to cross the limit
            if self.idx >= self.n_frames:
                self.idx -= 1

        else:
            # Same logic as above block.
            # But for backward case.
            if self.idx is None:
                self.idx = self.n_frames - 1
            else:
                self.prev_idx = self.idx
                self.idx -= 1

            # we do not want the index to cross the limit
            if self.idx < 0:
                self.idx = 0

    def run(self):
        while self.run_thread:
            while self._play:
                # Keeping with our index keeping ##############################
                self.update_idx()

                # Handling videos flow ########################################
                if self.prev_idx == self.idx:
                    # We at the end of video
                    self.stop()
                    continue

                elif self.prev_idx == self.idx - 1:
                    frame = self.next_frame()
                else:
                    # In the case of jumping buffer or going backward
                    frame = self.get_frame(self.idx)

                # TODO: Can import this
                if not isinstance(frame, np.ndarray):
                    raise Exception
                else:
                    self.frame = frame

                # for session in self.session: session()

                # fi = self.dh.from_frame(self.idx, to="frameinfo")
                # fi.frame = self.frame

                rr = RunResults(self.idx, "dummy")
                self.curr_frame.emit(
                    SignalPacket(sender="Buffer", data=(frame.copy(), self.idx))
                )

                time.sleep(1 / self.fps) # fps
            time.sleep(0.1)

    def stop_thread(self):
        # Is this a good approach??
        # I do not know. But it works!
        self._play = False
        self.run_thread = False
        # Give time for the `run` to completely stop
        time.sleep(0.2)

    def get_points(self, rect_pts):
        if rect_pts:
            x1, y1, x2, y2 = rect_pts
            x1 = int(x1 * self.width)
            x2 = int(x2 * self.width)
            y1 = int(y1 * self.height)
            y2 = int(y2 * self.height)
            template = self.session.get_frame_points(self.frame, x1, y1, x2, y2)
            # self.buffer_rect.emit(
            #     (template, self.idx)
            # )
            self.buffer_rect.emit(
                (self.idx, self.frame, x1, y1, x2, y2)
            )
