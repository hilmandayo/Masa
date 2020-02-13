"""Collections of mock annotations data for testing."""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Union

import numpy as np


class DummyAnnotationsFactory:
    @staticmethod
    def get_annotations(name):
        if name == "simple_anno":
            return SimpleAnnotations()

@dataclass
class DummyAnnotations:
    """A parent class that every annotations test data class should inherit.

    In this context, `head` will always means the metadata of the data,
    `data` will always means the actual data that corresponds to the `head` and
    annotations will mean the `head` and `data` combined.
    """

class SimpleAnnotationsF:
    @staticmethod
    def data():
        return [
            [0, 31, 500, 176, 564, 206, "road_scene", "red_traffic_light", "small"],
            [0, 35, 558, 118, 638, 158, "road_scene", "red_traffic_light", "middle"],
            [0, 37, 854, 200, 918, 230, "road_scene", "red_traffic_light", "large"],
            [1, 44, 738, 274, 778, 302, "road_scene", "yellow_traffic_light", "far"],
            [2, 45, 622, 240, 662, 258, "road_scene", "red_traffic_light", "small"],
            [2, 48, 760, 268, 830, 300, "road_scene", "red_traffic_light", "middle"],
            [2, 50, 714, 170, 792, 208, "road_scene", "red_traffic_light", "large"],
            [3, 46, 758, 380, 796, 404, "road_scene", "red_traffic_light", "small"],
            [3, 47, 1010, 288, 1060, 314, "road_scene", "red_traffic_light", "middle"],
            [3, 48, 388, 246, 450, 282, "road_scene", "red_traffic_light", "large"],
            [4, 55, 678, 372, 708, 384, "road_scene", "red_traffic_light", "far"],
            [4, 58, 560, 354, 602, 384, "road_scene", "red_traffic_light", "far"],
            [5, 70, 834, 338, 888, 372, "road_scene", "red_traffic_light", "far"],
            ]

    @staticmethod
    def head():
        return "track_id frame_id x1 y1 x2 y2 scene object view".split()

    @staticmethod
    def data_per_instance():
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
    _head: List[str] = field(default_factory=SimpleAnnotationsF.head)
    _data: List[Union[int, str]] = field(default_factory=SimpleAnnotationsF.data)
    _data_per_instance: List[List[Union[int, str]]] = field(
        default_factory=SimpleAnnotationsF.data_per_instance
    )

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

    def create_file(self, empty_annotations_dir: Path,
                    file_name: str = "annotations.csv") -> Path:
        """Create the data into the empty annotations directory"""
        data_file = empty_annotations_dir / file_name
        if data_file.exists(): data_file.unlink()

        with data_file.open("a") as f:
            f.write(f"{','.join(self.head)}\n")
            for data in self.data:
                data = [str(d) for d in data]
                f.write(f"{','.join(data)}\n")

        return data_file
