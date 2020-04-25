from collections import defaultdict
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Union, List, Dict, Tuple
import csv

from PySide2 import QtCore as qtc

from Masa.core.data import TrackedObject, Instance
from Masa.core.utils import SignalPacket, DataUpdateInfo, FrameData, DataInfo


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
    pass_datainfo = qtc.Signal(SignalPacket)
    curr_frame_data = qtc.Signal(SignalPacket)
    print_data = qtc.Signal(SignalPacket)

    def __init__(self, input_file: Union[str, Path] = None, input_str: str = None,
                 backup_file: int = 3, autosave_step: int = 5):
        super().__init__()
        if not input_file and not input_str:
            raise ValueError(
                "Must pass input file or csv like string to DataHandler"
            )

        self.input_file = input_file
        self.input_meta = input_file.parent / f".meta_{input_file.stem}"
        self.input_str = input_str
        self.backup_file = backup_file
        self.autosave_step = autosave_step
        self.change_count = 0
        if input_file:
            self.input_file = Path(input_file)
        else:
            self.input_str = input_str
        self.tracked_objs: Dict[int, TrackedObject] = {}

        self._read_meta()
        self._read_from_input()
        self._fixed_head = "track_id object_class".split()
        self._update()

    def _read_meta(self):
        if not self.input_meta.exists():
            raise ValueError(f"Cannot find meta file {self.input_meta}")

        meta = qtc.QSettings(str(self.input_meta), qtc.QSettings.NativeFormat)
        obj_cls_key = "object_classes"
        scene_key = "scene"

        self.scene = meta.value(scene_key)
        self.all_object_classes = meta.value(obj_cls_key)
        self.all_tags = {}
        for key in meta.allKeys():
            if key not in [obj_cls_key, scene_key]:
                self.all_tags[key] = meta.value(key)

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
                new_instance: dict = {}
                track_id = int(instance.pop("track_id"))
                object_class = instance.pop("object_class")  # TEMP: Repair this
                if object_class not in self.object_classes:
                    raise ValueError(f"Class of {object_class} is not valid.")
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

                # XXX: Forcing the tags...
                tags = {}
                for key in self.all_tags:
                    val = instance[key]
                    if val in self.all_tags[key]:
                        tags[key] = val
                    else:
                        raise ValueError(f"Problem with tags of key: {key}, val: {val}")
                new_instance["tags"] = tags

                # for tag, val in instance.items():
                #     tags[tag] = val
                # new_instance["tags"] = tags
                
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
        return self.all_object_classes
        # return list(set(t_obj.object_class for t_obj in self.tracked_objs.values()))

    @property
    def object_class_mapping(self):
        # obj_cls_map = defaultdict(list)
        obj_cls_map = {obj_cls: [] for obj_cls in self.object_classes}
        for tobj in self.tracked_objs.values():
            obj_cls_map[tobj.object_class].append(tobj.track_id)

        return obj_cls_map

    @property
    def tags(self):
        if self.all_tags:
            return self.all_tags

        # tags = defaultdict(set)
        # for tobj in self:
        #     for tag, values in tobj.tags.items():
        #         tags[tag] |= set(values)

        # return {tag: list(vals) for tag, vals in tags.items()}

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

    def data_update_sl(self, packet: SignalPacket):
        dui: DataUpdateInfo = packet.data

        # We just consider for an Instance object to
        # other Instance or new TrackedObject
        if dui.added:
            self.add(dui.added)

        elif dui.deleted:
            pos: Tuple[int, int] = dui.deleted
            self.delete(*pos) # TODO: How to delete object??
        elif dui.replaced:
            self.replace(dui.replaced)
        elif dui.moved:
            self.move(*dui.moved)
            

        self._update()
        try:
            # Assuming every data added and deleted is through this function,
            # this will make sure our viewport is also updated.
            framedata = FrameData(self.curr_frame, self.curr_index, self.from_frame(self.curr_index))
            self.curr_frame_data.emit(
                SignalPacket(sender=[*packet.sender, self.__class__.__name__],
                             data=framedata)
            )
        except NameError:
            # Haven't even started the buffer yet...
            pass
        # TODO: This determines autosave feature.
        #       However, only valid on change based on slot. Make it better.

        self.change_count += 1
        if self.change_count >= self.autosave_step:
            self.save()
            self.change_count = 0

        self.print_data.emit(
            SignalPacket(sender=[self.__class__.__name__], data=self.__str__())
        )

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

    def get_datainfo_sl(self, packet: SignalPacket):
        data = self.get_datainfo(*packet.data)
        packet.sender.append(self.__class__.__name__)
        self.pass_datainfo.emit(
            SignalPacket(sender=packet.sender, data=data)
        )

    def get_datainfo(self, track_id=None, instance_id=None):
        if track_id is None and instance_id is None:
            instance = None
        else:
            instance = self[track_id][instance_id]

        di = DataInfo(
            instance=instance,
            obj_classes=self.object_class_mapping,
            tags=self.tags
        )

        return di
        

    def add(self, data: Union[TrackedObject, Instance, List[Instance]]):
        """Add data.

        The passed data should already have `track_id` and `object_id` set
        beforehand.
        """
        if (isinstance(data, TrackedObject) and len(data) == 1):
                self._add_tobj(data)

        elif isinstance(data, Instance):
            self._add_instance(data)

        else:
            raise ValueError(f"Data of type {type(data)} "
                             f"with len of {len(data)}is not supported.")

        dui = DataUpdateInfo(added=data)
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

        return self

    def move(self, old_pos, obj: Union[TrackedObject, Instance]):
        prev_len = len(self)
        self._delete_instance(*old_pos)

        # TODO: There must be a better way...
        if old_pos[0] <= obj.track_id and prev_len == len(self) + 1:
            try:
                obj.change_track_id(obj.track_id - 1)
            except AttributeError:
                obj.track_id -= 1

        if isinstance(obj, TrackedObject):
            self._add_tobj(obj)
        else:
            self._add_instance(obj)

        dui = DataUpdateInfo(moved=(old_pos, obj))
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

    def __str__(self):
        ret = f"DataHandler {str(self.input_file)}\n"
        for tobj in self:
            ret += f"\tTrackedObject ({tobj.track_id}, {tobj.object_class})\n"
            for ins in tobj:
                ret += f"\t\tInstance {ins.instance_id}:  "
                tags = ""
                for key, value in ins.tags.items():
                    tags += f"{key}: {value}, "
                ret += f"({tags.strip()[:-1]})\n"

        return ret.strip()
        
    def replace(self, instance: Union[Instance, dict]):
        if isinstance(instance, dict):
            pos = ["track_id", "instance_id"]
            t_id, ins_id = instance[pos[0]], instance[pos[1]]
            new = deepcopy(self[t_id][ins_id])
            for key in instance:
                if key not in pos:
                    setattr(new, key, instance[key])
            instance = new

        self._replace(instance)

        dui = DataUpdateInfo(replaced=instance)
        self.data_updated.emit(
            SignalPacket(sender=self.__class__.__name__, data=dui)
        )

    def _replace(self, instance):
        self._replace_instance(instance)

    def _replace_instance(self, instance):
        self._delete_instance(instance.track_id, instance.instance_id, update=False)
        self._add_instance(instance)

    def _add_instance(self, instance):
        """Add `Instance` to an already created `TrackedObject`."""
        if instance.track_id >= len(self.tracked_objs):
            raise Exception(f"Must instantiated the `TrackedObject` with "
                            f"`track_id`={instance.track_id} first.")
        # The `append`, `insert` and how it is updated is handled by the
        # `TrackedObject` class.
        self.tracked_objs[instance.track_id].add_instance(instance)

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

        self.tracked_objs = keep_tobjs
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
            if update:
                if len(self.tracked_objs[tobj_idx]) == 0:
                    self._delete(tobj_idx)
        
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

    def save(self):
        # Backup file. ########################################################
        for i in range(self.backup_file - 1, 0, -1):
            b_file = self.input_file.parent / f".#{self.input_file.name}{i - 1}"
            if b_file.exists():
                b_file.rename(self.input_file.parent / f".#{self.input_file.name}{i}")
        i = 0
        (self.input_file.parent / f".#{self.input_file.name}{i}").write_text(
            self.input_file.read_text()
        )

        # Write current data. #################################################
        self.input_file.write_text(self._data_as_text())


    def _data_as_text(self):
        header = [
        "frame_id", "track_id", "x1", "y1", "x2", "y2", "scene",
        "object_class", *list(self.all_tags.keys())
        ]

        data = ",".join(header) + "\n"
        for tobj in self:
            for ins in tobj:
                tags = ",".join([ins.tags[tag] for tag in self.all_tags.keys()])
                data += (f"{ins.track_id},{ins.frame_id},"
                         f"{ins.x1},{ins.y1},{ins.x2},"
                         f"{ins.y2},{self.scene},{ins.object_class},{tags}"
                         "\n")

        return data[:-1]

    def propogate_curr_frame_data_sl(self, packet: SignalPacket):
        # TODO: check the best way to pass  ndarray
        self.curr_frame, self.curr_index = packet.data
        framedata = FrameData(self.curr_frame, self.curr_index, self.from_frame(self.curr_index))
        self.curr_frame_data.emit(
            SignalPacket(sender=self.__class__.__name__, data=framedata)
        )
