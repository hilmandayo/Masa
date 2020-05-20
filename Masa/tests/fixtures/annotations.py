from collections import namedtuple
import uuid
import pytest
from Masa.tests.utils import DummyAnnotationsFactory
from Masa.core.data import TrackedObject
from Masa.models.datahandler import DataHandler



@pytest.fixture(name="s_anno_factory", scope="session")
def simple_annotations_factory():
    def new_simple_annotations(increase_track_id=None):
        return DummyAnnotationsFactory.get_annotations("simple_anno", increase_track_id)
    return new_simple_annotations

simple_anno = DummyAnnotationsFactory.get_annotations("simple_anno")

@pytest.fixture(name="s_anno_rl", scope="session",
                params=simple_anno.data)
def simple_raw_annotations_loop(request):
    return simple_anno.head, request.param


@pytest.fixture(name="s_anno_rli", scope="session",
                params=simple_anno.data_per_object_id)
def simple_raw_annotations_loop_per_object_id(request):
    return simple_anno.head, request.param


AnnotationsSet = namedtuple("AnnotationsSet", "file head data")
@pytest.fixture(name="s_anno_rf_class",scope="class")
def simple_raw_annotations_file_class(data_id_dir_factory):
    data_id_dir = data_id_dir_factory(str(uuid.uuid4()))
    data_id_dir.mkdir()
    return AnnotationsSet(
        simple_anno.create_file(data_id_dir),
        simple_anno.head, simple_anno.data
    )


@pytest.fixture(name="s_anno_rf",scope="function")
def simple_raw_annotations_file(empty_annotations_dir):
    return AnnotationsSet(
        simple_anno.create_file(empty_annotations_dir),
        simple_anno.head, simple_anno.data
    )


@pytest.fixture(scope="function")
def data_handler(s_anno_rf):
    dh = DataHandler(s_anno_rf.file)
    return dh

# TODO: Change track_id and object
TRACKED_OBJECT_CONSTANT_VARS = "track_id object".split()
INSTANT_CONSTANT_VARS = "frame_id x1 y1 x2 y2".split()
def tracked_objects_per_object_id():
    head, data = simple_anno.head, simple_anno.data_per_object_id
    tobjs = []
    for d in data:
        tobj = None
        _tobjs = []
        for instance in d:
            instance_dict = {}
            track_id = instance[head.index("track_id")]
            object_class = instance[head.index("object")]
            tags = {}
            for h in head:
                if h in INSTANT_CONSTANT_VARS:
                    instance_dict[h] = instance[head.index(h)]
                elif h not in TRACKED_OBJECT_CONSTANT_VARS:
                    tags[h] = instance[head.index(h)]
            instance_dict["tags"] = tags

            if tobj is None:
                tobj = TrackedObject(track_id, object_class, instance_dict)
            else:
                tobj.add_instance(instance_dict)

        tobjs.append(tobj)

    return tobjs


def tracked_objects():
    head, data = simple_anno.head, simple_anno.data
    tobjs = []
    for d in data:
        instance_dict = {}
        track_id = d[head.index("track_id")]
        object_class = d[head.index("object")]
        tags = {}
        for h in head:
            if h in INSTANT_CONSTANT_VARS:
                instance_dict[h] = d[head.index(h)]
            elif h not in TRACKED_OBJECT_CONSTANT_VARS:
                tags[h] = d[head.index(h)]
        instance_dict["tags"] = tags

        tobj = TrackedObject(track_id, object_class, instance_dict)
        tobjs.append(tobj)

    return tobjs


@pytest.fixture(name="s_tobj_l", scope="function",
                params=tracked_objects())
def simple_tracked_object_loop(request):
    return request.param

@pytest.fixture(name="s_tobj_instance_l", scope="function",
                params=tracked_objects_per_object_id())
def simple_tracked_object_instance_loop(request):
    return request.param
