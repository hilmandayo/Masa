from collections import defaultdict
from Masa.gui import ImagesViewerView
import pytest
from Masa.tests.utils import DummyAnnotationsFactory


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


simple_anno = DummyAnnotationsFactory.get_annotations("simple_anno")
def get_row_indexes():
    row_indexes = []
    for data in simple_anno.data:
        row_indexes.append(data[simple_anno.head.index("track_id")])

    return row_indexes

def get_col_indexes_per_row():
    pass
    return row_indexes

@pytest.fixture(scope="function", params=get_row_indexes())
def row_index(request):
    return request.param


@pytest.fixture(name="col_index", scope="function")
def col_index_per_row():
    pass



def test_show(ivv):
    ivv.show()


class TestAddData:
    def test_initialized_images_viewer_view(self, qtbot, ivv, data_handler, buff):
        ivv.get_frames.connect(buff.get_frames)
        buff.pass_frames.connect(ivv.refresh_images)
        ivv.init_data([instance
                    for tobj in data_handler
                    for instance in tobj])

        asserts = []
        for tobj, (label, row) in zip(data_handler, ivv._grid_map.items()):
            for instance, col in zip(tobj, row["col_meta"]):
                # Not perfect one... but hey...
                asserts.append(instance.frame_id == col["frame_id"])

        assert all(asserts)

class TestDeleteData:
    def test_delete_row(self, i_ivv):
        pass
    def test_delete_col_in_a_row(self, i_ivv):
        pass


# def test_adding_images(qtbot, s_finfo):
#     imgs_viewerv = ImagesViewerView()
#     imgs_viewerv.show()
#     qtbot.add_widget(imgs_viewerv)

#     for fi in s_finfo:
#         imgs_viewerv.add_to_row(fi)

# def test_requesting_frames_upon_init():
#     pass

