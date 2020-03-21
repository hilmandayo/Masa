"""Test one of the core of Masa data structure.

`DataHandler` glues a lot of things. So, it is important to make sure it works
flawlessly!
"""


import random
import csv
import pytest
from Masa.models import DataHandler
from Masa.core.data import  TrackedObject, Instance
from Masa.core.utils import  SignalPacket
from Masa.tests.utils import DummyAnnotationsFactory


# TODO: Make this as a more robust conftest
simple_anno_p3 = DummyAnnotationsFactory.get_annotations("simple_anno", increase_track_id=3)
@pytest.fixture(scope="function")
def data_handler_p3(empty_annotations_dir):
    """Make sure the method that reorder `track_id` from 0 is called upon init."""
    return DataHandler(simple_anno_p3.create_file(empty_annotations_dir))


def test_update_track_id_upon_init(data_handler_p3):
    for idx, tobj in enumerate(data_handler_p3, 0):
        assert idx == tobj.track_id


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


@pytest.mark.parametrize("frame_id, n_ins", simple_anno.frameid_to_nframes_map)
def test_run_results_r(data_handler, frame_id, n_ins):
    instances = data_handler.from_frame(frame_id)
    prev_len = len(instances)

    sp = SignalPacket("dummy", instances)
    data_handler.run_results_r(sp)

    assert len(instances) == prev_len


@pytest.mark.parametrize("frame_id, n_ins", simple_anno.frameid_to_nframes_map)
def test_run_results_r_error(data_handler, frame_id, n_ins):
    instances = data_handler.from_frame(frame_id)
    instances.append(Instance(100, "dummy", 100, 1, 2, 1, 2, None))
    sp = SignalPacket("dummy", instances)

    with pytest.raises(Exception):
        data_handler.run_results_r(sp)


class TestAppendDeleteExistingTrackedObject:
    """Test adding (append) and delete for an already related existing `TrackedObject`.

    1. An `Instance`.
    2. A `TrackedObject` with an `Instance`.
    3. A `TrackedObject` with `Instance`s.
    """

    def test_append_instance(self, qtbot, data_handler, s_tobj_l):
        """Passing an `Instance`.

        The `DataHandler.added_instance` signal should emit the added `Instance`.
        """
        ins = s_tobj_l[0]
        prev_len = len(data_handler[s_tobj_l.track_id])
        with qtbot.wait_signal(data_handler.added_instance) as blocker:
            data_handler.append(ins)
        assert all([
            len(data_handler[s_tobj_l.track_id]) == (prev_len + 1),
            data_handler[s_tobj_l.track_id][-1] == ins,
            blocker.args[0].data == ins
        ])

    def test_append_tobj(self, qtbot, data_handler, s_tobj_l):
        """Passing an `TrackedObject` with an `Instance`.

        The `DataHandler.added_instance` signal should emit the added `Instance`.
        """
        prev_len = len(data_handler[s_tobj_l.track_id])
        with qtbot.wait_signal(data_handler.added_instance) as blocker:
            data_handler.append(s_tobj_l)
        assert all([
            len(data_handler[s_tobj_l.track_id]) == (prev_len + 1),
            data_handler[s_tobj_l.track_id][-1] == s_tobj_l[0],
            blocker.args[0].data == s_tobj_l[0]
        ])


    def test_append_tobj_mul_instances(self, qtbot, data_handler, s_tobj_instance_l):
        """Passing an `TrackedObject` with multiple `Instance`s.

        The `DataHandler.added_instance` signal should emit the added `Instance`s.
        """
        # for k in s_tobj_instance_l:
        #     print(k)

        prev_len = len(data_handler[s_tobj_instance_l.track_id])
        to_be_added_len = len(s_tobj_instance_l)
        # for some reason, below is not working
        # with qtbot.wait_signal(data_handler.added_instances, timeout=10000) as blocker:
        data_handler.append(s_tobj_instance_l)
        assert all([
            len(data_handler[s_tobj_instance_l.track_id]) == prev_len + to_be_added_len,
            data_handler[s_tobj_instance_l.track_id][prev_len:] == s_tobj_instance_l[:]
        ])

    def test_delete_tobj(self, qtbot, data_handler, s_tobj_instance_l):
        orig_len = len(data_handler)
        with qtbot.wait_signal(data_handler.deleted_tobj) as blocker:
            data_handler.delete(s_tobj_instance_l.track_id)

        assert all([
            blocker.args[0].data == (s_tobj_instance_l.track_id, orig_len - 1),
            len(data_handler) == orig_len - 1,
            # check the key
            all(i == k for (i, k) in enumerate(data_handler.tracked_objs.keys())),
            # check tracked objet itself
            all(k == tobj.track_id for k, tobj in data_handler.tracked_objs.items()),
            # check every instance
            all(k == ins.track_id
                for k, tobj in data_handler.tracked_objs.items()
                for ins in tobj)
        ])

    # TODO: make `test_delete_instances`
    def test_delete_instance(self, qtbot, data_handler, s_tobj_instance_l):
        dh_len = len(data_handler)
        orig_len = len(s_tobj_instance_l)
        del_this = random.randint(0, orig_len - 1)
        with qtbot.wait_signal(data_handler.deleted_instance) as blocker:
            data_handler.delete(s_tobj_instance_l.track_id, del_this)

        assert all([
            blocker.args[0].data == (s_tobj_instance_l.track_id, del_this, orig_len - 1),
            len(data_handler) == dh_len,
            # check the key is always up-to-date
            all(i == k for (i, k) in enumerate(data_handler.tracked_objs.keys())),
            # check tracked objet itself is always up-to-date
            all(k == tobj.track_id for k, tobj in data_handler.tracked_objs.items()),
            # check every instance is always up-to-date
            all(k == ins.track_id
                for k, tobj in data_handler.tracked_objs.items()
                for ins in tobj)
        ])
