from dataclasses import dataclass, field
from typing import Union, Optional, Dict

import numpy as np

@dataclass
class FrameData:
    """Special class to be sent by signal"""
    # TODO: Accept support for width and what not
    x1: Union[float, int]
    y1: Union[float, int]
    x2: Union[float, int]
    y2: Union[float, int]
    object_class: str
    tag: str  # TODO: support for multiple tags
    track_id: int = None

@dataclass
class FrameInfo:
    """Special class to be sent by signal"""
    # TODO: Accept support for width and what not
    frame: np.ndarray
    frame_id: int
    data_init: dict
    data: List[FrameData] = field(init=False)

    # def __post_init_(self):
    #     for data in self.data_init:
    #         self.data.append(FrameData(
    #             data["x1"], data["y1"], data["x2"], data["y2"],
    #             data["object"], "dummy", data["track_id"]
    #         ))
    #             # self.data[]

    # x1: Union[float, int]
    # y1: Union[float, int]
    # x2: Union[float, int]
    # y2: Union[float, int]
    # object_class: str
    # tag: str  # TODO: support for multiple tags
    # frame_id: int = None
    # track_id: int = None
