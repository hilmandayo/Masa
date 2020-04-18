from collections import namedtuple
from pathlib import Path
from typing import Union
import numpy as np

from PySide2 import QtGui as qtg, QtWidgets as qtw
import cv2


SignalPacket = namedtuple("SignalPacket", "sender data")
DataUpdateInfo = namedtuple("DataUpdateInfo", "added deleted replaced moved")
DataUpdateInfo.__new__.__defaults__ = (None, None, None, None)
FrameData = namedtuple("FrameData", "frame index data")
DataInfo = namedtuple("DataInfo", "tobj instance obj_classes tags")
DataInfo.__new__.__defaults__ = (None, None, None, None)


def create_dirs(dirs: Union[list, str]):
    """An utility to create directories.

    Raises
    ------
    TypeError
        If the passed directories are not of type `str` or `pathlib.Path`.
    """
    if isinstance(dirs, str):
        dirs = [dirs]

    _dirs = []
    for d in dirs:
        if isinstance(d, str):
            d = Path(d)
        elif isinstance(d, Path):
            pass
        else:
            raise TypeError(f"Cannot deal with type {type(d)}")
        _dirs.append(d)

    for d in _dirs:
        d.mkdir(exist_ok=True)

def delete_dirs(dirs: Union[list, str]):
    """An utility to delete directories."""
    pass


def convert_np(frame: np.ndarray, to: str = "qpixmap", scale: bool = True,
               input_bgr: bool = True) -> Union[qtg.QPixmap, qtw.QGraphicsPixmapItem]:
    # https://stackoverflow.com/questions/34232632/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image
    if input_bgr:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame = np.require(frame, np.uint8, "C")
    y2, width, channel = frame.shape
    bytes_per_line = width * 3
    # XXX: For some reasons, we need to copy it here.
    #      If I do `frame = qtg.QPixmap.fromImage(frame.copy())`,
    #      we will still got bad result.
    frame = qtg.QImage(frame.data, width, y2, bytes_per_line, qtg.QImage.Format_RGB888).copy()
    frame = qtg.QPixmap.fromImage(frame)
    if scale:
        frame = frame.scaled(width, y2)

    if to == "qpixmap":
        return frame
    elif to == "qpixmapitem":
        return qtw.QGraphicsPixmapItem(frame)


def resize_calculator(orig_width, orig_height,
                      target_width=None, target_height=None, ratio=True):
    if ratio:
        if target_width:
            ratio = target_width / orig_width
            target_height = int(orig_height * ratio)
        elif target_height:
            ratio = target_height / orig_height
            target_width = int(orig_width * ratio)
        else:
            raise ValueError(f"Both `width` and `y2` is not provided "
                              "while `ratio` is True")
    else:
        if not target_width:
            target_width = orig_width
        if not target_height:
            target_height = orig_height

    return target_width, target_height


class BoundingBoxConverter:
    @staticmethod
    def edge_bb_to_center_bb(x1, y1, x2, y2,
                             width_scale=None, height_scale=None, as_int=True):
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        width = abs(x2 - x1)
        y2 = abs(y2 - y1)

        if width_scale and height_scale:
            x, width = int(x * width_scale), int(width * width_scale)
            y, y2 = int(y * height_scale), int(y2 * height_scale)
        if as_int:
            x, width, y, y2 = int(x), int(width), int(y), int(y2)

        return x, y, width, y2

    @staticmethod
    def center_bb_to_edge_bb(x, y, width, y2,
                             width_scale=None, height_scale=None, as_int=True):
        wc = width / 2
        hc = y2 / 2
        x1 = x - wc
        x2 = x + wc
        y1 = y - hc
        y2 = y + hc


        if width_scale and height_scale:
            x1, x2 = int(x1 * width_scale), int(x2 * width_scale)
            y1, y2 = int(y1 * height_scale), int(y2 * height_scale)
        if as_int:
            x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)

        return x1, y1, x2, y2

    @staticmethod
    def calc_width_height(x1, y1, x2, y2,
                          width_scale=None, height_scale=None, as_int=True):
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width_scale and height_scale:
            x1, width = x1 * width_scale, width * width_scale
            y1, height = y1 * height_scale, height * height_scale
        if as_int:
            x1, y1, width, height = int(x1), int(y1), int(width), int(height)

        return x1, y1, width, height

    @staticmethod
    def calc_bottom_coord(x1, y1, width, height,
                          width_scale=None, height_scale=None, as_int=True):
        x2 = x1 + width
        y2 = y1 + height
        if width_scale and height_scale:
            x1, x2 = x1 * width_scale, x2 * width_scale
            y1, y2 = y1 * height_scale, y2 * height_scale
        if as_int:
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        return x1, y1, x2, y2
        


def resize(frame, width=None, y2=None, ratio: bool = True,
           inter=cv2.INTER_CUBIC):
    """Resize frame.

    If `ratio` is `True`, the frame will be resized by using the value of width.
    If `width` is not provided, `y2` will be used.

    Raises
    ------
    ValueError
        If `width` and `y2` is not provided when `ratio` is `True`.
    """
    orig_height, orig_width = frame.shape[:2]
    width, y2 = resize_calculator(
        orig_width, orig_height, target_width=width, target_height=y2, ratio=ratio
    )

    return cv2.resize(frame, (width, y2), interpolation=inter)
