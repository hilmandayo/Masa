"""Collections of mock annotations data for testing."""

from collections import defaultdict
from dataclasses import dataclass, field, InitVar
from pathlib import Path
from random import choice
from typing import List, Any, Union, Tuple, Optional, Dict

import numpy as np


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


class SimpleAnnotationsF:
    """A class that provide simple annotations data.

    This class acts as a wrapper that holds all data that will then be provided
    to `SimpleAnnotations` class (the `F` means factory).
    """
    @staticmethod
    def head() -> List[str]:
        """Output the keys of the data.

        This mocks the header of a CSV file.
        """
        return "track_id frame_id x1 y1 x2 y2 scene object".split()

    @staticmethod
    def data(increase_track_id=None) -> List[List[Union[int, str]]]:
        """Output the data mocking the contents of a CSV file.

        Each column represents the data as defined in `head()`.
        """
        # TODO: Make it better
        retval =  [
            [0, 35, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [0, 37, 33, 10, 48, 20, "road_scene", "red_traffic_light"],
            [0, 33, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [1, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light"],
            [2, 45, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [2, 48, 10, 10, 20, 36, "road_scene", "red_traffic_light"],
            [2, 50, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [3, 46, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [3, 33, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [3, 48, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [4, 55, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [4, 58, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [5, 1, 10, 10, 20, 20, "road_scene", "red_traffic_light"],
            [6, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light"],
            [7, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light"],
            [7, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light"],
            [8, 44, 10, 10, 20, 20, "road_scene", "green_traffic_light"],
            ]

        return retval

    @staticmethod
    # TODO: Correct return data format?
    def data_per_object_id() -> List[List[List[Union[int, str]]]]:
        """Returns list of data, but with each list is grouped as a same instance."""
        # TODO: Make it more robust in terms of csv head order
        if SimpleAnnotationsF.head()[0] != "track_id":
            raise ValueError(f"The first element of `head` is not `track_id`: "
                             f"{SimpleAnnotationsF.head()}")

        inter_data = defaultdict(list)
        for data in SimpleAnnotationsF.data():
            inter_data[data[0]].append(data)

        ret_data = []
        for k, v in inter_data.items():
            ret_data.append(v)

        return ret_data


@dataclass
class SimpleAnnotations(DummyAnnotations):
    increase_object_id: Optional[int] = None
    tags: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    _head: List[str] = field(init=False, default_factory=SimpleAnnotationsF.head)
    _data: List[Union[int, str]] = field(init=False)
    _data_per_object_id: List[List[Union[int, str]]] = field(
        default_factory=SimpleAnnotationsF.data_per_object_id
    )

    def __post_init__(self):
        # any better way??
        self._head += list(self.tags.keys())

        data = []
        for d in SimpleAnnotationsF.data():
            for values in self.tags.values():
                d.append(choice(values))
                d[self._head.index("track_id")] += self.increase_object_id
            data.append(d)
        self._data = data

    def _get_data(self, per_object_id=False):
        data = self._data

        if per_object_id:
            if self.head[0] != "track_id":
                raise ValueError(f"The first element of `head` is not `track_id`: "
                                f"{self.head}")

            inter_data = defaultdict(list)
            for d in data:
                inter_data[d[0]].append(d)

            data = []
            for k, v in inter_data.items():
                data.append(v)

        return data

    @property
    def data(self):
        return self._get_data(per_object_id=False)

    @property
    def data_per_object_id(self):
        return self._get_data(per_object_id=True)

    @property
    def head(self) -> List[str]:
        return self._head

    @property
    def data_str(self):
        data_str = ""
        data_str += f"{','.join(self.head)}\n"
        for data in self.data:
            data = [str(d) for d in data]
            data_str += f"{','.join(data)}\n"

        return data_str

    def create_file(self, empty_annotations_dir: Path,
                    file_name: str = "annotations.csv") -> Path:
        """Write data into the empty annotations directory.

        If the provided `file_name` in `empty_annotations_dir` is already
        created, it will be overwritten. This is to mock a file (mainly CSV)
        written on the disk.
        """
        data_file = empty_annotations_dir / file_name
        if data_file.exists(): data_file.unlink()

        with data_file.open("w") as f:
            f.write(self.data_str)

        return data_file

    @property
    def frameid_to_nframes_map(self) -> List[Tuple[int, int]]:
        """Return the number of frames for certain frame_id.

        The element of return value within a list will be in a form of
        `(frame_id, n_frame)`.
        """
        mapping = defaultdict(lambda: 0)
        h = self.head
        for data in self.data:
            mapping[data[h.index("frame_id")]] += 1

        return [(frame_id, n_frame) for frame_id, n_frame in mapping.items()]
