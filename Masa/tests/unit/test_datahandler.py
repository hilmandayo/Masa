import pytest
from Masa.core.datahandler import DataHandler


def test_dummy_annotations(dummy_annotations):
    """Make sure we have a dummy annotations to work with."""
    _, data = dummy_annotations
    assert data.read_text()


def test_parse_annotations(dummy_annotations):
    _, data = dummy_annotations
    DataHandler._read_csv(data)
