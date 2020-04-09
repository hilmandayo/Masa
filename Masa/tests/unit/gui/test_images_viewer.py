from collections import defaultdict, namedtuple
from Masa.gui import ImagesViewerView
from Masa.core.data import TrackedObject
import pytest
from Masa.tests.utils import DummyAnnotationsFactory


# TODO: Makes this better
@pytest.fixture(
    name="c_tobjs",
    scope="function", params="red_traffic_light yellow_traffic_light".split())
def classed_tracked_objects(data_handler, request):
    tobjs = []
    for tobj in data_handler:
        if tobj.object_class == request.param:
            tobjs.append(tobj)

    return tobjs, request.param


@pytest.fixture(name="ivv", scope="function")
def images_viewer_view(qtbot, c_tobjs):
    ivv = ImagesViewerView(c_tobjs[1])
    qtbot.add_widget(ivv)
    return ivv, c_tobjs[0]

@pytest.fixture(name="buff", scope="function")
def buffer(m_buffer, ocv_video, data_handler):
    return m_buffer(ocv_video(length=100), target_width=640)


@pytest.fixture(name="i_ivv", scope="function")
def initialized_images_viewer_view(qtbot, ivv, buff):
    ivv, tobjs = ivv
    ivv.req_frames.connect(buff.get_frames_sl)
    buff.pass_frames.connect(ivv.set_frames_sl)
    ivv.init_data(tobjs)

    return ivv

class TestInitImagesViewerView():
    # TODO: How to make it as a class fixture?
    @pytest.fixture(scope="function", autouse=True)
    def _init_ivv(self, ivv, buff):
        self.ivv, self.tobjs = ivv
        self.ivv.req_frames.connect(buff.get_frames_sl)
        buff.pass_frames.connect(self.ivv.set_frames_sl)
        self.ivv.init_data(self.tobjs)

    def test_class_name(self):
        assert self.ivv.name == self.tobjs[0].object_class

    def test_labels_start_from_zero(self):
        labels_map = self.ivv.labels_mapping()
        assert labels_map[0][0] == 0

    def test_labels_seq(self):
        labels_map = self.ivv.labels_mapping()
        assert all([
            labels_map[i][0] + 1 == labels_map[i + 1][0]
            for i in range(len(labels_map) - 1)
        ])

    def test_labels_mapping(self):
        labels_map = self.ivv.labels_mapping()
        assert all([
            t_obj_id == tobj.track_id
            for (label, t_obj_id), tobj in zip(labels_map, self.tobjs)
        ])

    def test_image_buttons_length(self):
        labels_map = self.ivv.labels_mapping()
        assert all([
            len(self.ivv._grid_map[label]["image_buttons"]) == len(tobj)
            for (label, t_id), tobj in zip(labels_map, self.tobjs)
        ])
        

simple_anno = DummyAnnotationsFactory.get_annotations("simple_anno")
Index = namedtuple("Indexes", "row length")
def get_row_length_information():
    indexes = []
    cols_len = 0
    prev_row = None
    for data in simple_anno.data:
        curr_row = data[simple_anno.head.index("track_id")]

        if prev_row is None:
            # At the start.
            prev_row = curr_row

        if curr_row == prev_row:
            cols_len += 1
        else:
            indexes.append(Index(row=curr_row, length=cols_len))
            cols_len = 1

        prev_row = curr_row


    return indexes


@pytest.fixture(scope="function", params=get_row_length_information())
def row_info(request):
    return request.param


@pytest.fixture(scope="function")
def test_show(ivv):
    ivv.show()

def tracked_objs_factory(track_id, object_class):
    tobj = TrackedObject(
        track_id=track_id,
        object_class=object_class,
        instance = {"x1": 10, "y1": 10, "x2": 20, "y2": 20,
                    "frame_id": 2, "tags": {}}
    )
    return tobj

