"""Define the necessary fixtures that will need to be used globally."""

from collections import namedtuple
from pathlib import Path
import uuid

from PySide2 import QtCore as qtc
import cv2
import numpy as np
import pytest

from Masa.core.data import TrackedObject, FrameData
from Masa.models import Buffer, DataHandler
import Masa.models.buffer

from Masa.tests.fixtures.data_center import *
from Masa.tests.fixtures.annotations import *
from Masa.tests.fixtures.buffer import *


# Video buffer related test data ##############################################
# FrameData related test data #################################################


# GUI #########################################################################
@pytest.fixture(name="gui_imgb")
def gui_image_button(qtbot):
    image = np.zeros([240, 240, 3], np.uint8)
    imgb = GUIFactory.get_gui("image_button", image)
    imgb.show()
    qtbot.add_widget(imgb)
    return imgb
