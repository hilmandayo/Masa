from copy import deepcopy
import pytest
from Masa.gui import SessionVisualizer, ImagesViewerView
from Masa.core.utils import SignalPacket, DataUpdateInfo


@pytest.fixture(name="_svv", scope="function")
def session_visualizer_view_not_init(qtbot):
    svv = SessionVisualizer()
    qtbot.add_widget(svv)
    return svv

@pytest.fixture(name="svv", scope="function")
def session_visualizer_view(qtbot, _svv, buff, data_handler):
    _svv.init_data(data_handler[:])
    for iv in _svv:
        iv.req_frames.connect(buff.get_frames_sl)
        buff.pass_frames.connect(iv.set_frames_sl)
    return _svv


@pytest.fixture(scope="function")
def buff(m_buffer, ocv_video, data_handler):
    buff = m_buffer(ocv_video(length=max(data_handler.frames) + 30), target_width=640)
    buff.start()
    yield buff
    buff.stop_thread()
    buff.quit()


class TestInit:
    def test_recieve_frames_upon_init(self, buff, _svv, data_handler):
        """Frames should be request and passed after `init_data` is called."""
        _svv.init_data(data_handler[:])
        for iv in _svv:
            # TODO: How to connect through _svv directly?
            iv.req_frames.connect(buff.get_frames_sl)
            buff.pass_frames.connect(iv.set_frames_sl)

class TestAddInstance:
    def test_append_one_instance(self, data_handler, svv, s_tobj_l, qtbot):
        instance = deepcopy(s_tobj_l[0])
        instance.instance_id = len(data_handler[instance.track_id])
        dui = DataUpdateInfo(added=instance)
        svv.data_update_sl(
            SignalPacket(sender="dummy", data=dui)
        )

        for iv in svv:
            idx = iv.labels_mapping(instance.track_id)
            if idx is not None:
                break

        # since basically `data_handler` used `s_tobj_l`
        img_btns = iv[idx]["image_buttons"]
        assert all([
            len(img_btns) == len(data_handler[instance.track_id]) + 1,
            img_btns[instance.instance_id].x1 == instance.x1,
            img_btns[instance.instance_id].y1 == instance.y1,
            img_btns[instance.instance_id].x2 == instance.x2,
            img_btns[instance.instance_id].y2 == instance.y2,
        ])


    def test_insert_one_instance(self, data_handler, svv, s_tobj_l, qtbot):
        instance = deepcopy(s_tobj_l[0])
        instance.instance_id = len(data_handler[instance.track_id]) - 1
        dui = DataUpdateInfo(added=instance)
        svv.data_update_sl(
            SignalPacket(sender="dummy", data=dui)
        )

        for iv in svv:
            idx = iv.labels_mapping(instance.track_id)
            if idx is not None:
                break

        # since basically `data_handler` used `s_tobj_l`
        img_btns = iv[idx]["image_buttons"]
        assert all([
            len(img_btns) == len(data_handler[instance.track_id]) + 1,
            img_btns[instance.instance_id].x1 == instance.x1,
            img_btns[instance.instance_id].y1 == instance.y1,
            img_btns[instance.instance_id].x2 == instance.x2,
            img_btns[instance.instance_id].y2 == instance.y2,
            img_btns[instance.instance_id].track_id == instance.track_id,
        ])


class TestAddTrackedObject:
    def test_append_one_tracked_obj_with_one_instance(self, data_handler, svv, s_tobj_l, qtbot):
        tobj = deepcopy(s_tobj_l)
        tobj.change_track_id(len(data_handler))
        dui = DataUpdateInfo(added=tobj)
        svv.data_update_sl(
            SignalPacket(sender="dummy", data=dui)
        )

        for iv in svv:
            idx = iv.labels_mapping(tobj.track_id)
            if idx is not None:
                break

        # since basically `data_handler` used `s_tobj_l`
        img_btns = iv[idx]["image_buttons"]
        assert all([
            len(img_btns) == 1,
            img_btns[tobj[0].instance_id].x1 == tobj[0].x1,
            img_btns[tobj[0].instance_id].y1 == tobj[0].y1,
            img_btns[tobj[0].instance_id].x2 == tobj[0].x2,
            img_btns[tobj[0].instance_id].y2 == tobj[0].y2,
        ])

    def test_insert_one_tracked_obj_with_one_instance(self, data_handler, svv, s_tobj_l, qtbot):
        tobj = deepcopy(s_tobj_l)
        if tobj.track_id == 0:
            tobj.change_track_id(1)
            tobj.object_class = data_handler[1].object_class
        else:
            tobj.change_track_id(0)
            tobj.object_class = data_handler[0].object_class

        dui = DataUpdateInfo(added=tobj)
        svv.data_update_sl(
            SignalPacket(sender="dummy", data=dui)
        )

        for iv in svv:
            idx = iv.labels_mapping(tobj.track_id)
            if idx is not None:
                break

        # since basically `data_handler` used `s_tobj_l`
        img_btns = iv[idx]["image_buttons"]
        assert all([
            len(img_btns) == 1,
            img_btns[tobj[0].instance_id].x1 == tobj[0].x1,
            img_btns[tobj[0].instance_id].y1 == tobj[0].y1,
            img_btns[tobj[0].instance_id].x2 == tobj[0].x2,
            img_btns[tobj[0].instance_id].y2 == tobj[0].y2,
        ])        
        
class TestDelete:

    def test_delete_instance(self, svv, s_tobj_instance_l):
        delete = s_tobj_instance_l.track_id, len(s_tobj_instance_l) // 2

        iv = svv.get(s_tobj_instance_l.object_class)
        prev_lm = iv.labels_mapping()
        prev_label = iv.labels_mapping(delete[0])
        prev_len = len(iv[prev_label]["image_buttons"])

        dui = DataUpdateInfo(deleted=delete)
        svv.data_update_sl(
            SignalPacket(sender="dummy", data=dui)
        )

        curr_lm = iv.labels_mapping()
        curr_label = iv.labels_mapping(delete[0])
        if prev_len != 1:
            curr_len = len(iv[prev_label]["image_buttons"])

        if prev_len == 1:
            # Deleted a row...
            assert all([
                len(prev_lm) - 1 == len(curr_lm),
                all([curr_lm[i][0] + 1 == curr_lm[i + 1][0] for i in range(len(curr_lm) - 1)])
            ])
        else:
            assert all([
                curr_label == prev_label,
                curr_len == prev_len - 1
            ])

    def test_delete_tobj(self, svv, s_tobj_instance_l):
        delete = s_tobj_instance_l.track_id, None

        iv = svv.get(s_tobj_instance_l.object_class)
        prev_lm = iv.labels_mapping()
        prev_label = iv.labels_mapping(delete[0])

        dui = DataUpdateInfo(deleted=delete)
        svv.data_update_sl(
            SignalPacket(sender="dummy", data=dui)
        )

        curr_lm = iv.labels_mapping()
        curr_label = iv.labels_mapping(delete[0])

        assert all([
            len(prev_lm) == len(curr_lm) + 1,
        ])
        

class TestReplace:
    def test_replace_instance(self, svv, s_tobj_instance_l):
        pass

class TestMove:
    def test_move_instance(self, qtbot, data_handler, s_tobj_l):
        pass

