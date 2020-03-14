from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

try:
    from ..views.visualization.sessions_visualizer_view import SessionsVisualizerView, ImagesViewerView
except (ValueError, ImportError, ModuleNotFoundError):
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    import sys;
    sys.path.append(str(_dir.parent / "views" / "visualization"))
    from sessions_visualizer_view import SessionsVisualizerView
    from images_viewer_view import ImagesViewerView

from Masa.models import DataHandler


class SessionVisualizer(qtw.QWidget):
    def __init__(self, data_handler: DataHandler, parent=None):
        super().__init__(parent=parent)

        self.data_handler = data_handler
        self.data_init = False

        self._init_widgets()
        self._optimize_widgets()
        self._init_layouts()
        self._init()

        self._setup_images_viewers()
        self._setup_data()

    def _init_widgets(self):
        self.view = SessionsVisualizerView()

    def _optimize_widgets(self):
        pass

    def _init_layouts(self):
        self.main_layout = qtw.QVBoxLayout()

    def _init(self):
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.view)

    def _init_data(self, buff):
        if self.data_init:
            raise Exception(f"`_init_data` is called twice from `SessionVisualizer`")
        buff.to_pause()
        for t_obj in self.data_handler:
            for instance in t_obj:
                pass
        buff.to_play()

    def _setup_images_viewers(self):
        for obj_cls in self.data_handler.object_classes:
            self.view._add_images_viewer(obj_cls, ImagesViewerView())

    def _setup_data(self):
        for t_obj in self.data_handler:
            for instance in t_obj:
                self.view._images_viewers[instance.object_class].add_to_row(instance)

    def _add_images_viewer(self, group: str, img_viewer: ImagesViewerView):
        """Add an ImagesViewerView object."""
        self.main_layout.addWidget(img_viewer)
        self.view._images_viewers[group] = img_viewer

    # def add_data(self, data: FrameData):
    #     if data.object_class not in self._images_viewers.keys():
    #         raise ValueError()

    #     self._images_viewers[data.object_class].add_to_row(data)



if __name__ == '__main__':
    sys.path.append(str(_dir.parent.parent / "tests" / "utils"))
    # for some reasons, below does not work although we put the path
    # from tests.utils import DummyAnnotationsFactory
    from annotations.simple_annotations import DummyAnnotationsFactory

    app = qtw.QApplication(sys.argv)
    sa = DummyAnnotationsFactory.get_annotations("simple_anno")
    dh = DataHandler(input_str=sa.data_str)

    sv = SessionVisualizer(dh)

    sv.show()

    sys.exit(app.exec_())
