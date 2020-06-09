import brambox as bb
from pathlib import Path
import cv2


class RoadSceneAnnotationParser(bb.io.parser.AnnotationParser):
    # Choose Parser, AnnotationParser or DetectionParser
    parser_type = bb.io.parser.ParserType.MULTI_FILE
    serialize_group = "image"

    def __init__(self):
        super().__init__()
        self.to_ignore = ["other"]
        self.add_column("distance")

    def deserialize(self, raw_data, data_id_path):
        data_id_path = Path(data_id_path).parent.parent
        # vid = list((data_id_path / "data").glob("*.mp4"))
        # assert len(vid) == 1
        # vid = vid[0]

        anno = data_id_path / "annotations" / "annotations.csv"
        assert anno.exists()

        # TODO: Record width and height of our data
        raw_data = raw_data.strip().split("\n")
        header = raw_data[0].split(",")
        for data in raw_data[1:]:
            data = data.split(",")
            if data[header.index("object_class")] == "green_traffic_light":
                continue
            orig_height, orig_width = cv2.imread(
                str(data_id_path / "data" / ".extracted" /
                    f"{data[header.index('frame_id')]}.jpg")
            ).shape[:2]

            x1, x2 = [float(x) * orig_width for x in
                        (data[header.index("x1")], data[header.index("x2")])]
            y1, y2 = [float(y) * orig_height for y in
                        (data[header.index("y1")], data[header.index("y2")])]
            width = x2 - x1
            height = y2 - y1

            self.append(
                str(Path(data_id_path.name) / "data" / ".extracted" /
                    f"{data[header.index('frame_id')]}"),
                class_label=data[header.index('object_class')],
                x_top_left=x1, y_top_left=y1,
                width=width, height=height,
                distance = data[header.index("distance")],
                ignore = (True if
                          data[header.index("distance")] in self.to_ignore
                          else False)
            )

    def serialize(self, df):
        """ Save dataframe at location `path`"""
        print(df)


class RoadSceneDetectionParser(bb.io.parser.DetectionParser):
    # Choose Parser, AnnotationParser or DetectionParser
    parser_type = bb.io.parser.ParserType.MULTI_FILE
    serialize_group = "image"

    def __init__(self):
        super().__init__()

    def deserialize(self, raw_data, data_id_path):
        data_id_path = Path(data_id_path).parent.parent
        vid = list((data_id_path / "data").glob("*.mp4"))
        assert len(vid) == 1
        vid = vid[0]

        det = data_id_path / "annotations" / "annotations.csv"
        assert det.exists()

        orig_height, orig_width = cv2.VideoCapture(str(vid)).read()[1].shape[:2]
        # TODO: Record width and height of our data
        raw_data = raw_data.strip().split("\n")
        header = raw_data[0].split(",")
        for data in raw_data[1:]:
            data = data.split(",")

            x1, x2 = [float(x) * orig_width for x in
                        (data[header.index("x1")], data[header.index("x2")])]
            y1, y2 = [float(y) * orig_height for y in
                        (data[header.index("y1")], data[header.index("y2")])]
            width = x2 - x1
            height = y2 - y1

            self.append(
                (data_id_path / "data" / ".extracted" /
                f"{data[header.index('frame_id')]}"),
                class_label=data[header.index('object_class')],
                x_top_left=x1, y_top_left=y1,
                width=width, height=height,
            )

    def serialize(self, df):
        """ Save dataframe at location `path`"""
        pass
