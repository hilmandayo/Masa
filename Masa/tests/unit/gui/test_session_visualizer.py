import pytest
from Masa.gui import SessionVisualizer


@pytest.fixture(name="svv", scope="function")
def session_visualizer_view(data_handler, qtbot):
    svv = SessionVisualizer(data_handler)
    qtbot.add_widget(svv)
    return svv


def test_init(svv):
    svv.show()


def test_pass_buffer(m_buffer, ocv_video):
    print(m_buffer(ocv_video(), target_width=640))
