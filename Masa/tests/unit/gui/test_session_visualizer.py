import pytest
from Masa.gui import SessionVisualizer, ImagesViewerView


@pytest.fixture(name="svv", scope="function")
def session_visualizer_view(data_handler, qtbot):
    svv = SessionVisualizer(data_handler)
    qtbot.add_widget(svv)
    return svv


def test_init(svv):
    svv.show()


# TODO: move this to proper file
def test_pass_buffer(m_buffer, ocv_video):
    m_buffer(ocv_video(), target_width=640)


def get_images_viewer():
    return [
        (ImagesViewerView,),
        (ImagesViewerView, ImagesViewerView),
        (ImagesViewerView, ImagesViewerView, ImagesViewerView),
    ]

@pytest.mark.skip(reason="Change of API")
@pytest.mark.parametrize("imgs_viewer", get_images_viewer())
def test_add_images_viewer(qtbot, svv, imgs_viewer):
    for i, img_v in enumerate(imgs_viewer):
        img_v = img_v()
        qtbot.add_widget(img_v)
        svv.add_images_viewer(str(i), img_v)
