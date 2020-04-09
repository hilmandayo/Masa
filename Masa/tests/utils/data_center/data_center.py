from pathlib import Path
from typing import Union, Optional


class DataCenterUtility:
    __shared_state = {}
    def __init__(self, root: Optional[str, Path]):
        self.__dict__ = self.__shared_state

        if not self.__dict__.get("root"):
            if root is None:
                raise ValueError(f"Must pass a path to first instance of `DataCenterUtility`")
            self.root = root

    def data_center(self, data_center: Optional[str, Path] = "data_center"):
        data_center = self.root / data_center
        data_center.mkdir()

        return data_center

        
