from typing import Dict
from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

try:
    from Masa.core.utils import BoundingBoxConverter as bbc
    from .video_buffer_scene import VideoBufferScene
except ModuleNotFoundError:
    import sys
    from pathlib import Path; _dir = Path(__file__).absolute().parent

    sys.path.append(str(_dir.parent.parent.parent))
    from Masa.core.utils import BoundingBoxConverter as bbc
    from video_buffer_scene import VideoBufferScene


# TODO: Refractor to name BoundingBoxItem
class GraphicsRectItem(qtw.QGraphicsRectItem):

    handle_top_left = 1
    handle_top_middle = 2
    handle_top_right = 3
    handle_middle_left = 4
    handle_middle_right = 5
    handle_bottom_left = 6
    handle_bottom_middle = 7
    handle_bottom_right = 8

    handle_size = +8.0
    handle_space = -4.0

    handle_cursors = {
        handle_top_left: qtc.Qt.SizeFDiagCursor,
        handle_top_middle: qtc.Qt.SizeVerCursor,
        handle_top_right: qtc.Qt.SizeBDiagCursor,
        handle_middle_left: qtc.Qt.SizeHorCursor,
        handle_middle_right: qtc.Qt.SizeHorCursor,
        handle_bottom_left: qtc.Qt.SizeBDiagCursor,
        handle_bottom_middle: qtc.Qt.SizeVerCursor,
        handle_bottom_right: qtc.Qt.SizeFDiagCursor,
    }

    def __init__(self, x1, y1, x2, y2, width_scale, height_scale,
                 track_id=None, instance_id=None, parent=None):
        """Initialize the shape."""

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width_scale = width_scale
        self.height_scale = height_scale
        self.track_id = track_id
        self.instance_id = instance_id

        x, y, width, height = bbc.calc_width_height(
            self.x1, self.y1, self.x2, self.y2,
            self.width_scale, self.height_scale, True
        )

        # super().__init__(x, y, width, height)
        super().__init__(0, 0, width, height, parent=parent)
        self.setPos(x, y)

        # The 8 handles surrounding the item
        self.handles: Dict[int, qtc.QRectF] = {}
        self.handle_selected = None
        self.mouse_press_pos = None
        self.mouse_press_rect = None
        self.setAcceptHoverEvents(True)

        # self.edit_mode = True
        self.setFlag(qtw.QGraphicsItem.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.ItemIsSelectable)
        self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(qtw.QGraphicsItem.ItemIsFocusable)
        self.update_handles_pos()

    # def set_edit_mode(self, edit):
    #     self.edit_mode = edit
    #     self.setFlag(qtw.QGraphicsItem.ItemIsMovable, self.edit_mode)
    #     self.setFlag(qtw.QGraphicsItem.ItemIsSelectable, self.edit_mode)
    #     self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges, self.edit_mode)
    #     self.setFlag(qtw.QGraphicsItem.ItemIsFocusable, self.edit_mode)
    #     self.update()

    def handle_at(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():  # k: int, v: qrectf
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, move_event):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handle_at(move_event.pos())
            cursor = qtc.Qt.ArrowCursor if handle is None else self.handle_cursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(move_event)

    def hoverLeaveEvent(self, move_event):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.setCursor(qtc.Qt.ArrowCursor)
        super().hoverLeaveEvent(move_event)

    def mousePressEvent(self, mouse_event):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handle_selected = self.handle_at(mouse_event.pos())
        if self.handle_selected:
            self.mouse_press_pos = mouse_event.pos()
            self.mouse_press_rect = self.boundingRect()
        super().mousePressEvent(mouse_event)

    def mouseMoveEvent(self, mouse_event):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handle_selected is not None:
            self.interactive_resize(mouse_event.pos())
        else:
            super().mouseMoveEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouse_event)
        self.handle_selected = None
        self.mouse_press_pos = None
        self.mouse_press_rect = None

        new_x1 = self.pos().x()
        new_y1 = self.pos().y()
        new_x2 = new_x1 + self.rect().width()
        new_y2 = new_y1 + self.rect().height()

        self.x1, self.x2 = new_x1 / self.width_scale, new_x2 / self.width_scale
        self.y1, self.y2 = new_y1 / self.height_scale, new_y2 / self.height_scale
        
        self.update()
        if self.scene():
            self.scene().on_rect_change(
                self.track_id, self.instance_id, self.x1, self.y1, self.x2, self.y2
            )

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handle_size + self.handle_space
        return self.rect().adjusted(-o, -o, o, o)

    def update_handles_pos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handle_size
        b = self.boundingRect()
        self.handles[self.handle_top_left] = qtc.QRectF(b.left(), b.top(), s, s)
        self.handles[self.handle_top_middle] = qtc.QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handle_top_right] = qtc.QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handle_middle_left] = qtc.QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handle_middle_right] = qtc.QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handle_bottom_left] = qtc.QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handle_bottom_middle] = qtc.QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handle_bottom_right] = qtc.QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactive_resize(self, mouse_pos):
        """
        Perform shape interactive resize.
        """
        offset = self.handle_size + self.handle_space
        bounding_rect = self.boundingRect()
        rect = self.rect()
        diff = qtc.QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handle_selected == self.handle_top_left:

            fromX = self.mouse_press_rect.left()
            fromY = self.mouse_press_rect.top()
            toX = fromX + mouse_pos.x() - self.mouse_press_pos.x()
            toY = fromY + mouse_pos.y() - self.mouse_press_pos.y()

            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setLeft(toX)
            bounding_rect.setTop(toY)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setTop(bounding_rect.top() + offset)

            self.setRect(rect)

        elif self.handle_selected == self.handle_top_middle:

            fromY = self.mouse_press_rect.top()
            toY = fromY + mouse_pos.y() - self.mouse_press_pos.y()
            diff.setY(toY - fromY)
            bounding_rect.setTop(toY)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)

        elif self.handle_selected == self.handle_top_right:

            fromX = self.mouse_press_rect.right()
            fromY = self.mouse_press_rect.top()
            toX = fromX + mouse_pos.x() - self.mouse_press_pos.x()
            toY = fromY + mouse_pos.y() - self.mouse_press_pos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setRight(toX)
            bounding_rect.setTop(toY)
            rect.setRight(bounding_rect.right() - offset)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)

        elif self.handle_selected == self.handle_middle_left:

            fromX = self.mouse_press_rect.left()
            toX = fromX + mouse_pos.x() - self.mouse_press_pos.x()
            diff.setX(toX - fromX)
            bounding_rect.setLeft(toX)
            rect.setLeft(bounding_rect.left() + offset)
            self.setRect(rect)

        elif self.handle_selected == self.handle_middle_right:
            fromX = self.mouse_press_rect.right()
            toX = fromX + mouse_pos.x() - self.mouse_press_pos.x()
            diff.setX(toX - fromX)
            bounding_rect.setRight(toX)
            rect.setRight(bounding_rect.right() - offset)
            self.setRect(rect)

        elif self.handle_selected == self.handle_bottom_left:

            fromX = self.mouse_press_rect.left()
            fromY = self.mouse_press_rect.bottom()
            toX = fromX + mouse_pos.x() - self.mouse_press_pos.x()
            toY = fromY + mouse_pos.y() - self.mouse_press_pos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setLeft(toX)
            bounding_rect.setBottom(toY)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        elif self.handle_selected == self.handle_bottom_middle:

            fromY = self.mouse_press_rect.bottom()
            toY = fromY + mouse_pos.y() - self.mouse_press_pos.y()
            diff.setY(toY - fromY)
            bounding_rect.setBottom(toY)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        elif self.handle_selected == self.handle_bottom_right:

            fromX = self.mouse_press_rect.right()
            fromY = self.mouse_press_rect.bottom()
            toX = fromX + mouse_pos.x() - self.mouse_press_pos.x()
            toY = fromY + mouse_pos.y() - self.mouse_press_pos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setRight(toX)
            bounding_rect.setBottom(toY)
            rect.setRight(bounding_rect.right() - offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        self.update_handles_pos()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = qtg.QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.setBrush(qtg.QBrush(qtg.QColor(255, 0, 0, 100)))
        painter.setPen(qtg.QPen(qtg.QColor(0, 0, 0), 1.0, qtc.Qt.SolidLine))
        painter.drawRect(self.rect())

        # if self.edit_mode:
        painter.setRenderHint(qtg.QPainter.Antialiasing)
        painter.setBrush(qtg.QBrush(qtg.QColor(255, 0, 0, 255)))
        painter.setPen(qtg.QPen(qtg.QColor(0, 0, 0, 255), 1.0, qtc.Qt.SolidLine, qtc.Qt.RoundCap, qtc.Qt.RoundJoin))
        for handle, rect in self.handles.items():
            if self.handle_selected is None or handle == self.handle_selected:
                painter.drawEllipse(rect)


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    main = qtw.QGraphicsView()
    main.setFixedSize(700, 700)
    main.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignLeft)  # start at 0, 0
    main.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
    main.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
    main.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
    # main.setSceneRect(0, 0, 1000, 1000)
    # main.setFixedSize(1000, 1000)

    rect = [0, 0, 1, 1]
    scene = VideoBufferScene()
    item = qtw.QGraphicsRectItem(0, 0, 500, 500)
    scene.addItem(item)

    rect2 = [0.1, 0.2, 1, 1]
    item2 = GraphicsRectItem(0, 0, *rect2, 300, 300)
    scene.addItem(item2)

    # scene.rect_changed.connect(lambda packet: print(packet.data))

    main.setScene(scene)
    main.show()

    sys.exit(app.exec_())
