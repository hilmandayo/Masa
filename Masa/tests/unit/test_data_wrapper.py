from Masa.core.data import FrameData
import numpy as np


def test_frame_info(s_anno_rl):
    head, data = s_anno_rl
    x1 = data[head.index("x1")]
    y1 = data[head.index("y1")]
    x2 = data[head.index("x2")]
    y2 = data[head.index("y2")]
    object_class = data[head.index("object")]
    tag = data[head.index("view")]
    frame = np.zeros([30, 30, 3])
    frame_id = data[head.index("frame_id")]
    track_id = data[head.index("track_id")]
    frame_info = FrameData(
        frame=frame, x1=x1, y1=y1, x2=x2, y2=y2,
        object_class=object_class, tag=tag,
        frame_id=frame_id, track_id=track_id
    )

    assert all([
        np.all(frame_info.frame == frame),
        frame_info.x1 == x1,
        frame_info.y1 == y1,
        frame_info.x2 == x2,
        frame_info.y2 == y2,
        frame_info.object_class == object_class,
        frame_info.track_id == track_id,
        frame_info.tag == tag
    ])
