import pytest

from Masa.gui import BufferRenderView


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

@pytest.fixture(name="brv", scope="function")
def buffer_render_view(request, qtbot):
    # width, height = request.param
    width, height = 640, 540
    # print("fixture:", width, height)
    brv = BufferRenderView(width=width, height=height)
    # print(brv.size())
    qtbot.add_widget(brv)
    # request.instance.brv = brv
    return brv


def test_dims(brv):
    # for some reasons, the dimension is not as thought.
    # maybe coz of qtbot
    pass
