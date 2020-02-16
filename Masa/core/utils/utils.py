from pathlib import Path
from typing import Union
import numpy as np

from PySide2 import QtGui as qtg
import cv2


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


def np_to_pixmap(frame: np.ndarray, scale=True, input_bgr=True):
    # https://stackoverflow.com/questions/34232632/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image
    frame = np.require(frame, np.uint8, "C")
    height, width, channel = frame.shape
    bytes_per_line = width * 3
    frame = qtg.QImage(frame.data, width, height, bytes_per_line, qtg.QImage.Format_RGB888)
    if input_bgr:
        frame = frame.rgbSwapped()
    frame = qtg.QPixmap.fromImage(frame)
    if scale:
        frame = frame.scaled(width, height)

    return frame


def resize(frame, width=None, height=None, ratio: bool = True,
           inter=cv2.INTER_CUBIC):
    """Resize frame.

    If `ratio` is `True`, the frame will be resized by using the value of width.
    If `width` is not provided, `height` will be used.

    Raises
    ------
    ValueError
        If `width` and `height` is not provided when `ratio` is `True`.
    """
    orig_height, orig_width = frame.shape[:2]
    if ratio:
        if width:
            ratio = width / orig_width
            height = int(frame.height * ratio)
        elif heigth:
            ratio = height / orig_height
            width = int(orig_width * ratio)
        else:
            raise ValueError(f"Both `width` and `height` is not provided "
                              "while `ratio` is True")
    else:
        if not width:
            width = orig_width
        if not height:
            height = orig_height

    return cv2.resize(frame, (width, height), interpolation=inter)
