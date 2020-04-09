"""Test one of the core of Masa data structure.

`DataHandler` glues a lot of things. So, it is important to make sure it works
flawlessly!
"""


import random
import csv
import pytest
from copy import deepcopy
from Masa.models import DataHandler
from Masa.core.data import  TrackedObject, Instance
from Masa.core.utils import  SignalPacket
from Masa.tests.utils import DummyAnnotationsFactory


# TODO: Make this as a more robust conftest
@pytest.fixture(name="dhc_p3", scope="function")
def data_handler_plus_3_class(s_anno_factory):
    """Make sure the method that reorder `track_id` from 0 is called upon init."""
    # The downside of using fixture instead of direct class is that I
    # cannot execute it in loop for test.
    # XXX: Something is really wrong with simple annotations class... Beware..
    return  s_anno_factory(3)

def test_dhf_p3(dhc_p3):
    """Make sure `dhf_p3` really did plus with three."""
    out = [data[0] for data in dhc_p3.data]
    assert min(out) == 3

@pytest.fixture(name="dh_p3", scope="function")
def data_handler_plus_3_file(dhc_p3, empty_annotations_dir):
    """Make sure the method that reorder `track_id` from 0 is called upon init."""
    dh_3_f = dhc_p3.create_file(empty_annotations_dir)
    dh = DataHandler(dh_3_f)
    return dh


class TestUponInit():
    # TODO: Test sort sequence based on frame_id
    def test_track_id_sequence(self, dh_p3):
        ret_tid = []
        ret_tid_internal_key = []
        for idx, (tobj, tobj_in_key) in enumerate(zip(dh_p3, dh_p3.tracked_objs.keys()), 0):
            ret_tid.append(idx == tobj.track_id)
            ret_tid_internal_key.append(idx == tobj_in_key)
        assert all([
            all(ret_tid), all(ret_tid_internal_key)
        ])
    def test_instance_id_sequence(self, dh_p3):
        ret = []
        for idx, tobj in enumerate(dh_p3):
            ret.append(all(tobj[idx].instance_id == tobj[idx + 1].instance_id - 1
                           for idx in range(len(tobj) - 1)))
        assert all(ret)
        
def test_simple_annotations(s_anno_rf):
    """Make sure we have a correct simple annotations test data to work with.

    Read the raw file, and make sure it maps correctly to the raw data.
    """
    out = []
    with s_anno_rf.file.open("r") as f:
        csv_anno = csv.DictReader(f)
        for anno, data in zip(csv_anno, s_anno_rf.data):
            for i, h in enumerate(s_anno_rf.head):
                anno_val = anno[h]
                data_val = data[i]
                if isinstance(data_val, int):
                    anno_val = int(anno_val)
                elif isinstance(data_val, float):
                    anno_val = float(anno_val)

                out.append(anno_val == data_val)

    assert all(out)


def test_iter_dh(s_anno_rf):
    """Instantiated `DataHandler` should gives `TrackedObject`"""
    dh = DataHandler(s_anno_rf.file)
    assert all(isinstance(to, TrackedObject) for to in dh)

simple_anno = DummyAnnotationsFactory.get_annotations("simple_anno")

@pytest.mark.parametrize("frame_id, n_ins", simple_anno.frameid_to_nframes_map)
def test_index_frame(s_anno_rf, frame_id, n_ins):
    dh = DataHandler(s_anno_rf.file)
    out = dh.from_frame(frame_id)
    assert len(out) == n_ins


@pytest.mark.skip()
@pytest.mark.parametrize("frame_id, n_ins", simple_anno.frameid_to_nframes_map)
def test_slun_slesults_sl(data_handler, frame_id, n_ins):
    instances = data_handler.from_frame(frame_id)
    prev_len = len(instances)

    sp = SignalPacket("dummy", instances)
    data_handler.run_slesults_sl(sp)

    assert len(instances) == prev_len


@pytest.mark.skip()
@pytest.mark.parametrize("frame_id, n_ins", simple_anno.frameid_to_nframes_map)
def test_run_results_r_error(data_handler, frame_id, n_ins):
    instances = data_handler.from_frame(frame_id)
    instances.append(Instance(100, "dummy", 100, 1, 2, 1, 2, None))
    sp = SignalPacket("dummy", instances)

    with pytest.raises(Exception):
        data_handler.run_slesults_sl(sp)

class TestAddInstance:
    def test_append_one_instance(self, qtbot, data_handler, s_tobj_l):
        instance = deepcopy(s_tobj_l[0])
        prev_len = len(data_handler[instance.track_id])
        instance = deepcopy(instance)
        instance.instance_id = prev_len
        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.add(instance)
        dui = blocker.args[0].data
        assert all([
            data_handler[instance.track_id][instance.instance_id] == instance,
            len(data_handler[instance.track_id]) == prev_len + 1,
            dui.added == instance
        ])

    def test_insert_one_instance(self, qtbot, data_handler, s_tobj_l):
        instance = deepcopy(s_tobj_l[0])
        prev_len = len(data_handler[instance.track_id])
        offset = len(data_handler[instance.track_id][instance.instance_id:])

        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.add(instance)
        dui = blocker.args[0].data
        assert all([
            data_handler[instance.track_id][instance.instance_id] == instance,
            len(data_handler[instance.track_id]) == prev_len + 1,
            dui.added == instance,
            offset == len(data_handler[instance.track_id][instance.instance_id + 1:])
        ])

