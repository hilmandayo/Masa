from Masa.core.datahandler import TrackedObject
import pytest


def test_TO_single_instances_init(s_anno_rl):
    """Test whether `TrackedObject` can be properly instantiate."""
    # Get only the first data
    head, anno = s_anno_rl

    # Preprocess the data. We already know that only `track_id` and
    # `object_class` will need to be passed directly.
    # Anything else will be handled as `instance`.
    instance = {}
    for i, h in enumerate(head):
        if h not in ["track_id", "object"]:
            instance[h] = anno[i]

    tracked = TrackedObject(track_id=anno[head.index("track_id")],
                            object_class=anno[head.index("object")],
                            instance=instance)

@pytest.mark.skip
def test_TO_multiple_instances_init(s_anno_rli):
    pass


# TODO: Make this into class that check everything on instances
def test_TO_add_instances(s_anno_rli):
    # TODO: Improve this
    head, data = s_anno_rli
    tracked = None
    for d in data:
        track_id = d.pop(head.index("track_id"))
        object_class = d.pop(head.index("object"))
        if tracked is None:
            tracked = TrackedObject(track_id, object_class, d)
        else:
            tracked.add_instance(d)

    assert len(tracked) == len(data)


def test_s_tobjs_iter(l_stobj):
    for tobj in l_stobj:
        assert tobj


def test_change_tobjs_track_id(l_stobj):
    dummy_val = "dummy_val"
    for i, instance in enumerate(l_stobj):
        ins = instance["instance"]
        ins["object_class"] = dummy_val

        assert l_stobj[i]["instance"]["object_class"] == dummy_val


@pytest.mark.skip
def test_TO_init():
    pass


# def test_instance():
#     Instance(tags)