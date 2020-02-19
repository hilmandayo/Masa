from pathlib import Path
from typing import Union
import time

from PySide2 import QtCore as qtc
import cv2
import numpy as np
# from .algorithm import EpipolarTrack


class Buffer(qtc.QThread):
    """A buffer of images thread.

    This buffer act as the main engine for the video player.

    Signal:
    `run_result`:
    """

    run_result = qtc.Signal([tuple], [int])
    video_ended = qtc.Signal(int)
    backwarded = qtc.Signal(bool)
    buffer_rect = qtc.Signal(tuple)

    def __init__(self, video: Union[Path, str], parent=None, width=None, height=None,
                 backward=False, session=None, fps=60, **kwargs):
        super().__init__(parent=parent, **kwargs)

        self.play = False
        self.video = cv2.VideoCapture(video)
        self.n_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.idx = None
        self.prev_idx = -1
        self.prev_idx = None
        self.width = width
        self.height = height
        # self.session = EpipolarTrack()
        self.backward = backward
        self.run_thread = True
        self.fps = fps

    def play_pause_toggle(self):
        if self.play:
            self.pause()
        else:
            self.play()

    def play(self):
        self.play = True

    def pause(self):
        self.play = False

    def stop(self, video_ended=False):
        self.play = False

        if video_ended:
            self.video_ended.emit(self.idx)

    def get_frame(self, idx):
        self.idx = idx
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.idx)

        return self.next_frame()

    def set_backward(self, backward: bool):
        """Set the buffer to backward or not.

        Nothing will happen if the state is the same as before.
        """
        if self.backward != backward:
            prev_play_status = self.play
            self.play = False
            if backward:
                self.backward = True
            else:
                self.backward = False

            self.session = EpipolarTrack(backward=self.backward)
            # Cont from here...
            # How to make more robust backward (tochuu and from start...)
            self.idx = None
            self.play = prev_play_status
            self.backwarded.emit()

    def next_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return

        if self.width and self.height:
            frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        return frame

    def update_index(self):
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
            while self.play:
                # Keeping with our index keeping ##############################
                self.update_index()

                # Handling videos flow ########################################
                if self.prev_idx == self.idx:
                    # We at the end of video
                    self.stop(video_ended=True)
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

                # EpipolarTrack ###################################################
                # ret = self.session.run(self.frame, self.idx)
                # if ret:
                #     x1, y1, x2, y2 = ret
                # else:
                #     x1, y1, x2, y2 = None, None, None, None
                # self.run_result[tuple].emit(
                #     (self.frame, self.idx, x1, y1, x2, y2)
                # )
                # self.run_result[int].emit(self.idx)

                time.sleep(1 / fps) # fps
            time.sleep(0.1)

    def stop_thread(self):
        self.play = False
        self.run_thread = False
        # Give time for the `run` to completely stop
        time.sleep(0.1)

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
