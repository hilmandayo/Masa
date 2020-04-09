from Masa.gui.dialog import editor_dialog_factory
from Masa.gui import SessionVisualizer


@pytest.fixture(name="svv", scope="function")
def session_visualizer_view(qtbot, buff, data_handler):
    svv = SessionVisualizer()
    qtbot.add_widget(svv)
    svv.init_data(data_handler[:])
    for iv in svv:
        iv.req_frames.connect(buff.get_frames_sl)
        buff.pass_frames.connect(iv.set_frames_sl)
    return svv


def test_request_from_images_viewers(svv, data_handler):
    svv.req_data.connect(data_handler.get_data_sl)
    data_handler.pass_data(svv.receive_data_sl)

