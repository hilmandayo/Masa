from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, List, Dict
import csv

from .data import TrackedObject


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
    tracked_objs: Dict[int, TrackedObject] = field(default_factory=dict)
    _fixed_head: List[str] = field(init=False)

    def __post_init__(self):
        self.input_file = Path(self.input_file)
        self._fixed_head = "track_id object_class".split()
        self._read_from_csv()

    def _read_from_csv(self):
        """Read data from CSV."""
        with self.input_file.open(mode="r") as f_csv:
            csv_reader = csv.DictReader(f_csv)
            line_count = 0
            for instance in csv_reader:
                track_id = int(instance.pop("track_id"))
                object_class = instance.pop("object")  # TEMP: Repair this
                if self.tracked_objs.get(track_id) is None:
                    self.tracked_objs[track_id] = TrackedObject(
                        track_id=track_id, object_class=object_class,
                        instance=instance)
                else:
                    self.tracked_objs[track_id].add_instance(instance)

    def __getitem__(self, index):
        return self.tracked_objs[index]

    def __iter__(self):
        self._iter = iter(self.tracked_objs)
        self._iter_idx = None
        return self

    def __next__(self):
        try:
            next_key = next(self._iter)
        except StopIteration:
            raise StopIteration()

        next_val = self.tracked_objs[next_key]
        if self._iter_idx is None:
            self._iter_idx = 0
        else:
            self._iter_idx += 1

        return next_val

    def __len__(self):
        return len(self.instances)

    def add(self, tracked_obj: Union[dict, TrackedObject]):
        """Add an tracked_objs object."""
        if isinstance(tracked_obj, dict):
            # Track
            pass

    def _update_tracked_objs(self):
        """Make sure `self.tracked_objs` is always sorted with no missed number."""
        keys = list(self.tracked_objs.keys())
        sort_ok = all(keys[i] == keys[i + 1] for i in range(len(keys) - 1))
        if not sort_ok:
            keys = list(range(len(keys)))
            for k, tobj in zip(keys, self.tracked_objs):
                tobj.change_track_id(k)

        self.tracked_objs = {key: tobj for key, tobj in self.tracked_objs.items()}