class TestAddTrackedObject:
    def test_append_one_tracked_obj_with_one_instance(self, qtbot, data_handler, s_tobj_l):
        prev_len = len(data_handler)
        # TODO: Why this will effect the next test and that is why
        #       I need to copy it?
        s_tobj_l = deepcopy(s_tobj_l)
        s_tobj_l.change_track_id(prev_len)
        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.add(s_tobj_l)
        dui = blocker.args[0].data
        assert all([
            data_handler[s_tobj_l.track_id] == s_tobj_l,
            len(data_handler) == prev_len + 1,
            dui.added == s_tobj_l
        ])

    def test_insert_one_tracked_obj_with_one_instance(self, qtbot, data_handler, s_tobj_l):
        if s_tobj_l.track_id == len(data_handler):
            s_tobj_l = deepcopy(s_tobj_l)
            s_tobj_l.change_track_id(len(data_handler) - 1)
        prev_len = len(data_handler)
        offset = len(data_handler[s_tobj_l.track_id:])

        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.add(s_tobj_l)
        dui = blocker.args[0].data

        keys = list(data_handler.tracked_objs.keys())
        assert all([
            data_handler[s_tobj_l.track_id] == s_tobj_l,
            len(data_handler) == prev_len + 1,
            dui.added == s_tobj_l,
            offset == len(data_handler[s_tobj_l.track_id + 1:]),
            all(keys[i] + 1 == keys[i + 1] for i in range(len(keys) - 1))
        ])


class TestDelete:
    def test_delete_instance(self, qtbot, data_handler, s_tobj_l):
        instance = s_tobj_l[0]
        prev_len =len(data_handler[instance.track_id])  
        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.delete(instance.track_id, instance.instance_id)

        instances = data_handler[instance.track_id]
        dui = blocker.args[0].data
        assert all([
            len(instances) == prev_len - 1,
            all(instances[i].instance_id == instances[i + 1].instance_id - 1
                for i in range(len(instances) - 1)),
            dui.deleted == (instance.track_id, instance.instance_id)
        ])
        
    def test_delete_tobj(self, qtbot, data_handler, s_tobj_l):
        prev_len =len(data_handler)  
        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.delete(s_tobj_l.track_id)

        keys = list(data_handler.tracked_objs.keys())
        dui = blocker.args[0].data
        assert all([
            len(data_handler) == prev_len - 1,
            all(keys[i] == keys[i + 1] - 1
                for i in range(len(keys) - 1)),
            all(data_handler[i].track_id == i
                for i in keys),
            dui.deleted == (s_tobj_l.track_id, None)
        ])

class TestReplace:
    def test_replace_instance(self, qtbot, data_handler, s_tobj_l):
        rep_pos = (0, 0)
        if s_tobj_l.track_id == 0 and s_tobj_l[0].instance_id == 0:
            rep_pos = (2, 1)

        instance = deepcopy(s_tobj_l[0])
        instance.track_id = rep_pos[0]
        instance.instance_id = rep_pos[1]
        prev_tobj_len = len(data_handler)
        prev_instances_len = [len(tobj) for tobj in data_handler]

        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            data_handler.replace(instance)

        dui = blocker.args[0].data
        assert all([
            prev_tobj_len == len(data_handler),
            prev_instances_len == [len(tobj) for tobj in data_handler],
            data_handler[rep_pos[0]][rep_pos[1]] == instance,
            dui.replaced == instance
        ])

class TestMove:
    def test_move_instance(self, qtbot, data_handler, s_tobj_l):
        dest_pos = (2, 1)
        if s_tobj_l.track_id == dest_pos[0]:
            dest_pos = (0, 0)
        old_pos = (s_tobj_l.track_id, s_tobj_l[0].instance_id)

        instance = deepcopy(s_tobj_l[0])
        instance.track_id = dest_pos[0]
        instance.instance_id = dest_pos[1]

        prev_tobj_len = len(data_handler)
        prev_instances_len_0 = len(data_handler[old_pos[0]])
        prev_instances_len_1 = len(data_handler[instance.track_id])

        with qtbot.wait_signal(data_handler.data_updated) as blocker:
            # delete old_pos, put instance to its place
            data_handler.move(old_pos, instance)

        dui = blocker.args[0].data
        assert all([
            prev_tobj_len == len(data_handler),
            prev_instances_len_0 - 1 == len(data_handler[old_pos[0]]),
            prev_instances_len_1 + 1 == len(data_handler[instance.track_id]),
            data_handler[instance.track_id][instance.instance_id] == instance,
            dui.moved == (old_pos, instance)
        ])


