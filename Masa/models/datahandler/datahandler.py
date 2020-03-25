from io import StringIO
from pathlib import Path
from typing import Union, List, Dict, Tuple
import csv

from PySide2 import QtCore as qtc

from Masa.core.data import TrackedObject, Instance
from Masa.core.utils import SignalPacket


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
    added_tobj = qtc.Signal(SignalPacket)  # data=TrackedObject
    added_tobjs = qtc.Signal(SignalPacket)  # data=list
    added_instance = qtc.Signal(SignalPacket)  #  data=Instance
    added_instances = qtc.Signal(SignalPacket)  # data=List[instance]
    deleted_tobj = qtc.Signal(SignalPacket) # data=Tuple[tobj_idx, new_tobj_len]
    deleted_instance = qtc.Signal(SignalPacket)  # data=Tuple[tobj_idx, instance_idx, new_instances_len]

    def __init__(self,
                 input_file: Union[str, Path] = None,
                 input_str: str = None,
                 name: str = "DataHandler"):

        super().__init__()
        if not input_file and not input_str:
            raise ValueError(
                "Must pass input file or csv like string to DataHandler"
            )

        self.name = name
        if input_file:
            self.input_file = Path(input_file)
        else:
            self.input_str = input_str
        self.tracked_objs: Dict[int, TrackedObject] = {}

        self._read_from_input()
        self._fixed_head = "track_id object_class".split()
        self._update_tracked_objs()

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


    def from_frame(self, frame_id, to: str = None) -> List[Instance]:
        ret = []
        for tobj in self.tracked_objs.values():
            ins = []
            for instance in tobj:
                if instance.frame_id == frame_id:
                    ins.append(instance)
            if ins:
                ret.extend(ins)

        # if to:
        #     if to.lower() == "frameinfo":
        #         ret = FrameData.from_instances(frame_id, ret)
        #     else:
        #         raise ValueError(f"Cannot understand of type {type(to)}")

        return ret

    def run_results_r(self, curr_results: SignalPacket):
        """Receive result from current index of session.

        Play mode???
        """
        curr_results: List[Instance] = curr_results.data
        try:
            curr_idx = curr_results[0].frame_id
        except IndexError:
            return

        # Sanity check.
        if not all([i.frame_id == curr_idx for i in curr_results]):
            raise Exception(f"Expecting `Instance` with {curr_idx} index, "
                            f"got {result.frame_id} instead")

        for result in curr_results:
            self.append(result)


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

    def add_tobj_r(self, packet: SignalPacket):
        tobj = packet.data[0]
        self.append(tobj)

    def append(self, data: Union[TrackedObject, Instance, List[Instance]]):
        """Add an tracked_objs object."""
        # TODO: Rename as add
        if (isinstance(data, TrackedObject) and
            data.track_id >= len(self.tracked_objs)):
                self._add_tobj(data)

        elif isinstance(data, Instance):
            self._add_instance(data)

        elif isinstance(data, list) or isinstance(data, TrackedObject):
            if len(data) == 1:
                self._add_instance(data[0])
            else:
                print("here")
                self._add_instances(data)

        else:
            raise ValueError(f"Data of typed {type(data)} is not supported.")

        return self


    def _add_instance(self, data, emit_signal=True):
        """Add `Instance` to an already created `TrackedObject`."""
        if data.track_id >= len(self.tracked_objs):
            raise Exception(f"Must instantiated the `TrackedObject` with "
                            f"`track_id`={data.track_id} first.")
        self.tracked_objs[data.track_id].add_instance(data)
        if emit_signal:
            self.added_instance.emit(
                SignalPacket(sender=self.name, data=data)
            )

    def _add_instances(self, data: List[Instance]):
        for d in data:
            if not isinstance(d, Instance):
                raise ValueError(f"Wrong data type passed: {type(data)}")
            self._add_instance(d, emit_signal=False)
        self.added_instances.emit(
            SignalPacket(sender=self.name, data=data)
        )

    def _add_tobj(self, tobj):
        self._update_tracked_objs()
        if len(tobj) != 1:
            raise Exception("Only can instantiated a `TrackedObject` with an `Instance`.")
        if tobj.track_id < len(self.tracked_objs):
            raise ValueError(f"`TrackedObject` with `track_id`={data.track_id} is already exist.")
        self._update_tracked_objs()

        if tobj.track_id != len(self.tracked_objs):
            raise Exception("Weird!")
        self.tracked_objs[tobj.track_id] = tobj
        self.added_tobj.emit(
            SignalPacket(sender=self.name, data=tobj)
        )


    def delete(self, tobj_idx: int, instance_idx: int = None):
        if not isinstance(instance_idx, int):
            try:
                del self.tracked_objs[tobj_idx]
            except KeyError:
                raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")
            self._update_tracked_objs()
            self.deleted_tobj.emit(
                SignalPacket(sender=self.name, data=(tobj_idx, len(self.tracked_objs)))
            )
            return self

        try:
            self.tracked_objs[tobj_idx].delete(instance_idx)
        except KeyError:
            raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")
        except IndexError:
            raise ValueError(f"`instance_idx`={instance_idx} does not exist")
        self._update_tracked_objs()
        self.deleted_instance.emit(
            SignalPacket(sender=self.name,
                         data=(tobj_idx, instance_idx, len(self.tracked_objs[tobj_idx])))
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
