import unittest
from unittest.mock import Mock

from PySide.QtGui import QApplication

from libtuto.size import Size

from libtuto.tutorial import Tutorial
from plustutocenter.definitions.mvp import Controller
from plustutocenter.qt.view_qt import ViewQt
from plustutocenter.qt.widgets.main_window import MainWindow


class ViewQtTests(unittest.TestCase):
    TUTORIAL = Tutorial("", "St", "St", "", [], Size(800, 600))
    TUTORIALS = {("someapp.desktop", "version"): [TUTORIAL]}
    DONE_TUTORIALS = {"someapp.desktop": ["Some tutorial"]}

    QT_APP_BCK = ViewQt.QT_APPLICATION

    def setUp(self):
        self.controller_mock = Mock(spec=Controller)
        self.controller_mock.getDoneTutorials.return_value = self.DONE_TUTORIALS
        self.controller_mock.getTutorials.return_value = self.TUTORIALS
        self.view_qt = ViewQt(self.controller_mock)

    def tearDown(self):
        ViewQt.QT_APPLICATION.reset_mock()

    @classmethod
    def setUpClass(cls):
        ViewQt.QT_APPLICATION = Mock(spec=QApplication)

    @classmethod
    def tearDownClass(cls):
        ViewQt.QT_APPLICATION = cls.QT_APP_BCK

    def test_init(self):
        self.assertIs(self.controller_mock, self.view_qt._controller)
        self.assertIsNotNone(self.view_qt._main_window)

    def test_update_tutorials(self):
        self.view_qt._main_window = Mock(spec=MainWindow)
        self.view_qt._updateTutorials(self.TUTORIALS)
        self.view_qt._main_window.setTutorials.assert_called_with(
            self.TUTORIALS)

    def test_update_done_tutorials(self):
        self.view_qt._main_window = Mock(spec=MainWindow)
        self.view_qt.updateDoneTutorials()
        self.view_qt._main_window.updateDoneTutorials.assert_called_with(
            self.DONE_TUTORIALS
        )

    def test_launch(self):
        self.view_qt._main_window = Mock(spec=MainWindow)
        self.view_qt.launch()
        self.assertTrue(self.view_qt._main_window.show.called)
        self.assertTrue(ViewQt.QT_APPLICATION.exec_.called)
