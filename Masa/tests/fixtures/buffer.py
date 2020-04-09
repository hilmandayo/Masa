import pytest
import Masa
from Masa.tests.utils import DummyBufferFactory
from Masa.models.buffer import Buffer

@pytest.fixture(name="ocv_video", scope="function")
def ocv_tagged_video_factory(empty_data_dir):
    def vid(length=30, width=640, height=320):
        ocv_tagged_video = DummyBufferFactory.get_buffer(
            "ocv_simple_tagged", length=length, width=width, height=height
        )
        ocv_tagged_video.create_dummy_data(empty_data_dir)
        return ocv_tagged_video

    return vid

@pytest.fixture(name="m_buffer", scope="function")
def monkey_patched_buffer_class(monkeypatch):
    """Monkey patched `Masa.models.Buffer`.

    We want the `Buffer` to be able to receive our mocked video.
    """
    monkeypatch.setattr(Masa.models.buffer.cv2, "VideoCapture", lambda x: x)
    return Buffer

