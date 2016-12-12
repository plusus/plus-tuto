import sys
from os.path import join

from PySide.QtCore import QTranslator
from PySide.QtGui import QApplication

from plustutocenter.definitions.mvp import View, Controller
from plustutocenter.qt.widgets.main_window import MainWindow
from plustutocenter.utils import project_root


class ViewQt(View):
    """
    Main view of the application
    """

    QT_APPLICATION = QApplication(["Tutorial Center"], QApplication.GuiClient)
    TRANSLATOR = QTranslator()
    i18n = join(project_root(), "i18n", "fr_CA")
    TRANSLATOR.load(i18n)
    QT_APPLICATION.installTranslator(TRANSLATOR)

    def __init__(self, controller):
        """
        :type controller: Controller
        """
        self._controller = controller
        self._main_window = MainWindow(self._controller.getDoneTutorials,
                                       self._controller.saveDoneTutorials)

        self._updateTutorials(self._controller.getTutorials())

    def _updateTutorials(self, tutorials):
        """
        :type tutorials: dict[str, List[Tutorial]]
        """
        self._main_window.setTutorials(tutorials)

    def updateDoneTutorials(self):
        self._main_window.updateDoneTutorials(
            self._controller.getDoneTutorials())

    def launch(self):
        """
        Launch the view (blocking call)
        """
        self._main_window.show()
        ViewQt.QT_APPLICATION.exec_()
