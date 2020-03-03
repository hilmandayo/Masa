from dataclasses import dataclass, field
from typing import Union, Optional, Dict, List
from .data import Instance

import numpy as np

# @dataclass
# class FrameData:
#     """Special class to be sent by signal"""
#     # TODO: Accept support for width and what not
#     x1: Union[float, int]
#     y1: Union[float, int]
#     x2: Union[float, int]
#     y2: Union[float, int]
#     object_class: str
#     tag: str  # TODO: support for multiple tags
#     track_id: int = None

@dataclass
class FrameData:
    """Special class to be sent by signal.

    This class act as a data container for a certain `frame_id`.
    """
    # TODO: Accept support for width and what not
    frame_id: int
    data: List[Instance]
    frame: Optional[np.ndarray] = None

    @staticmethod
    def from_instances(frame_id, instances):
        return FrameData(frame_id, data=instances)
