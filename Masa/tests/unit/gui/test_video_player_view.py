import numpy as np
import pytest

from Masa.gui import VideoPlayerView


class Dims:
    """Class to produce some combination of width and height."""
    @staticmethod
    def values():
        dims = [
            # width x height
            (640, 540),
            (1080, 720),
            (640, 720),
        ]
        return dims
    @staticmethod
    def ids():
        return [f"W:{width}, H:{height}" for width, height in Dims.values()]


@pytest.fixture(name="vpv", scope="function", params=Dims.values(), ids=Dims.ids())
def video_player_view(request, qtbot):
    width, height = request.param
    vpv = VideoPlayerView(width=width, height=height)
    qtbot.add_widget(vpv)
    # request.instance.vpv = vpv
    return vpv


@pytest.mark.skip(reason="Need to figure out how the qtbot altered the size")
class TestAttributes:
    @pytest.mark.usefixtures("vpv")
    def test_dims(self, vpv):
        # the inherited `QGraphicsScene` should have the same `QSize`
        # as video player view attributes
        # print("test:", request.instance.vpv.size())
        # assert (request.instance.vpv.width == request.instance.vpv.video_view.size().width and
        #         request.instance.vpv.height == request.instance.vpv.video_view.size().height)
        assert (vpv.width == vpv.video_view.size().width() and
                vpv.height == vpv.video_view.size().height())


def test_passing_framedata(data_handler, vpv):
    size = vpv.video_view.size()
    dummy = np.zeros([size.height(), size.width(), 3], np.uint8)
    for frame_id in data_handler.frames():
        frame_data = data_handler.from_frame(frame_id, to="frameinfo")
        frame_data.frame = dummy

        vpv.set_data(frame_data)
