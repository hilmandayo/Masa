from functools import partial
from typing import List

from PySide2 import (QtCore as qtc, QtGui as qtg, QtWidgets as qtw)
import cv2
import numpy as np

from Masa.core.utils import convert_np, SignalPacket
from Masa.gui.widgets.graphics_rect_item import GraphicsRectItem
from Masa.gui.dialog.instance_editor_dialog import InstanceEditorDialog
from Masa.core.data import Instance
from Masa.core.utils import BoundingBoxConverter as bbc
from ..widgets.video_buffer_scene import VideoBufferScene


class BufferRenderView(qtw.QGraphicsView):
    """A QGraphicsView for raw buffer rendering and object selection."""
    pass_rect_coords = qtc.Signal(tuple)
    set_class_name = qtc.Signal(str)
    rect_changed = qtc.Signal(SignalPacket)
    req_datahandler_info = qtc.Signal(SignalPacket)
    prop_data_change = qtc.Signal(SignalPacket)

    def __init__(self, parent=None, width=None, height=None, video_player=None):
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
        self.curr_frame = None
        self.draw_box = False
        self.repair_box = False
        self.current_selection = None
        self.brush_current = qtg.QBrush(qtg.QColor(10, 10, 100, 120))

        self.class_name = []
        self.video_player = video_player
        # self.menu = TextInputMenu(self.class_name, parent=self)

    def _set_attributes(self):
        """Set internal attributes of the view."""
        self.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignLeft)
        self.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)
        # self.setScene(qtw.QGraphicsScene())
        scene = VideoBufferScene()
        scene.rect_changed.connect(
            lambda packet: self.rect_changed.emit(
                SignalPacket(sender=[*packet, self.__class__.__name__],
                             data=packet.data)
        ))
        self.setScene(scene)

    def set_frame(self, frame=None, frame_id=None):
        if isinstance(frame, np.ndarray):
            self.curr_frame = frame.copy()
        if frame_id is not None:
            self.frame_id = frame_id

        curr_frame = convert_np(self.curr_frame, to="qpixmapitem")
        self.scene().addItem(curr_frame)

    def set_data(self):
        for d in self.curr_data:
            self._draw_data(d)

    def _draw_data(self, data: Instance):
        width = data.x2 - data.x1
        height = data.y2 - data.y1
        self.scene().addItem(GraphicsRectItem(data.x1, data.y1, data.x2, data.y2,
                                              self.width, self.height,
                                              data.track_id, data.instance_id,
        ))

    def update_frame(self):
        """Update frames during Box Selection."""
        self.scene().clear()
        self.set_frame()
        self.set_data()

        if self.draw_box:
            x1, y1 = self.bb_top_left.x() / self.width, self.bb_top_left.y() / self.height
            x2, y2 = self.bb_bottom_right.x() / self.width, self.bb_bottom_right.y() / self.height
            self.current_selection = GraphicsRectItem(x1, y1, x2, y2,
                                                      self.width, self.height)
            self.scene().addItem(self.current_selection)

    # def on_rect_change(self, track_id, instance_id, x1, y1, x2, y2):
    #     if self.video_player:
    #         self.video_player._on_rect_change(track_id, instance_id, x1, y1, x2, y2)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == qtc.Qt.MouseButton.RightButton:
            self.draw_box = True
            self.bb_top_left = event.pos()
            self.bb_bottom_right = event.pos()
            self.update_frame()

        elif event.button() == qtc.Qt.MouseButton.LeftButton:
            # We can actually straight handle the process of repairing boxes
            # from here!!! Weird.
            pass
                

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if self.draw_box:
            x = event.pos().x()
            y = event.pos().y()

            max_x = self.curr_frame.shape[1]
            if x < 0:
                self.bb_bottom_right.setX(0)
            elif x > max_x:
                self.bb_bottom_right.setX(max_x - 1)
            else:
                self.bb_bottom_right.setX(x)

            max_y = self.curr_frame.shape[0]
            if y < 0:
                self.bb_bottom_right.setY(0)
            elif y > max_y:
                self.bb_bottom_right.setY(max_y - 1)
            else:
                self.bb_bottom_right.setY(y)

            self.update_frame()

    def _adding_new_sl(self, packet: SignalPacket):
        di = packet.data
        object_class = list(di.obj_classes.keys())[0]
        try:
            track_id = max(di.obj_classes[object_class])
        except ValueError:
            track_id = None
        tags = {k: v[0] for k, v in di.tags.items()}
        instance = Instance(
            track_id=track_id, object_class=object_class, instance_id=None,
            x1=self.current_selection.x1, y1=self.current_selection.y1,
            x2=self.current_selection.x2, y2=self.current_selection.y2,
            frame_id=self.frame_id, tags=tags
        )
        ied = InstanceEditorDialog(instance, di.obj_classes, di.tags, delete_btn=False,
                                   add_only=True)
        ied.prop_data_change.connect(self._propogate_data_change)
        ied.exec_()

    def _propogate_data_change(self, packet: SignalPacket):
        self.prop_data_change.emit(
            SignalPacket(sender=[*packet.sender, self.__class__.__name__], data=packet.data)
        )

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.draw_box:
            self.req_datahandler_info.emit(
                SignalPacket(sender=[self.__class__.__name__], data=(None, None))
            )

            self.draw_box = False
            self.update_frame()

    def add_manual_box(self):
        pass

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

    def set_frame_data_sl(self, packet: SignalPacket):
        framedata = packet.data
        self.scene().clear()

        self.set_frame(framedata.frame, framedata.index)

        self.curr_data = []
        for d in framedata.data:
            self.curr_data.append(d)
        self.set_data()


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

    main.set_frame(np.full([height, width, 3], 155, dtype=np.uint8))
    print(main.size())

    sys.exit(app.exec_())
