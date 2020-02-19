from PySide2 import QtWidgets as qtw
from Masa.gui import ImagesViewerView


def test_adding_images(qtbot, s_finfo):
    imgs_viewerv = ImagesViewerView()
    imgs_viewerv.show()
    qtbot.add_widget(imgs_viewerv)

    for fi in s_finfo:
        imgs_viewerv.add_to_row(fi)
