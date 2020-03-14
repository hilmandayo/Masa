from io import StringIO
from pathlib import Path
from typing import Union, List, Dict, Tuple
import csv

from PySide2 import QtCore as qtc

from Masa.core.data import TrackedObject, Instance
from Masa.core.data import FrameData


class DataHandler(qtc.QObject):
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
    added_tobj = qtc.Signal(TrackedObject)
    added_tobjs = qtc.Signal(list)
    added_instance = qtc.Signal(Instance)
    added_instances = qtc.Signal(list)  # list of instances
    deleted_tobj = qtc.Signal(tuple) # (tobj_idx, new_tobj_len)
    deleted_instance = qtc.Signal(tuple)  # (tobj_idx, instance_idx, new_instances_len))

    def __init__(self,
                 input_file: Union[str, Path] = None,
                 input_str: str = None):

        super().__init__()
        if not input_file and not input_str:
            raise ValueError(
                "Must pass input file or csv like string to DataHandler"
            )

        if input_file:
            self.input_file = Path(input_file)
        else:
            self.input_str = input_str
        self.tracked_objs: Dict[int, TrackedObject] = {}

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


    # CONT: track_id to object_id???
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
        return len(self.tracked_objs)

    def append(self, data: Union[TrackedObject, Instance, List[Instance]]):
        """Add an tracked_objs object."""
        if isinstance(data, TrackedObject) and len(data) == 1:
            data = data[0]
        if isinstance(data, Instance):
            self.tracked_objs[data.track_id].add_instance(data)
            self.added_instance.emit(data)
            return self

        if not (isinstance(data, TrackedObject) or
                isinstance(data, list)):
            raise ValueError(f"Wrong data type passed: {type(data)}")
        instances = []
        for instance in data:
            if not isinstance(instance, Instance):
                raise ValueError(
                    f"Element of `data` passed is of wrong type {type(instance)}"
                )
            self.tracked_objs[instance.track_id].add_instance(instance)
            instances.append(instance)
        self.added_instances.emit(instances)
        return self

    def delete(self, tobj_idx: int, instance_idx: int = None):
        if not isinstance(instance_idx, int):
            try:
                del self.tracked_objs[tobj_idx]
            except KeyError:
                raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")
            self._update_tracked_objs()
            self.deleted_tobj.emit((tobj_idx, len(self.tracked_objs)))
            return self

        try:
            self.tracked_objs[tobj_idx].delete(instance_idx)
        except KeyError:
            raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")
        except IndexError:
            raise ValueError(f"`instance_idx`={instance_idx} does not exist")
        self._update_tracked_objs()
        self.deleted_instance.emit(
            (tobj_idx, instance_idx, len(self.tracked_objs[tobj_idx]))
            )
        return self

    def _update_tracked_objs(self):
        """Make sure `self.tracked_objs` is always sorted with no missed number."""
        keys = list(self.tracked_objs.keys())
        sort_ok = all(keys[i] == keys[i + 1] for i in range(len(keys) - 1))

        old = self.tracked_objs
        self.tracked_objs = {}
        if not sort_ok:
            keys = list(range(len(keys)))
            for k, tobj in zip(keys, old.values()):
                self.tracked_objs.update({k: tobj.change_track_id(k)})
