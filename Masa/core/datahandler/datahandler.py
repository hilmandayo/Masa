from dataclasses import dataclass, field
from pathlib import Path
from typing import Union
import csv

from .data import TrackObject


@dataclass
class DataHandler:
    """Represent the saved data.

    Data from buffer extraction process will be saved in some format (csv, xml,
    etc.). This class will (eventually) abstract and handle all of the data
    format. An instance of this class will represent one file/directory group
    of a particular data.

    Parameters
    ----------
    input_file
        Path to the data file.
    """
    input_file: Union[str, Path]
    tracked: dict = field(default_factory=dict)

    def __post_init__(self):
        self.input_file = Path(self.input_file)
        self._read_from_csv()

    def _read_from_csv(self):
        """Read data from CSV."""
        with self.input_file.open(mode="r") as f_csv:
            csv_reader = csv.DictReader(f_csv)
            line_count = 0
            for row in csv_reader:
                track_id = int(row["track_id"])
                instance = {"view": row["view"],
                            "x1": row["x1"], "y1": row["y1"],
                            "x2": row["x2"], "y2": row["y2"],}
                if self.tracked.get(track_id) is None:
                    self.tracked[track_id] = TrackObject(
                        track_id=track_id, object_class=row["object"],
                        instance=instance)
                else:
                    self.tracked[track_id].add_instance(instance)

    def __getitem__(self, index):
        return self.tracked[index]

    def add(self, tracked_object: Union[dict, TrackObject]):
        """Add an tracked object."""
        if isinstance(tracked_object, dict):
            Track
