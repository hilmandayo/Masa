# from pymagextractor.models.annotations import Annotations
from pathlib import Path
from typing import Union

from Masa.core.utils import create_dirs


class DataID:
    """Handle the data acquisition from a certain Data ID."""
    def __init__(self, data_id: Union[str, Path]):
        self._data_id_dir = Path(data_id)
        dirs = []

        self._data_dir = self._data_id_dir / "data"
        dirs.append(self._data_dir)
        self._anns_dir = self._data_id_dir / "annotations"
        dirs.append(self._anns_dir)

        create_dirs(dirs)

    def set_and_get_annotations(self, name, annotations_setting):
        return Annotations(name, annotations_setting, self._anns_dir)

    @property
    def buffer(self):
        """Return path to video or file of images within the DataID."""
        try:
            # TODO: Make it possible to handle multiple separated sequential videos
            buffer = str(next(self._data_dir.glob("*.mp4")))
        except StopIteration:
             buffer = None
        return buffer
