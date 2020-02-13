"""Define the necessary fixtures that will need to be used globally."""

from collections import namedtuple
from pathlib import Path
import uuid

from PySide2 import QtCore as qtc
import pytest

from .utils import DummyAnnotationsFactory


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


# Annotations and binaries test data ##########################################

simple_anno = DummyAnnotationsFactory.get_annotations("simple_anno")
@pytest.fixture(name="s_anno_rl", scope="session",
                params=simple_anno.data)
def simple_raw_annotations_loop(request):
    return simple_anno.head, request.param

@pytest.fixture(name="s_anno_rli", scope="session",
                params=simple_anno.data_per_instance)
def simple_raw_annotations_loop_per_instance(request):
    return simple_anno.head, request.param

AnnotationsSet = namedtuple("AnnotationsSet", "file head data")
@pytest.fixture(name="s_anno_rf",scope="function")
def simple_raw_annotations_file(empty_annotations_dir):
    return AnnotationsSet(simple_anno.create_file(empty_annotations_dir), simple_anno.head, simple_anno.data)
