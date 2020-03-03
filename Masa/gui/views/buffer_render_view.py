from functools import partial

from PySide2 import (QtCore as qtc, QtGui as qtg, QtWidgets as qtw)
import cv2
import numpy as np
from Masa.core.datahandler import FrameData
# from .text_input import TextInputMenu
try:
    from Masa.core.utils import convert_np
    from Masa.gui import GraphicsRectItem
except (ImportError, ModuleNotFoundError):
    import sys
    from pathlib import Path; _dir = Path(__file__).absolute().parent
    sys.path.append(str(_dir.parent.parent / "core" / "utils"))
    from utils import convert_np
    sys.path.append(str(_dir.parent / "widgets"))
    from graphics_rect_item import GraphicsRectItem


class BufferRenderView(qtw.QGraphicsView):
    """A QGraphicsView for raw buffer rendering and object selection."""
    pass_rect_coords = qtc.Signal(tuple)
    set_class_name = qtc.Signal(str)

    def __init__(self, parent=None, width=None, height=None):
        super().__init__(parent)
        self._set_attributes()

        self.width = width
        self.height = height
        self.rect = None
        self.size_adjusted = False
        self.ratio = 1

        # Variables for bonding box selection #################################
        self.bb_top_left = None
        self.bb_bottom_right = None
        self.frame = None
        self.draw_box = False
        self.current_selection = None
        self.brush_current = qtg.QBrush(qtg.QColor(10, 10, 100, 120))

        self.class_name = []
        # self.menu = TextInputMenu(self.class_name, parent=self)

    def _set_attributes(self):
        """Set internal attributes of the view."""
        self.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignLeft)
        self.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)
        self.setScene(qtw.QGraphicsScene())

    def set_data(self, f_data: FrameData):
        if f_data.frame is not None:
            self.frame = f_data.frame.copy()

        # # XXX: not good
        # if rect:
        #     x1, y1, x2, y2 = rect
        #     cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # elif self.rect:
        #     x1, y1, x2, y2 = self.rect
        #     self.rect = None
        #     cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        frame = convert_np(self.frame, to="qpixmapitem")
        self.scene().addItem(frame)

    def update_frame(self):
        # get our image...
        self.scene().clear()
        # self.set_data()

        if self.draw_box:
            x1, y1 = self.bb_top_left.x(), self.bb_top_left.y()
            width, height = self.bb_bottom_right.x() - x1, self.bb_bottom_right.y() - y1
            self.current_selection = GraphicsRectItem(x1, y1, width, height)
            self.scene().addItem(self.current_selection)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # TODO: make below reliable for out of 0 things
        self.bb_top_left = event.pos()
        self.bb_bottom_right = event.pos()
        self.draw_box = True
        self.update_frame()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        x = event.pos().x()
        y = event.pos().y()

        max_x = self.frame.shape[1]
        if x < 0:
            self.bb_bottom_right.setX(0)
        elif x > max_x:
            self.bb_bottom_right.setX(max_x - 1)
        else:
            self.bb_bottom_right.setX(x)

        max_y = self.frame.shape[0]
        if y < 0:
            self.bb_bottom_right.setY(0)
        elif y > max_y:
            self.bb_bottom_right.setY(max_y - 1)
        else:
            self.bb_bottom_right.setY(y)
        self.update_frame()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # self.menu.exec_(qtg.QCursor.pos())  # This will block

        if self.class_name:
            self.set_class_name.emit(self.class_name[0])
            self.get_rect_coords()
            _rect = self.current_selection.rect()
            x1 = int(_rect.x())
            y1 = int(_rect.y())
            width = int(_rect.width())
            height = int(_rect.height())
            x2, y2 = x1 + width, y1 + height
            self.rect = (x1, y1, x2, y2)
            self.class_name.pop(0)

        self.draw_box = False
        self.update_frame()

    def add_manual_box(self):
        pass # CONT

    def sizeHint(self):
        return qtc.QSize(self.width, self.height)

    def get_rect_coords(self):
        rect = self.current_selection.rect()
        x1 = rect.x()
        y1 = rect.y()
        width = rect.width()
        height = rect.height()

        x2, y2 = x1 + width, y1 + height

        self.pass_rect_coords.emit(
            (x1 / self.width(), y1 / self.height(),
             x2 / self.width(), y2 / self.height()))


if __name__ == '__main__':
    import sys
    import time

    width = 640
    height = 540
    app = qtw.QApplication(sys.argv)
    main = BufferRenderView(width=width, height=height)

    main.show()

    # for i in np.zeros([100, width, height, 3], np.uint8):
    #     main.set_data(i)

    main.set_data(np.full([height, width, 3], 155, dtype=np.uint8))
    print(main.size())

    sys.exit(app.exec_())
