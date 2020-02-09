from pathlib import Path
from typing import Union
import datetime

import toml
import cv2

from .workspace import WorkSpace
from Masa.core.utils import create_dirs


class DataCenter:
    """Represents the Data Center of Masa.

    Almost every data will directly go to the data center. This class will
    handle the directories structure of the Data Center. User can get the
    Workspace through this class.
    """

    def __init__(self, data_base_path: Union[str, Path]):
        """Constructor."""
        dirs = []
        self._db_dir = Path(data_base_path)
        dirs.append(self._db_dir)

        self._workspaces_dir = self._db_dir / "workspaces"
        dirs.append(self._workspaces_dir)

        self._settings_dir = self._db_dir / "settings"
        dirs.append(self._settings_dir)

        self._settings_anns_dir = self._settings_dir / "workspaces_annotations"
        dirs.append(self._settings_anns_dir)

        # self.get_db_information(is_debug = True)
        # self.db_info = None
        create_dirs(dirs)

    def __len__(self):
        return len(list(db._workspaces_dir.iterdir()))

    @property
    def workspaces(self):
        return list(i.name for i in self._workspaces_dir.iterdir())

    def __getitem__(self, workspace):
        d = dict([(i.name, i) for i in self._workspaces_dir.iterdir()])
        if workspace in d.keys():
            return WorkSpace(
                str(d[workspace]), str(self._settings_anns_dir / f"{workspace}.toml")
                )
        else:
            # TODO: make this better
            raise ValueError

    def new_workspace(self, name: str):
        ws = self._workspaces_dir / name
        create_dirs(ws)

        ws_anns = self._settings_anns_dir / (name + ".toml")
        ws_anns.write_text("")

        self.db_info['workspaces'].append(name)
        return WorkSpace(str(ws), str(ws_anns))

    def get_db_information(self, is_debug = True):
        '''
        If the database is already exist, the function will try to retrieve its information.
        If the information of the database does not exist, a new information file will be written.
        '''
        db_info_file = self._db_dir / 'db_info.toml'

        if db_info_file.is_file():
            print('db information found')
            self.db_info = toml.load(open(db_info_file))
            self.db_info['workspaces'] = self.is_ws_dir_exist()
            self.db_info['date']['modified'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            toml.dump(self.db_info, open(db_info_file, mode='w'))
        else:
            print('db file not found')
            self.db_info = {'path':str(self._db_dir),
                       'date':{'created' :datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                               'modified':datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')},
                       'workspaces':self.is_ws_dir_exist(),
                       'last_opened_workspace':[]}
            toml.dump(self.db_info, open(db_info_file, mode='w'))

        if is_debug:
            print(self.db_info)

    def is_ws_dir_exist(self):
        '''
        refreshes the workspace list everytime database is called.
        '''
        return [f.name for f in self._workspaces_dir.iterdir() if f.is_dir()]


#     def _create_annotation_setting(self):
#         # TODO: repair this
#         if self._ann_setting is None:
#             raise RuntimeError

#         for key, values in self._ann_setting.items():
#             pd = self._ann_dir / key
#             pd.mkdir(exist_ok=True)
#             # TODO: Improve this (csv head)
#             for v in values.keys():
#                 d = pd / f"{v}"
#                 f = pd / f"{v}.csv"

#                 d.mkdir(exist_ok=True)
#                 if not f.exists():
#                     f.write_text("")

#     def save(self, image, index: list, meta=None):
#         i1, i2 = index
#         d = self._ann_dir / i1 / i2
#         image_name = str(d / f"{str(self._ann_setting[i1][i2])}.jpg")
#         cv2.imwrite(image_name, image)

#         self._ann_setting[i1][i2] += 1
