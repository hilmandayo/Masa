from dataclasses import dataclass, field
from typing import Union, Optional

import numpy as np


@dataclass
class FrameInfo:
    """Special class to be sent by signal"""
    # TODO: Accept support for width and what not
    frame: np.ndarray
    x1: Union[float, int]
    y1: Union[float, int]
    x2: Union[float, int]
    y2: Union[float, int]
    object_class: str
    tag: str  # TODO: support for multiple tags
    frame_id: int = None
    track_id: int = None
