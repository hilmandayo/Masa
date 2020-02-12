"""Define the necessary fixtures that will need to be used globally."""

from pathlib import Path
import uuid

from PySide2 import QtCore as qtc
import pytest



@pytest.fixture(name="dcpf", autouse=True, scope="session")
def data_center_path_file(tmp_path_factory) -> qtc.QSettings:
    """Initialized needed settings and directories for the Data Center.

    Create and return `QSettings` object with initialized values.
    """
    # TODO: Make this works on Windows too!!!
    masa_base = tmp_path_factory.mktemp("Masa")
    masa_dc = masa_base / "data_center"
    config = masa_base / ".config"

    settings = qtc.QSettings(str(config), qtc.QSettings.NativeFormat)
    settings.setValue("data_center", str(masa_dc))
    settings.sync()

    return settings


@pytest.fixture(scope="session")
def data_center_dir(dcpf):
    """Create and return the `data_center` directory."""
    dc = Path(dcpf.value("data_center", "", type=str))
    dc.mkdir()

    return dc


@pytest.fixture(scope="session")
def workspace_dir(data_center_dir):
    ws = data_center_dir / "test_workspace"
    ws.mkdir()

    return ws


@pytest.fixture(scope="function")
def empty_data_id_dir(workspace_dir):
    d_id = workspace_dir / str(uuid.uuid4())
    d_id.mkdir()

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


@pytest.fixture(scope="function")
def dummy_data(empty_data_dir):
    data = create_dummy_data(empty_data_dir)

    return empty_data_dir.parent, data


@pytest.fixture(scope="function")
def dummy_annotations(empty_annotations_dir):
    raw_data, data_file = create_dummy_annotations(empty_annotations_dir)

    return raw_data, data_file, empty_annotations_dir.parent


@pytest.fixture(scope="function")
def dummy_data_id_dir(empty_data_dir):
    data = create_dummy_data(empty_data_dir)

    return empty_data_dir.parent, data
