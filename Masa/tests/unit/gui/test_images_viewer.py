from Masa.gui import ImagesViewerView
import pytest


@pytest.fixture(name="ivv", scope="function")
def images_viewer_view(qtbot):
    ivv = ImagesViewerView()
    qtbot.add_widget(ivv)
    return ivv

@pytest.fixture(name="buff", scope="function")
def buffer(m_buffer, ocv_video, data_handler):
    return m_buffer(ocv_video(length=100), target_width=640)


@pytest.fixture(name="i_ivv", scope="function")
def initialized_images_viewer_view(qtbot, data_handler, buff):
    ivv = ImagesViewerView()
    qtbot.add_widget(ivv)
    # Refreshing images stuff #################################################
    ivv.get_frames.connect(buff.get_frames)
    buff.pass_frames.connect(ivv.refresh_images)
    # End #####################################################################
    ivv.init_data([instance
                   for tobj in data_handler
                   for instance in tobj])
    return ivv


def test_show(ivv):
    ivv.show()


def test_initialized_images_viewer_view(qtbot, ivv, data_handler, buff):
    ivv.get_frames.connect(buff.get_frames)
    buff.pass_frames.connect(ivv.refresh_images)
    ivv.init_data([instance
                   for tobj in data_handler
                   for instance in tobj])

    asserts = []
    for tobj, (label, row) in zip(data_handler, ivv._idx_map.items()):
        for instance, col in zip(tobj, row["col_meta"]):
            # Not perfect one... but hey...
            asserts.append(instance.frame_id == col["frame_id"])

    assert all(asserts)

# def test_adding_images(qtbot, s_finfo):
#     imgs_viewerv = ImagesViewerView()
#     imgs_viewerv.show()
#     qtbot.add_widget(imgs_viewerv)

#     for fi in s_finfo:
#         imgs_viewerv.add_to_row(fi)

# def test_requesting_frames_upon_init():
#     pass

