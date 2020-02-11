from Masa.core.datahandler import TrackObject
import pytest


@pytest.mark.parametrize(
    "data_collection"
    [([0, 37, 854, 200, 918, 230, "red_traffic_light", "large"]),
     ([1, 44, 738, 274, 778, 302, "yellow_traffic_light", "far"]),
     ([2, 48, 760, 268, 830, 300, "red_traffic_light", "middle"],
      [2, 45, 622, 240, 662, 258, "red_traffic_light", "small"])
     ]
)
def test_track_object(data):
    tracked = None
    for data in data_collection:
        track_id, frame_id, x1, y1, x2, y2, object_class, view = data
        out = {"view": view, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
        if tracked is None:
            tracked = TrackObject(track_id=track_id, object_class=object_class,
                                  instance=out)
        else:
            pass
