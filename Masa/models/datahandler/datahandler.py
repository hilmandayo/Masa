from io import StringIO
from pathlib import Path
from typing import Union, List, Dict, Tuple
import csv

from PySide2 import QtCore as qtc

from Masa.core.data import TrackedObject, Instance
from Masa.core.utils import SignalPacket, DataUpdateInfo, FrameData


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
    data_updated = qtc.Signal(SignalPacket)
    pass_data = qtc.Signal(SignalPacket)
    curr_frame_data = qtc.Signal(SignalPacket)

    def __init__(self,
                 input_file: Union[str, Path] = None,
                 input_str: str = None,
                 name: str = "DataHandler"):

        super().__init__()
        if not input_file and not input_str:
            raise ValueError(
                "Must pass input file or csv like string to DataHandler"
            )

        self.input_file = input_file
        self.input_str = input_str
        if input_file:
            self.input_file = Path(input_file)
        else:
            self.input_str = input_str
        self.tracked_objs: Dict[int, TrackedObject] = {}

        self._read_from_input()
        self._fixed_head = "track_id object_class".split()
        self._update()

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
                tags = {}
                new_instance: dict = {}
                track_id = int(instance.pop("track_id"))
                object_class = instance.pop("object")  # TEMP: Repair this
                for key in to_number:
                    if key == "frame_id":
                        new_instance[key] = int(float(instance.pop("frame_id")))
                    else:
                        # the numbers could be of type `int` of `float`
                        try:
                            val = instance.pop(key)
                            new_instance[key] = int(val)
                        except ValueError:
                            try:
                                new_instance[key] = float(val)
                            except ValueError as v:
                                raise v(f"Cannot convert data of key {key}"
                                        "to `int` of `float`.")
                # tags
                for tag, val in instance.items():
                    tags[tag] = val
                new_instance["tags"] = tags
                
                if self.tracked_objs.get(track_id) is None:
                    # TODO: Should we use the internal methods?
                    self.tracked_objs[track_id] = TrackedObject(
                        track_id=track_id, object_class=object_class,
                        instance=new_instance)
                else:
                    self.tracked_objs[track_id].add_instance(new_instance, update=False)

            # For possibly performance purpose
            for tracked_obj in self.tracked_objs.values():
                tracked_obj._update()
        finally:
            if self.input_file:
                f_csv.close()

    def __getitem__(self, index):
        return list(self.tracked_objs.values())[index]

    def get_instance_sl(self, packet: SignalPacket):
        d = packet.data
        instance = self.tracked_objs[d[0]][d[1]]
        self.pass_instance.emit(
            SignalPacket(sender=self.__class__.__name__, data=d)
        )

    def __iter__(self):
        self._iter = iter(self.tracked_objs)
        self._iter_idx = None
        return self

    @property
    def instances(self):
        return [instance
                for t_obj in self[:] 
                for instance in t_obj[:]]

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

    def from_frame(self, frame_id, to: str = None) -> List[Instance]:
        ret = []
        for tobj in self.tracked_objs.values():
            ins = []
            for instance in tobj:
                if instance.frame_id == frame_id:
                    ins.append(instance)
            if ins:
                ret.extend(ins)

        return ret

    def data_handler_sl(self, packet: SignalPacket):
        dui: DataUpdateInfo = packet.data

        # We just consider for an Instance object to
        # other Instance or new TrackedObject
        if dui.add:
            self._add_instance(dui.add)
        elif dui.delete:
            pos: Tuple[int, int] = dui.delete
            self._delete_instance(*pos) # TODO: How to delete object??
        elif dui.edit:
            old_pos, new_obj = dui.edit
            self._edit(old_pos, new_obj)
            

        self._update()

    def run_sresults_sl(self, curr_sresults: SignalPacket):
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


    def _edit(self, pos: Tuple[int, int], new_obj: Union[Instance, TrackedObject]):
        self._delete_instance(*pos, emit_signal=False)
        if isinstance(new_obj, TrackedObject):
            self._add_tobj(new_obj, emit_signal=False)
        elif isinstance(new_obj, Instance):
            self._add_instance(new_instance, emit_signal=False)
        else:
            raise ValueError(f"Do not support data of type {type(new_obj)}")

        # self.edited_instance.emit(
        #     SignalPacket(sender=self.__class__.__name__, data=(pos, new_obj))
        # )
        dui = DataUpdateInfo(edit=(pos, new_obj))
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

        return self

    def get_data_sl(self, packet: SignalPacket):
        data = self.get_data(*packet.data)
        self.pass_data.emit(
            SignalPacket(sender=self.__class__.__name__, data=data)
        )

    def get_data(self, track_id, instance_id):
        return self[track_id][instance_id]
        

    def add(self, data: Union[TrackedObject, Instance, List[Instance]]):
        """Add data.

        The passed data should already have `track_id` and `object_id` set
        beforehand.
        """
        if (isinstance(data, TrackedObject) and len(data) == 1):
                self._add_tobj(data)

        elif isinstance(data, Instance):
            self._add_instance(data)

        # elif isinstance(data, list) or isinstance(data, TrackedObject):
        #     if len(data) == 1:
        #         self._add_instance(data[0])
        #     else:
        #         self._add_instances(data)

        else:
            raise ValueError(f"Data of type {type(data)} "
                             f"with len of {len(data)}is not supported.")

        dui = DataUpdateInfo(added=data)
        self.data_updated.emit(SignalPacket(sender=self.__class__.__name__, data=dui))

        return self

    def move(self, old_pos, obj: Union[TrackedObject, Instance]):
        self._delete_instance(*old_pos)
        if isinstance(obj, TrackedObject):
            self._add_tobj(obj)
        else:
            self._add_instance(obj)

        dui = DataUpdateInfo(moved=(old_pos, obj))
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )
        

    def replace(self, instance):
        self._replace(instance)

        dui = DataUpdateInfo(replaced=instance)
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

    def _replace(self, instance):
        self._replace_instance(instance)

    def _replace_instance(self, instance):
        self._delete_instance(instance.track_id, instance.instance_id)
        self._add_instance(instance)

    def _add_instance(self, instance):
        """Add `Instance` to an already created `TrackedObject`."""
        if instance.track_id >= len(self.tracked_objs):
            raise Exception(f"Must instantiated the `TrackedObject` with "
                            f"`track_id`={instance.track_id} first.")
        # The `append`, `insert` and how it is updated is handled by the
        # `TrackedObject` class.
        self.tracked_objs[instance.track_id].add_instance(instance)

    # def _add_instances(self, data: List[Instance], emit_signal=True):
    #     for d in data:
    #         if not isinstance(d, Instance):
    #             raise ValueError(f"Wrong data type passed: {type(data)}")
    #         self._add_instance(d, emit_signal=False)
    #     if emit_signal:
    #         # self.added_instances.emit(
    #         #     SignalPacket(sender=self.__class__.__name__, data=data)
    #         # )
    #         dui = DataUpdateInfo(added=data)
    #         self.data_updated.emit(
    #             SignalPacket(sender=self.__class__.__name__, data=dui)
    #         )

    def _add_tobj(self, tobj):
        if len(tobj) != 1:
            raise Exception("Only can instantiated a `TrackedObject` with an `Instance`.")

        if tobj.track_id > len(self):
            tobj.change_track_id(len(self))
        if tobj.track_id == len(self):
            self._append_tobj(tobj)
        else:
            self._insert_tobj(tobj)

    def _append_tobj(self, tobj):
        self.tracked_objs[tobj.track_id] = tobj

    def _insert_tobj(self, tobj):
        old_tobjs = self.tracked_objs
        keep_keys = list(range(tobj.track_id))
        keep_tobjs = {k: old_tobjs[k] for k in keep_keys}

        self.tracked_objs = {}
        self.tracked_objs.update(keep_tobjs)
        self.tracked_objs[tobj.track_id] = tobj
        self.tracked_objs.update(
            {k + 1: old_tobjs[k].change_track_id(k + 1)
             for k in range(tobj.track_id, len(old_tobjs))}
        )
        

    def delete(self, tobj_idx: int, instance_idx: int = None):
        self._delete(tobj_idx, instance_idx)

        dui = DataUpdateInfo(deleted=(tobj_idx, instance_idx))
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

        return self

    def _delete(self, tobj_idx: int, instance_idx: int = None):
        if not isinstance(instance_idx, int):
            if tobj_idx == len(self):
                self._delete_tobj_end(tobj_idx)
            else:
                self._delete_tobj(tobj_idx)
        else:
            self._delete_instance(tobj_idx, instance_idx)
        

    def _delete_tobj_end(self, tobj_idx: int):
            try:
                del self.tracked_objs[tobj_idx]
            except KeyError:
                raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")

    def _delete_tobj(self, tobj_idx: int, update=True):
            try:
                del self.tracked_objs[tobj_idx]
            except KeyError:
                raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")

            if update:
                self._update(keep_until=tobj_idx - 1)

    def _delete_instance(self, tobj_idx: int, instance_idx: int, update=True):
            try:
                self.tracked_objs[tobj_idx].delete(instance_idx, update)
            except KeyError:
                raise ValueError(f"`tobj_idx`={tobj_idx} does not exist")
            except IndexError:
                raise ValueError(f"`instance_idx`={instance_idx} does not exist")
        
    def _update(self, keep_until=None):
        """Make sure `self.tracked_objs` is always sorted with no missed number.

        Can be only used with `*delete` method.
        """
        # TODO: Make it better. And how about put it inside *insert method?
        old_tobjs = self.tracked_objs
        old_keys = list(old_tobjs.keys())
        if isinstance(keep_until, int):
            # TODO: Ensure the index until `keep_until` is also sorted
            keep_keys = list(range(keep_until + 1))
            keep_tobjs = {k: old_tobjs[k] for k in keep_keys}
            old_tobjs = {k: old_tobjs[k] for k in list(old_tobjs.keys())
                         if k not in keep_tobjs}
            sort_ok = False
        else:
            keep_until = -1
            keep_tobjs = {}
            sort_ok = all(old_keys[i] == old_keys[i + 1] for i in range(len(old_keys) - 1))

        if not sort_ok:
            self.tracked_objs = {}
            self.tracked_objs.update(keep_tobjs)
            for new_k, tobj in enumerate(old_tobjs.values(), keep_until + 1):
                self.tracked_objs[new_k] = tobj.change_track_id(new_k)

    def propogate_curr_frame_data_sl(self, packet: SignalPacket):
        # TODO: check the best way to pass ndarray
        frame, index = packet.data
        framedata = FrameData(frame, index, self.from_frame(index))
        self.curr_frame_data.emit(
            SignalPacket(sender=self.__class__.__name__, data=framedata)
        )
