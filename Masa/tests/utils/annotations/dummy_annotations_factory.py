from ._simple_annotations import *


class DummyAnnotationsFactory:
    """A factory that returns certain mock annotations data."""
    @staticmethod
    def get_annotations(name, **kwargs):
        if name == "simple_anno":
            return SimpleAnnotations(**kwargs)
