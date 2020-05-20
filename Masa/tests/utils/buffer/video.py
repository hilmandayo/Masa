"""Collections of mock video data for testing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Union, Optional

import cv2
import numpy as np


class DummyBufferFactory:
    """A factory that returns certain mock video data."""
    @staticmethod
    def get_buffer(name, **kwargs):
        if name == "ocv_simple_tagged":
            return OCVSimpleTaggedVideo(**kwargs)


@dataclass
class DummyBuffer(ABC):
    """A class which every dummy buffer class need to inherit."""
    pass


@dataclass
class OpenCVVideoCapture(DummyBuffer):
    length: int = 30
    width: int = 640
    height: int = 320
    buff_idx: int = field(init=False, default=0)
    data_file: Optional[Path] = field(init=False, default=None)

    @property
    def read_all(self):

        _buff_idx = self.buff_idx
        self.buff_idx = 0

        retval = np.ndarray([
            self.read() for i in range(self.length)
        ])

        self.buff_idx = _buff_idx
        return retval

    def create_dummy_data(self, empty_data_dir, file_name="video.mp4"):
        self.data_file = empty_data_dir / file_name
        if self.data_file.exists():
            return self.data_file

        self.data_file.write_bytes(b"")
        return self.data_file

    @abstractmethod
    def _read(self):
        pass

    def read(self):
        if self.buff_idx >= self.length:
            frame = None
            ret = False
        else:
            frame = self._read()
            ret = True
            self.buff_idx += 1

        return ret, frame

    def isOpened(self) -> bool:
        """Mimic OpenCV's VideoCapture `isOpened`."""
        return True if self.data_file else False

    def get(self, flag: int):
        """Mimic OpenCV's VideoCapture `get`."""
        if flag == cv2.CAP_PROP_FRAME_COUNT:
            return self.length

    def set(self, flag: int, value: int):
        """Mimic OpenCV's VideoCapture `set`."""
        if flag == cv2.CAP_PROP_POS_FRAMES:
            self.buff_idx = value


@dataclass
class OCVSimpleTaggedVideo(OpenCVVideoCapture):
    # visualize: bool = False
    BLUE: int = field(init=False, default=0)
    GREEN: int = field(init=False, default=1)
    RED: int = field(init=False, default=2)

    def _read(self):
        buff = np.random.randint(
            0, 256, [self.height, self.width, 3], np.uint8
        )
        # if self.visualize:
        #     cv2.putText(
        #         buff, f"frame_id: {self.buff_idx}",
        #         (int(self.width * 0.2), int(self.height * 0.7)),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         3,
        #         (255, 255, 255))

        buff[0, 0, :] = self.buff_idx
        buff[0, 1, :] = (self.BLUE, self.GREEN, self.RED)

        return buff


if __name__ == "__main__":
    buff = DummyBufferFactory.get_buffer("simple_video")
