import pytest
from Masa.models.session import BBSession


def test_init_session(s_tobj_l):
    while len(s_tobj_l) != 1:
        s_tobj_l.delete(-1)

    bbs = BBSession()
    bbs.init.connect(added_tobj)
