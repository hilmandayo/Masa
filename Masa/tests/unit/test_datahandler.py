import csv
import pytest
from Masa.core.datahandler import DataHandler, TrackedObject


def test_simple_annotations(s_anno_rf):
    """Make sure we have a correct simple annotations test data to work with."""
    # CONT: here
    out = []
    with s_anno_rf.file.open("r") as f:
        csv_anno = csv.DictReader(f)
        for anno, data in zip(csv_anno, s_anno_rf.data):
            for i, h in enumerate(s_anno_rf.head):
                anno_val = anno[h]
                data_val = data[i]
                if isinstance(data_val, int):
                    anno_val = int(anno_val)
                elif isinstance(data_val, float):
                    anno_val = float(anno_val)

                # cont: why false?
                out.append(anno_val == data_val)

    assert all(out)


def test_iter_dh(s_anno_rf):
    dh = DataHandler(s_anno_rf.file)
    assert all(isinstance(to, TrackedObject) for to in dh)

class TestBasicInterface:
    pass


# def test_indexing(dummy_annotations):
#     # TODO: need to test this
#     raw_data, data_file, _ = dummy_annotations
#     dh = DataHandler(data_file)

#     for data in raw_data:
#         track_id = data["track_id"]
#         track_object = dh[track_id]
#         instances = track_object.to_dict()
