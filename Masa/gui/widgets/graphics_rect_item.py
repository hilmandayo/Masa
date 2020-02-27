from PySide2 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
import sys


class GraphicsRectItem(qtw.QGraphicsRectItem):

    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: qtc.Qt.SizeFDiagCursor,
        handleTopMiddle: qtc.Qt.SizeVerCursor,
        handleTopRight: qtc.Qt.SizeBDiagCursor,
        handleMiddleLeft: qtc.Qt.SizeHorCursor,
        handleMiddleRight: qtc.Qt.SizeHorCursor,
        handleBottomLeft: qtc.Qt.SizeBDiagCursor,
        handleBottomMiddle: qtc.Qt.SizeVerCursor,
        handleBottomRight: qtc.Qt.SizeFDiagCursor,
    }

    def __init__(self, *rect):
        """Initialize the shape."""
        super().__init__(*rect)
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)

        self.edit_mode = True
        self.setFlag(qtw.QGraphicsItem.ItemIsMovable, self.edit_mode)
        self.setFlag(qtw.QGraphicsItem.ItemIsSelectable, self.edit_mode)
        self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges, self.edit_mode)
        self.setFlag(qtw.QGraphicsItem.ItemIsFocusable, self.edit_mode)
        self.updateHandlesPos()

    def set_edit_mode(self, edit):
        self.edit_mode = edit
        self.setFlag(qtw.QGraphicsItem.ItemIsMovable, self.edit_mode)
        self.setFlag(qtw.QGraphicsItem.ItemIsSelectable, self.edit_mode)
        self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges, self.edit_mode)
        self.setFlag(qtw.QGraphicsItem.ItemIsFocusable, self.edit_mode)
        self.update()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():  # k: int, v: qrectf
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handleAt(moveEvent.pos())
            cursor = qtc.Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.setCursor(qtc.Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        print(mouseEvent.pos())
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = qtc.QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = qtc.QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = qtc.QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = qtc.QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = qtc.QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = qtc.QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = qtc.QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = qtc.QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = qtc.QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:

            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:

            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        self.updateHandlesPos()

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

        if self.edit_mode:
            painter.setRenderHint(qtg.QPainter.Antialiasing)
            painter.setBrush(qtg.QBrush(qtg.QColor(255, 0, 0, 255)))
            painter.setPen(qtg.QPen(qtg.QColor(0, 0, 0, 255), 1.0, qtc.Qt.SolidLine, qtc.Qt.RoundCap, qtc.Qt.RoundJoin))
            for handle, rect in self.handles.items():
                if self.handleSelected is None or handle == self.handleSelected:
                    painter.drawEllipse(rect)


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    main = qtw.QGraphicsView()
    main.setSceneRect(0, 0, 1000, 1000)
    main.setFixedSize(500, 500)

    rect = [100, 100, 100, 100]
    scene = qtw.QGraphicsScene(*rect)
    # scene.setSceneRect(qtc.QRectF(0, 0, 200, 200))
    item = GraphicsRectItem(*rect)
    # item.set
    scene.addItem(item)

    main.setScene(scene)
    main.show()

    sys.exit(app.exec_())
