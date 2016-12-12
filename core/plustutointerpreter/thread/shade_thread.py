from time import sleep
from PySide.QtCore import QThread


class ShadeThread(QThread):
    def __init__(self, overlay_item,
                 fct_repaint,
                 alpha_function,
                 stop_condition,
                 alpha_goal,
                 parent=None):
        """
        :type overlay_item: OverlayGraphicsItem
        :type fct_repaint: () -> None
        :param alpha_function: Alpha value function for each iteration
        :type alpha_function: (float) -> float
        :param stop_condition: Condition taking the alpha value
        :type stop_condition: (float) -> Bool
        :param alpha_goal: Final value expected to be attained
        :type alpha_goal: float
        """
        super().__init__(parent)
        self._overlay_item = overlay_item
        self._fct_repaint = fct_repaint
        self._alpha_function = alpha_function
        self._stop_condition = stop_condition
        self._alpha_goal = alpha_goal

    def run(self):
        alpha = self._overlay_item.getAlpha()
        iteration = 0
        while self._stop_condition(alpha):
            self._overlay_item.setAlpha(alpha)
            iteration += 1
            alpha = self._alpha_function(iteration)
            self._fct_repaint()
            sleep(0.02)
        self._overlay_item.setAlpha(self._alpha_goal)
        self._fct_repaint()
