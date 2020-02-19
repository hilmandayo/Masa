from PySide2 import QtWidgets as qtw
import pytest


def test_image_button(gui_imgb):
    assert isinstance(gui_imgb, qtw.QPushButton)
