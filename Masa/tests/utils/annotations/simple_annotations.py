"""Collections of mock annotations data for testing."""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Union, Tuple, Optional

import numpy as np


class DummyAnnotationsFactory:
    """A factory that returns certain mock annotations data."""
    @staticmethod
    def get_annotations(name, *args, **kwargs):
        if name == "simple_anno":
            return SimpleAnnotations(*args, **kwargs)

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
        return "track_id frame_id x1 y1 x2 y2 scene object view".split()

    @staticmethod
    def data(increase_track_id=None) -> List[List[Union[int, str]]]:
        """Output the data mocking the contents of a CSV file.

        Each column represents the data as defined in `head()`.
        """
        # TODO: Make it better
        retval =  [
            [0, 35, 10, 10, 20, 20, "road_scene", "red_traffic_light", "small"],
            [0, 37, 10, 10, 20, 20, "road_scene", "red_traffic_light", "middle"],
            [0, 33, 10, 10, 20, 20, "road_scene", "red_traffic_light", "large"],
            [1, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light", "far"],
            [2, 45, 10, 10, 20, 20, "road_scene", "red_traffic_light", "small"],
            [2, 48, 10, 10, 20, 20, "road_scene", "red_traffic_light", "middle"],
            [2, 50, 10, 10, 20, 20, "road_scene", "red_traffic_light", "large"],
            [3, 46, 10, 10, 20, 20, "road_scene", "red_traffic_light", "small"],
            [3, 33, 10, 10, 20, 20, "road_scene", "red_traffic_light", "middle"],
            [3, 48, 10, 10, 20, 20, "road_scene", "red_traffic_light", "large"],
            [4, 55, 10, 10, 20, 20, "road_scene", "red_traffic_light", "far"],
            [4, 58, 10, 10, 20, 20, "road_scene", "red_traffic_light", "far"],
            [5, 1, 10, 10, 20, 20, "road_scene", "red_traffic_light", "far"],
            [6, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light", "far"],
            [7, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light", "far"],
            [7, 44, 10, 10, 20, 20, "road_scene", "yellow_traffic_light", "far"],
            [8, 44, 10, 10, 20, 20, "road_scene", "green_traffic_light", "far"],
            ]

        if increase_track_id is not None:
            for r in retval:
                r[SimpleAnnotationsF.head().index("track_id")] += increase_track_id

        return retval

    @staticmethod
    # TODO: Correct return data format?
    def data_per_instance() -> List[List[List[Union[int, str]]]]:
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



# TODO: Make this as singleton
@dataclass
class SimpleAnnotations(DummyAnnotations):
    increase_track_id: Optional[int] = None
    _head: List[str] = field(init=False, default_factory=SimpleAnnotationsF.head)
    _data: List[Union[int, str]] = field(init=False)
    _data_per_instance: List[List[Union[int, str]]] = field(
        default_factory=SimpleAnnotationsF.data_per_instance
    )

    def __post_init__(self):
        # any better way??
        self._data = SimpleAnnotationsF.data(self.increase_track_id)

    def _get_data(self, per_instance=False):
        if per_instance:
            data = self._data_per_instance
        else:
            data = self._data

        return data

    @property
    def data(self):
        return self._get_data(per_instance=False)

    @property
    def data_per_instance(self):
        return self._get_data(per_instance=True)

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
