from copy import deepcopy
import pytest
from Masa.models.session import BBSession
from Masa.models.datahandler import DataHandler
from Masa.core.utils import SignalPacket

@pytest.fixture(name="edh", scope="function")
def empty_data_handler(empty_annotations_dir):
    ann = (empty_annotations_dir / "annotations.csv")
    ann.write_text("")
    return DataHandler(ann)


@pytest.fixture(name="bbs")
def set_up_bbsession_data_handler(data_handler):
    """Set up the `DataHandler`."""
    bbs = BBSession(data_handler)
    return bbs


def test_init_session_tobj(edh, s_tobj_l):
    tobj = deepcopy(s_tobj_l)
    while len(tobj) != 1:
        tobj.delete(-1)

    if tobj.track_id != 0:
        tobj.change_track_id(0)
    bbs = BBSession(edh)
    # bbs.added_tobj.connect(edh.add_r)

    bbs.add_tobj_sl(SignalPacket(sender="dummy", data=tobj))
    assert all([
        len(edh) == 1,
        edh[0] == tobj,
    ])


def test_add_instance(bbs, s_tobj_l):
    prev_len = len(bbs.get_tobj(s_tobj_l.track_id))
    bbs.add_instance_sl(SignalPacket(sender="dummy", data=s_tobj_l))

    assert all([
        len(bbs.get_tobj(s_tobj_l.track_id)) == prev_len + 1,
        bbs.get_tobj(s_tobj_l.track_id)[-1] == s_tobj_l[0]
    ])


def test_get_tobj(bbs, s_tobj_instance_l):
    bbs.get_tobj(s_tobj_instance_l.track_id)
