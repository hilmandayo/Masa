import pytest
from Masa.core.datahandler import DataHandler


def test_dummy_annotations(dummy_annotations):
    """Make sure we have a dummy annotations file to work with."""
    raw_data, data_file, _ = dummy_annotations
    assert data_file.read_text()


def test_parse_annotations(dummy_annotations):
    raw_data, data_file, _ = dummy_annotations
    dh = DataHandler(data_file)


def test_indexing(dummy_annotations):
    # TODO: need to test this
    raw_data, data_file, _ = dummy_annotations
    dh = DataHandler(data_file)

    for data in raw_data:
        track_id = data["track_id"]
        track_object = dh[track_id]
        instances = track_object.to_dict()