class TestAddTrackedObjectAnInstance:
    @pytest.fixture(scope="function", autouse=True)
    def _init(self, i_ivv):
        self._i_ivv = i_ivv

    def test_append_tobj(self):
        t_id = self._i_ivv.labels_mapping()[-1][1] + 1
        obj_cls = self._i_ivv.name
        t_obj = tracked_objs_factory(t_id, obj_cls)

        prev_lm = self._i_ivv.labels_mapping()
        self._i_ivv.add(t_obj)

        lm = self._i_ivv.labels_mapping()
        assert all([
            lm[:-1] == prev_lm,
            lm[-1] == ((len(lm) - 1), t_obj.track_id)
        ])

    def test_insert_tobj_middle(self):
        t_id = len(self._i_ivv) // 2
        obj_cls = self._i_ivv.name
        t_obj = tracked_objs_factory(t_id, obj_cls)

        prev_lm = self._i_ivv.labels_mapping()
        prev_t_ids = [i for _, i in prev_lm]
        self._i_ivv.add(t_obj)

        lm = self._i_ivv.labels_mapping()
        t_ids = [i for _, i in lm]
        inserted_label = self._i_ivv.labels_mapping(t_id)
        assert all([
            len(lm[:-1]) == len(prev_lm),
            ([t_id for _, t_id in lm[:inserted_label]] ==
             [t_id for _, t_id in prev_lm[:inserted_label]]),
            lm[inserted_label][1] == t_id,
            all([lm[i + 1][1] == prev_lm[i][1] + 1
                 for i in range(inserted_label, len(prev_lm))])
        ])

    def test_insert_tobj_zero(self):
        t_id = 0
        obj_cls = self._i_ivv.name
        t_obj = tracked_objs_factory(t_id, obj_cls)

        prev_lm = self._i_ivv.labels_mapping()
        self._i_ivv.add(t_obj)

        lm = self._i_ivv.labels_mapping()
        inserted_label = self._i_ivv.labels_mapping(t_id)
        assert all([
            len(lm[:-1]) == len(prev_lm),
            lm[inserted_label][1] == t_id,
            all([lm[i + 1][1] == prev_lm[i][1] + 1
                 for i in range(inserted_label, len(prev_lm))])
        ])

class TestDeleteTrackedObject:
    @pytest.fixture(scope="function", autouse=True)
    def _init(self, i_ivv):
        self._i_ivv = i_ivv

    def test_delete_last_tobj(self):
        prev_lm = self._i_ivv.labels_mapping()
        last_lm = prev_lm[-1]
        self._i_ivv.delete(last_lm[0])

        curr_lm = self._i_ivv.labels_mapping()
        assert all([
            curr_lm == prev_lm[:-1],
            last_lm[1] not in [t_id for _, t_id in curr_lm],
        ])

    def test_delete_middle_tobj(self):
        prev_lm = self._i_ivv.labels_mapping()
        del_label = len(prev_lm) // 2
        del_track_id = self._i_ivv.labels_mapping()[del_label][1]

        self._i_ivv.delete(del_label)

        curr_lm = self._i_ivv.labels_mapping()
        assert all([
            len(curr_lm) == len(prev_lm) - 1,
            all([t1[1] == t2[1] for t1, t2 in zip(prev_lm[:del_label], curr_lm[:del_label])]),
            all([prev_lm[i + 1][1] - 1 == curr_lm[i][1] for i in range(del_label, len(curr_lm))])
        ])

    def test_delete_first_tobj(self):
        prev_lm = self._i_ivv.labels_mapping()
        del_label = 0
        del_track_id = self._i_ivv.labels_mapping()[del_label][1]

        self._i_ivv.delete(del_label)

        curr_lm = self._i_ivv.labels_mapping()
        assert all([
            len(curr_lm) == len(prev_lm) - 1,
            all([t1[1] == t2[1] for t1, t2 in zip(prev_lm[:del_label], curr_lm[:del_label])]),
            all([prev_lm[i + 1][1] - 1 == curr_lm[i][1] for i in range(del_label, len(curr_lm))])
        ])
