from pathlib import Path
from typing import Union


def create_dirs(dirs: Union[list, str]):
    """An utility to create directories.

    Raises
    ------
    TypeError
        If the passed directories are not of type `str` or `pathlib.Path`.
    """
    if isinstance(dirs, str):
        dirs = [dirs]

    _dirs = []
    for d in dirs:
        if isinstance(d, str):
            d = Path(d)
        elif isinstance(d, Path):
            pass
        else:
            raise TypeError(f"Cannot deal with type {type(d)}")
        _dirs.append(d)

    for d in _dirs:
        d.mkdir(exist_ok=True)

def delete_dirs(dirs: Union[list, str]):
    """An utility to delete directories."""
    pass
