from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Union, List, Dict, Tuple
import csv

from .data import TrackedObject
from .data_wrapper import FrameData


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
    input_file: Union[str, Path] = None
    input_str: str = None
    tracked_objs: Dict[int, TrackedObject] = field(init=False, default_factory=dict)
    _fixed_head: Tuple[str] = field(init=False, default=("dummy",))

    def __post_init__(self):
        if not self.input_file and not self.input_str:
            raise ValueError("Must pass input file or csv like string to DataHandler")

        if self.input_file:
            self.input_file = Path(self.input_file)
        self._read_from_input()
        self._fixed_head = "track_id object_class".split()

    def _read_from_input(self):
        """Read data from CSV."""
        to_number = ["x1", "x2", "y1", "y2", "frame_id"]
        try:
            if self.input_file:
                f_csv = self.input_file.open(mode="r")
            else:
                f_csv = StringIO(self.input_str)

            print(f_csv)
            csv_reader = csv.DictReader(f_csv)
            line_count = 0
            for instance in csv_reader:
                track_id = int(instance.pop("track_id"))
                object_class = instance.pop("object")  # TEMP: Repair this
                for key in to_number:
                    if key == "frame_id":
                        instance[key] = int(float(instance["frame_id"]))
                    else:
                        # the numbers could be of type `int` of `float`
                        try:
                            instance[key] = int(instance[key])
                        except ValueError:
                            try:
                                instance[key] = float(instance[key])
                            except ValueError as v:
                                raise v(f"Cannot convert data of key {key}"
                                        "to `int` of `float`.")
                if self.tracked_objs.get(track_id) is None:
                    self.tracked_objs[track_id] = TrackedObject(
                        track_id=track_id, object_class=object_class,
                        instance=instance)
                else:
                    self.tracked_objs[track_id].add_instance(instance)
        finally:
            if self.input_file:
                f_csv.close()

    def __getitem__(self, index):
        return self.tracked_objs[index]

    def __iter__(self):
        self._iter = iter(self.tracked_objs)
        self._iter_idx = None
        return self

    @property
    def frames(self):
        frames = set()
        for tobj in self.tracked_objs.values():
            for instance in tobj:
                frames.add(instance.frame_id)
        return sorted(list(frames))


    @property
    def object_classes(self):
        return list(set(t_obj.object_class for t_obj in self.tracked_objs.values()))


    def from_frame(self, frame_id, to: str = None):
        ret = []
        for tobj in self.tracked_objs.values():
            ins = []
            for instance in tobj:
                if instance.frame_id == frame_id:
                    ins.append(instance)
            if ins:
                ret.extend(ins)

        if to:
            if to.lower() == "frameinfo":
                ret = FrameData.from_instances(frame_id, ret)
            else:
                raise ValueError(f"Cannot understand of type {type(to)}")

        return ret

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
