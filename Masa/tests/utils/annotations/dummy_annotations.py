from Masa.core.data import TrackedObject


class DummyAnnotationsFactory:
    """A factory that returns certain mock annotations data."""
    @staticmethod
    def get_annotations(name, **kwargs):
        if name == "simple_anno":
            return SimpleAnnotations(**kwargs)


@dataclass
class DummyAnnotations:
    """A parent class that every annotations test data class should inherit.

    In this context, `head` will always means the metadata of the data,
    `data` will always means the actual data that corresponds to the `head` and
    annotations will mean the `head` and `data` combined.
    """
    TRACKED_OBJECT_CONSTANT_VARS: List[str] = field(
        init=False, default_factory=lambda: "track_id object".split()
    )
    INSTANT_CONSTANT_VARS: List[str] = field(
        init=False, default_factory=lambda: "frame_id x1 y1 x2 y2".split()
    )

    @property
    def to_tracked_objects(self):
        head, data = self.head, self.data_per_object_id
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
                    if h in self.INSTANT_CONSTANT_VARS:
                        instance_dict[h] = instance[head.index(h)]
                    elif h not in self.TRACKED_OBJECT_CONSTANT_VARS:
                        tags[h] = instance[head.index(h)]
                instance_dict["tags"] = tags

                if tobj is None:
                    tobj = TrackedObject(track_id, object_class, instance_dict)
                else:
                    tobj.add_instance(instance_dict)

            tobjs.append(tobj)

        return tobjs
