import pytest

from ..utils import DummyAnnotationsFactory
from Masa.core.datahandler import TrackedObject


@pytest.fixture(name="dh", scope="function")
def data_handler(srf_anno):
    dh = DataHandler(srf_anno.file)
    return dh

simple_anno = DummyAnnotationsFactory.get_annotations("simple_anno")
def make_tracked_objects():
    head, data = simple_anno.head, simple_anno.data_per_instance
    tobjs = []
    for d in data:
        tobj = None
        for instance in d:
            instance_dict = {}
            track_id = instance[head.index("track_id")]
            object_class = instance[head.index("object")]
            for h in head:
                if h not in ["track_id", "object"]:
                    instance_dict[h] = instance[head.index(h)]
            if tobj is None:
                tobj = TrackedObject(track_id, object_class, instance_dict)
            else:
                tobj.add_instance(instance_dict)
        tobjs.append(tobj)

    return tobjs

@pytest.fixture(name="l_stobj", scope="function", params=make_tracked_objects())
def simple_tracked_object_loop(request):
    return request.param
