from dataclasses import dataclass, field
from typing import ClassVar, List


def default_tags():
    return {"view": ["small", "middle", "large"]}


@dataclass
class TrackObject:
    """Represents a single tracked object.

    A single object might have multiple instances.
    """
    track_id: int
    object_class: str
    instances: list = field(default_factory=list, init=False)
    instance: dict = field(repr=False)
    tags: dict = field(default_factory=default_tags)

    def __post_init__(self):
        self.add_instance(self.instance)

    def add_instance(self, instance: dir):
        self.instances.append(instance)

    def to_dict(self):
        instances = []
        for instance in self.instances:
            instance_dict = {}
            instance_dict["track_id"] = self.track_id
            instance_dict["object_class"] = self.object_class
            instance_dict.update(instance)
            instances.append(instance_dict)

        return instances

    def __getitem__(self, index):
        pass
