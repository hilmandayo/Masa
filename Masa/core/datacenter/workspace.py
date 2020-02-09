from Masa.core.utils import create_dirs
from .dataid import DataID
from pathlib import Path
import toml


class WorkSpace:
    def __init__(self, workspace, annotations):
        self._workspace_dir = Path(workspace)
        self._anns_file_path = annotations
        # TODO: Make this better
        assert self._workspace_dir.exists()

    def __getitem__(self, data_id):
        d = dict([(i.name, i) for i in self._workspace_dir.iterdir()])
        if data_id in d.keys():
            return DataID(str(d[data_id]))
        else:
            # TODO: make this better
            raise ValueError

    @property
    def data_ids(self):
        return list(i.name for i in self._workspace_dir.iterdir())

    def new_data_id(self, data_id):
        d = self._workspace_dir / data_id
        create_dirs(d)
        return DataID(str(d))

    @property
    def workspace(self):
        return self._workspace_dir.name

    # TODO: implement appropriate annotations stuff here
    def anns_settings_get(self, name=None):
        try:
            with open(self._anns_file_path) as f:
                anns =  toml.load(f)
        except FileNotFoundError:
                return None

        if name is None:
            return anns
        elif isinstance(name, str):
            return anns.get(name, None)
        else:
            return None

    def anns_settings_update(self, name, annotations_setting):
        with open(self._anns_file_path) as f:
                anns =  toml.load(f)
                anns[name] = annotations_setting
        with open(self._anns_file_path, "w") as f:
                toml.dump(anns, f)


    @property
    def anns_settings_list(self):
        return [i for i in self.anns_settings_get().keys()]
