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
    def get_buffer(name, *args, **kwargs):
        if name == "ocv_simple_tagged":
            return OCVSimpleTaggedVideo(*args, **kwargs)


@dataclass
class DummyBuffer(ABC):
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
        if flag == cv2.cv2.CAP_PROP_POS_FRAMES:
            self.buff_idx = value


@dataclass
class OCVSimpleTaggedVideo(OpenCVVideoCapture):
    BLUE: int = field(init=False, default=0)
    GREEN: int = field(init=False, default=1)
    RED: int = field(init=False, default=2)

    def _read(self):
        buff = np.random.randint(
            0, 255, size=[self.height, self.width, 3]
        )
        buff[0, 0, :] = self.buff_idx
        buff[0, 1, :] = (self.BLUE, self.GREEN, self.RED)

        return buff

    # @staticmethod
    # def BLUE():
    #     return 0

    # @staticmethod
    # def GREEN():
    #     return 1

    # @staticmethod
    # def RED():
    #     return 2


if __name__ == "__main__":
    buff = DummyBufferFactory.get_buffer("simple_video")
