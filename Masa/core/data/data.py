from dataclasses import dataclass, field
from typing import ClassVar, List, Union, Optional


@dataclass(order=True)
class Instance:
    """Instance of tracked object."""
    track_id: int
    object_class: str
    instance_id: int
    x1: Union[int, float]
    y1: Union[int, float]
    x2: Union[int, float]
    y2: Union[int, float]
    frame_id: int
    tag = "dummy"
    # parent: Optional[TrackedObject] = None


def default_tags():
    return {"view": ["small", "middle", "large"]}


def fixed_fields():
    return tuple("track_id object_class".split())


@dataclass
class TrackedObject:
    """Represents a single tracked object.

    A single object might have multiple instances.
    """
    # TODO: Rename `track_id` to `object_id`
    track_id: int
    object_class: str
    instance: dict = field(repr=False)
    _fixed: List[str] = field(default_factory=fixed_fields)
    instances: List[dict] = field(default_factory=list, init=False)
    tags: dict = field(default_factory=default_tags)

    def __post_init__(self):
        self.add_instance(self.instance)

    def add_instance(self, instance: Union[dict, Instance]):
        if isinstance(instance, dict):
            instance = self._dict_to_instance(instance)
        self.instances.append(instance)

    def _dict_to_instance(self, instance: dict):
        i = instance
        instance = Instance(self.track_id, self.object_class,
                            len(self.instances),
                            i["x1"], i["y1"], i["x2"], i["y2"],
                            i["frame_id"])
        return instance

    def change_track_id(self, track_id):
        self.track_id = track_id
        for instance in self.instances:
            instance.track_id = self.track_id
        return self

    def delete(self, idx):
        del self.instances[idx]
        return self

    def __getitem__(self, index):
        return self.instances[index]

    def __iter__(self):
        self._iter = iter(self.instances)
        self._iter_idx = None
        return self

    def __next__(self):
        if self._iter_idx is None:
            self._iter_idx = 0
        else:
            self._iter_idx += 1

        try:
            val = self.__getitem__(self._iter_idx)
        except IndexError:
            raise StopIteration

        return val

    def __len__(self):
        return len(self.instances)
