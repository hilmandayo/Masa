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
    data_file = create_dummy_annotations_file(empty_annotations_dir)

    return empty_annotations_dir.parent, data_file


@pytest.fixture(scope="function")
def dummy_data_id_dir(empty_data_dir):
    data = create_dummy_data(empty_data_dir)

    return empty_data_dir.parent, data


def create_dummy_data(empty_data_dir):
    data = empty_data_dir / f"{str(uuid.uuid4())}.mp4"
    data.write_text("")

    return data


def create_dummy_annotations_file(empty_annotations_dir):
    anno = """
    frame_id,track_id,x1,y1,x2,y2,scene,object,view
    31,0,500,176,564,206,road_scene,red_traffic_light,small
    35,0,558,118,638,158,road_scene,red_traffic_light,middle
    37,0,854,200,918,230,road_scene,red_traffic_light,large
    44,1,738,274,778,302,road_scene,yellow_traffic_light,far
    45,2,622,240,662,258,road_scene,red_traffic_light,small
    48,2,760,268,830,300,road_scene,red_traffic_light,middle
    50,2,714,170,792,208,road_scene,red_traffic_light,large
    46,3,758,380,796,404,road_scene,red_traffic_light,small
    47,3,1010,288,1060,314,road_scene,red_traffic_light,middle
    48,3,388,246,450,282,road_scene,red_traffic_light,large
    55,4,678,372,708,384,road_scene,red_traffic_light,far
    58,4,560,354,602,384,road_scene,red_traffic_light,far
    70,5,834,338,888,372,road_scene,red_traffic_light,far
    """

    data_file = empty_annotations_dir / "annotations.csv"
    with data_file.open("a") as f:
        for i in anno.strip().split("\n"):
            f.write(f"{i.strip()}\n")

    return data_file
