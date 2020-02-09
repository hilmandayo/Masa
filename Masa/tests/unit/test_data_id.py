import pytest
from Masa.core.datacenter.dataid import DataID


def test_data_id_structure(empty_data_id_dir):
    """A call to an empty `DataID` should create needed directories.

    `Workspace` class will automatically create a DataID directory with the
    given name parameter. From there, `DataID` will handle the structures that
    it will need to have.
    """
    d_id = DataID(empty_data_id_dir)
    assert all([
        (empty_data_id_dir / "data").exists(),
        (empty_data_id_dir / "annotations").exists(),
    ])


def test_get_buffer(dummy_data):
    data_id, data = dummy_data_id_dir
    d_id = DataID(data_id)

    assert d_id.buffer == str(data)


@pytest.mark.skip(reason="Need to implement annotations")
def test_get_annotations(dummy_data_id_dir):
    data_id, data = dummy_data_id_dir
    d_id = DataID(data_id)

    assert d_id.buffer == str(data)
