import pytest
import uuid
from pathlib import Path

from PySide2 import QtCore as qtc


@pytest.fixture(name="dc_pathfile", autouse=True, scope="session")
def data_center_path_file(tmp_path_factory) -> qtc.QSettings:
    """Initialized needed settings and directories for the Data Center.

    Create and return `QSettings` object with initialized values.
    """
    # TODO: Make this works on Windows too!!!

    # A special directory mimicking `~`.
    masa_base = tmp_path_factory.mktemp("Masa")
    masa_dc = masa_base / "data_center"
    # By default, `qtc.QSettings` will handle where to write our information.
    # However, we make it simple by just setting it to `Masa/.config`.
    config = masa_base / ".config"

    settings = qtc.QSettings(str(config), qtc.QSettings.NativeFormat)
    settings.setValue("data_center", str(masa_dc))
    settings.sync()

    return settings


@pytest.fixture(name="dc_dir", scope="session")
def data_center_dir(dc_pathfile):
    """Create and return the `data_center` directory."""
    dc_key = "data_center"
    dc = Path(dc_pathfile.value(dc_key, "", type=str))
    dc.mkdir()

    (dc / "workspaces").mkdir()

    return dc


@pytest.fixture(name="ws_dir_factory", scope="session")
def workspace_dir_factory(dc_dir):
    def create_workspace(workspace):
        ws = dc_dir / "workspaces" / workspace
        ws.mkdir()
        return ws

    return create_workspace


@pytest.fixture(scope="session")
def default_workspace(ws_dir_factory):
    d_ws = ws_dir_factory("workspace_0")

    return d_ws


@pytest.fixture(scope="session")
def data_id_dir_factory(default_workspace):
    def make_data_id_dir(data_id_dir):
        d_id_dir = default_workspace / data_id_dir
        d_id_dir.mkdir()
        return d_id_dir
    return make_data_id_dir


@pytest.fixture(scope="function")
def empty_data_id_dir(data_id_dir_factory):
    # Probably because we modularize our conftest, sometimes, we got
    # already exists error.
    d_id = data_id_dir_factory(str(uuid.uuid4()))

    return d_id


@pytest.fixture(scope="function")
def empty_data_dir(empty_data_id_dir):
    """Create and return the `data` dir."""
    data_dir = empty_data_id_dir / "data"
    data_dir.mkdir()

    return data_dir


@pytest.fixture(scope="function")
def empty_annotations_dir(empty_data_id_dir):
    """Create the annotations dir within the Data ID."""
    ann = empty_data_id_dir / "annotations"
    ann.mkdir()

    return ann


