import unittest
from unittest.mock import Mock

from libtuto.size import Size

from libtuto.tutorial import Tutorial
from plustutocenter.qt.widgets.main_window import getSoftwareEntries, MainWindow
from plustutocenter.qt.widgets.tutorials_entries_widget import \
    TutorialEntriesWidget


class MainWindowTests(unittest.TestCase):
    TUTORIAL = Tutorial("Do something",
                        "Faire quelque chose",
                        "Description",
                        "", [], Size(800, 600))
    PYTHON_DESKTOP_PATH = "/usr/share/applications/python3.4.desktop"
    PYTHON_VERSION = "3.4"
    TUTORIALS = {(PYTHON_DESKTOP_PATH, PYTHON_VERSION): [TUTORIAL]}
    DONE_TUTORIALS = {PYTHON_DESKTOP_PATH: [TUTORIAL.key]}

    def setUp(self):
        self.done_tutorials_provider = lambda: self.DONE_TUTORIALS
        self.done_tutorials_saver = Mock()
        self.main_window = MainWindow(self.done_tutorials_provider,
                                      self.done_tutorials_saver)

    def test_init(self):
        self.assertIsNotNone(self.main_window.softwareEntriesListWidget)
        self.assertIsNotNone(self.main_window.tutorialEntriesListWidget)

    def test_get_software_entries(self):
        entries = getSoftwareEntries(self.TUTORIALS)
        self.assertEqual(1, len(entries))
        entry = entries[0]
        self.assertIsNotNone(entry.name)
        self.assertIsNotNone(entry.iconPath)
        self.assertIs(next(iter(self.TUTORIALS.values())), entry.tutorials)

    def test_set_tutorials(self):
        expected_entries = getSoftwareEntries(self.TUTORIALS)
        self.main_window.setTutorials(self.TUTORIALS)
        entries = self.main_window.softwareEntriesListWidget.getObjectEntries()
        self.assertEqual(1, len(entries))
        self.assertEqual(expected_entries[0], next(iter(entries)))


    class MockTutorialEntriesWidget:
        def __init__(self, mainWindow):
            """
            :type mainWindow: MainWindow
            """
            self._backup = None
            self._main_window = mainWindow

        def __enter__(self):
            self._backup = self._main_window.tutorialEntriesListWidget
            self._main_window.tutorialEntriesListWidget = \
                Mock(spec=TutorialEntriesWidget)
            return self._main_window.tutorialEntriesListWidget

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._main_window.tutorialEntriesListWidget = self._backup

    def test_update_done_tutorials_no_selection(self):
        with self.MockTutorialEntriesWidget(self.main_window) as m:
            # Should not be updated
            m.updateDoneTutorials.side_effect = self.fail
            self.main_window.updateDoneTutorials(self.DONE_TUTORIALS)

    def test_update_done_tutorials_with_selection(self):
        self.main_window.setTutorials(self.TUTORIALS)
        self.main_window.softwareEntriesListWidget.setCurrentRow(0)
        with self.MockTutorialEntriesWidget(self.main_window) as m:
            self.main_window.updateDoneTutorials(self.DONE_TUTORIALS)
            m.updateDoneTutorials.assert_called_with([self.TUTORIAL.key])

    def test_update_tutorials_view_no_software(self):
        self.main_window.updateTutorialsView(0)

    def test_update_tutorials_view_with_software(self):
        self.main_window.setTutorials(self.TUTORIALS)
        self.main_window.softwareEntriesListWidget.setCurrentRow(0)
        with self.MockTutorialEntriesWidget(self.main_window) as m:
            self.main_window.updateTutorialsView(0)
            m.setEntries.assert_called_with([self.TUTORIAL])
            m.updateDoneTutorials.assert_called_with([self.TUTORIAL.key])
