from PySide.QtCore import Qt, QRect, QPointF, QPoint
from PySide.QtGui import QGraphicsItem, QPainter, QColor, QFont

from libtuto.tutorial import TutorialStep


class OverlayGraphicsItem(QGraphicsItem):

    BACKGROUND_ALPHA = 150
    FONT_SIZE = 14

    def __init__(self,
                 step_provider,
                 is_done,
                 width=None, height=None,
                 parent=None, scene=None):
        """
        :type step_provider: () -> TutorialStep
        :type is_done: () -> bool
        :param width: Width of the widget (optional)
        :param height: Height of the widget (optional)
        :param parent: Parent widget
        :param scene: Scene owning the widget
        """
        super().__init__(parent, scene)
        self._width = width or 0
        self._height = height or 0
        self._alpha = 0
        self._step_provider = step_provider
        self._is_done = is_done

        self._updateQuads()

    def _get_action_zone_rect(self):
        """
        :rtype: QRect
        """
        zone = self._step_provider().actionZone
        top_left = zone.topLeft()
        bottom_right = zone.bottomRight()
        return QRect(top_left[0],
                     top_left[1],
                     bottom_right[0] - top_left[0],
                     bottom_right[1] - top_left[1])

    def boundingRect(self):
        """
        :rtype: QRect
        """
        return QRect(0, 0, self._width, self._height)

    def getAlpha(self):
        """
        :rtype: int
        """
        return self._alpha

    def setAlpha(self, alpha):
        """
        :param alpha: [0, 255]
        """
        self._alpha = alpha

    def _updateQuads(self):
        quad_width = self._width / 2
        quad_height = self._height / 2
        self._quadrants = [
            QRect(quad_width, 0, quad_width, quad_height),
            QRect(quad_width, quad_height, quad_width, quad_height),
            QRect(0, quad_height, quad_width, quad_height),
            QRect(0, 0, quad_width, quad_height)
        ]

    def setSize(self, width, height):
        """
        :type width: int
        :type height: int
        """
        self._width = width
        self._height = height
        self._updateQuads()

    def _dynamic_description_position(self, actionZoneRect):
        """
        Computes a dynamic position for the text which aimed at being at the
        opposite of the clickable region in the window
        :param actionZoneRect: Clickable zone as a rectangle
        :type actionZoneRect: QRect
        :rtype: QRect
        """
        quad = self._quadrants[0]
        for i, q in zip(range(4), self._quadrants):
            if q.contains(actionZoneRect.topLeft()):
                quad = self._quadrants[(i + 2) % 4]
                break
        return quad

    def paint(self, painter, option, widget):
        """
        :type painter: QPainter
        :type option: QStyleOptionGraphicsItem
        :type widget: QWidget
        """
        painter.setPen(QColor(0, 0, 0, 0))
        painter.setBrush(QColor(0, 0, 0, self._alpha))
        painter.drawRect(0, 0, self._width, self._height)

        painter.setCompositionMode(QPainter.CompositionMode_Clear)

        rect = self._get_action_zone_rect()
        if self._alpha < self.BACKGROUND_ALPHA:
            adj_width = self._width - \
                (self._alpha * self._width / self.BACKGROUND_ALPHA)
            adj_height = self._height - \
                (self._alpha * self._height / self.BACKGROUND_ALPHA)
            rect.adjust(-adj_width, -adj_height, adj_width, adj_height)

        painter.drawRect(rect)

        if not self._is_done():
            painter.setFont(QFont(None, self.FONT_SIZE, QFont.Bold))
            step = self._step_provider()
            if step.descriptionPosition:
                painter.drawText(QPointF(*step.descriptionPosition.topLeft()),
                                 step.description)
            else:
                painter.drawText(self._dynamic_description_position(rect),
                                 Qt.AlignCenter | Qt.TextWordWrap,
                                 step.description)
