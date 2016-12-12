from PySide.QtCore import QPoint, Qt
from PySide.QtGui import QGraphicsView, QMouseEvent


class OverlayGraphicsView(QGraphicsView):

    def __init__(self, scene, tutorial_click_handler):
        """
        :type: QGraphicsScene
        :param tutorial_click_handler: Function which handles the tutorial click
        :type tutorial_click_handler: (QPoint) -> None
        """
        super().__init__(scene)
        self.setStyleSheet("background: rgba(0, 0, 0, 0);")
        self._tutorial_click_handler = tutorial_click_handler
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        """
        :type event: QMouseEvent
        """
        super().mousePressEvent(event)
        self._tutorial_click_handler(event.pos())
