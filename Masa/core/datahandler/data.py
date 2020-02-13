from dataclasses import dataclass, field
from typing import ClassVar, List


def default_tags():
    return {"view": ["small", "middle", "large"]}

def fixed_fields():
    return tuple("track_id object_class".split())


@dataclass
class TrackedObject:
    """Represents a single tracked object.

    A single object might have multiple instances.
    """
    track_id: int
    object_class: str
    instance: dict = field(repr=False)
    _fixed: List[str] = field(default_factory=fixed_fields)
    instances: List[dict] = field(default_factory=list, init=False)
    tags: dict = field(default_factory=default_tags)

    def __post_init__(self):
        self.add_instance(self.instance)

    def add_instance(self, instance: dir):
        self.instances.append(instance)

    def dict_instance(self, index):
        instance = self.__getitem__[index]
        instance_dict["track_id"] = self.track_id
        instance_dict["object_class"] = self.object_class
        instance_dict.update(instance)

        return instance_dict

    def to_dict(self):
        instances = []
        for instance in self.instances:
            instance_dict = {}
            instance_dict["track_id"] = self.track_id
            instance_dict["object_class"] = self.object_class
            instance_dict.update(instance)
            instances.append(instance_dict)

        return instances

    def change_track_id(self, track_id):
        self.track_id = track_id

    def __getitem__(self, index):
        return self.instances[index]

    def __iter__(self):
        self._iter = iter(self.instances)
        self._iter_idx = None
        return self

    def __next__(self):
        try:
            val = next(self._iter)
        except StopIteration:
            raise StopIteration()

        if self._iter_idx is None:
            self._iter_idx = 0
        else:
            self._iter_idx += 1

        val = {key: getattr(self, key) for key in self._fixed}.update(val)
        return val

    def __len__(self):
        return len(self.instances)
