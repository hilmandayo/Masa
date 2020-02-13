class DummyBinaryDataFactory:
    @classmethod
    def get_data(self, data):
        if data == "simple_csv":
            return SimpleCSV()

# @dataclass
# class DummyBinaryData:
#     pass

# @dataclass
# class SimpleVideos(DummyBinaryData):
#     length: int = 100
#     values: Union[int, List] = field(
#         default_factory=np.random.randint(0, 255, size=self.length)
#     )

#     @property
#     def dummy_data(self):
#         return values

#     def create_dummy_data(self, empty_data_dir, file_name="video.mp4"):
#         data_file = empty_annotations_dir / file_name
#         if data_file.exists():
#             return data_file

#         data_file.write_bytes(b"")
#         return data_file
