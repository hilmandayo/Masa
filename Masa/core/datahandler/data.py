from dataclasses import dataclass
from typing import ClassVar, List


@dataclass
class TrackObject:
    """Represents a single tracked object.

    A single object might have multiple instances.
    """
    track_id: int
    object_class: str
    instances: dict
    tags: dict = {"view": ["small", "middle", "large"]}
