"""Collections of mock video data for testing."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Union, Optional

import numpy as np


class DummyBufferFactory:
    """A factory that returns certain mock video data."""
    @staticmethod
    def get_buffer(name):
        if name == "simple_video":
            return SimpleVideo()
        elif name == "simple_white_video":
            return SimpleWhiteVideo()
        if name == "simple_black_video":
            return SimpleBlackVideo()
        if name == "simple_tagged_video":
            return SimpleTaggedVideo()


@dataclass
class DummyBuffer:
    pass

@dataclass
class SimpleVideo(DummyBuffer):
    length: int = 30
    buff_idx: int = 0
    width: int = 640
    height: int = 320
    buffer: np.ndarray = field(init=False)

    def __post_init__(self):
        # Temporary... Do not know how to solve the `buffer` init problem when
        # this class is being inherited.
        self.buffer = np.random.randint(
            0, 255, size=[self.length, self.height, self.width, 3]
        )


    @property
    def read_all(self):
        return self.buffer

    def create_dummy_data(self, empty_data_dir, file_name="video.mp4"):
        data_file = empty_annotations_dir / file_name
        if data_file.exists():
            return data_file

        data_file.write_bytes(b"")
        return data_file

    def read(self):
        ret_frame = self.buff_idx[self.buff_idx]
        self.buff_idx += 1

        return ret_frame.copy()

    def reset(self):
        self.buff_idx = 0


@dataclass
class SimpleWhiteVideo(SimpleVideo):
    def __post_init__(self):
        # Temporary... Do not know how to solve the `buffer` init problem when
        # this class is being inherited.
        self.buffer = np.full(
            shape=[self.length, self.height, self.width, 3], fill_value=255
        )

@dataclass
class SimpleBlackVideo(SimpleVideo):
    def __post_init__(self):
        # Temporary... Do not know how to solve the `buffer` init problem when
        # this class is being inherited.
        self.buffer = np.full(
            shape=[self.length, self.height, self.width, 3], fill_value=0
        )

@dataclass
class SimpleTaggedVideo(SimpleVideo):
    _blue = 0
    _green = 1
    _red = 2
    rgb: bool = False

    def __post_init__(self):
        self.buffer = np.full(
            shape=[self.length, self.height, self.width, 3], fill_value=0
        )
        if self.rgb:
            color_tag = [self._red, self._green, self._blue]
        else:
            color_tag = [self._blue, self._green, self._red]

        self.buffer[:, 0, 0, :] = color_tag
        self.buffer[:, 0, 1, :] = [[i for _ in range(3)] for i in range(self.length)]

    @property
    def BLUE(self):
        return self._blue

    @property
    def GREEN(self):
        return self._green

    @property
    def RED(self):
        return self._red


if __name__ == "__main__":
    buff = DummyBufferFactory.get_buffer("simple_video")
