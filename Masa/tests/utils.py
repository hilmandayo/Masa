from typing import List


class DummyAnnotationsDataFactory:
    pass


@dataclass
class DummyAnnotationsData:
    pass


@dataclass
class SimpleCSV(DummyAnnotationsData):
    head: List[str] = "frame_id track_id x1 y1 x2 y2 scene object view".split()
    annotations: List[int, str] = [
        [31, 0, 500, 176, 564, 206, "road_scene", "red_traffic_light", "small"],
        [35, 0, 558, 118, 638, 158, "road_scene", "red_traffic_light", "middle"],
        [37, 0, 854, 200, 918, 230, "road_scene", "red_traffic_light", "large"],
        [44, 1, 738, 274, 778, 302, "road_scene", "yellow_traffic_light", "far"],
        [45, 2, 622, 240, 662, 258, "road_scene", "red_traffic_light", "small"],
        [48, 2, 760, 268, 830, 300, "road_scene", "red_traffic_light", "middle"],
        [50, 2, 714, 170, 792, 208, "road_scene", "red_traffic_light", "large"],
        [46, 3, 758, 380, 796, 404, "road_scene", "red_traffic_light", "small"],
        [47, 3, 1010, 288, 1060, 314, "road_scene", "red_traffic_light", "middle"],
        [48, 3, 388, 246, 450, 282, "road_scene", "red_traffic_light", "large"],
        [55, 4, 678, 372, 708, 384, "road_scene", "red_traffic_light", "far"],
        [58, 4, 560, 354, 602, 384, "road_scene", "red_traffic_light", "far"],
        [70, 5, 834, 338, 888, 372, "road_scene", "red_traffic_light", "far"],
        ]
    def dummy_annotations_data(self):
        return anno


    def create_dummy_annotations(self, empty_annotations_dir):
        anno_orig = dummy_annotations_data()

        # Get the raw data ########################################################
        anno = anno_orig.strip().split("\n")
        raw_data = []
        head = anno[0].split(",")
        for val in anno[1:]:
            val = val.split(",")
            retval = {}
            for h, v in zip(head, val):
                try:
                    v = int(v)
                except ValueError:
                    try:
                        v = int(float(v))
                    except ValueError:
                        pass
                retval[h] = v
            raw_data.append(retval)

        # Create the file #########################################################
        data_file = empty_annotations_dir / "annotations.csv"
        with data_file.open("a") as f:
            for i in anno_orig.strip().split("\n"):
                f.write(f"{i.strip()}\n")

        return raw_data, data_file

class DummyBinaryData:
    @staticmethod
    def create_dummy_video(empty_data_dir):
        data = empty_data_dir / f"{str(uuid.uuid4())}.mp4"
        data.write_text("")

        return data
