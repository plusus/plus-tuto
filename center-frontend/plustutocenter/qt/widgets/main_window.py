from PySide.QtCore import QProcess
from PySide.QtGui import QMainWindow, QWidget, QListWidget, QListWidgetItem,\
    QItemSelectionModel, QIcon

from xdg.DesktopEntry import DesktopEntry

from plustutocenter.qt.pyside_dynamic import loadUi
from plustutocenter.qt.widgets.search_bar import ClearableLineEdit
from plustutocenter.qt.widgets.software_entries_widget import \
    SoftwareEntriesWidget, SoftwareEntry
from plustutocenter.qt.widgets.tutorials_entries_widget import \
    TutorialEntriesWidget
from plustutocenter.utils import ui_filepath, resource_filepath


def getSoftwareEntries(tutorials):
    """
    :type tutorials: dict[(str, str), List[Tutorial]]
    :rtype: list[SoftwareEntry]
    """
    entries = []
    for p, tuto in tutorials.items():
        desktopEntry = DesktopEntry(p[0])
        entries.append(SoftwareEntry(desktopEntry.getName(),
                                     desktopEntry.getIcon(),
                                     tuto,
                                     p[0]))
    return sorted(entries)


class MainWindow(QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, done_tutorials_provider, done_tutorials_saver,
                 parent=None):
        """
        :param done_tutorials_provider: Provider for done tutorials
        :type done_tutorials_provider: () -> Dict[str, List[str]]
        :type done_tutorials_saver: (Dict[str, List[str]]) -> None
        :type parent: QWidget
        """
        QMainWindow.__init__(self, parent)
        loadUi(ui_filepath('manager_window.ui'), self)

        self.setWindowIcon(QIcon(resource_filepath("plustutocenter.svg")))

        self._done_tutorials = done_tutorials_provider
        self._done_tutorials_saver = done_tutorials_saver
        self.interpreter_process = QProcess()

        # Set decorators for promoting widgets to custom types
        self.softwareEntriesListWidget = SoftwareEntriesWidget(
            self.softwareEntriesListWidget)
        """:type: QListWidget | SoftwareEntriesWidget"""
        self.tutorialEntriesListWidget = TutorialEntriesWidget(
            self.tutorialEntriesListWidget)
        """:type: QListWidget | TutorialEntriesWidget"""

        # Auto-completion definitions
        self.mainSplitter = self.mainSplitter
        """:type: QSplitter"""
        self.rightSplitter = self.rightSplitter
        """:type: QSplitter"""
        self.tutorialDescription = self.tutorialDescription
        """:type: QLabel"""
        self.launchButton = self.launchButton
        """:type: QPushButton"""
        self.horizontalLayout = self.horizontalLayout
        """:type: QHBoxLayout"""

        self.searchEditLine = ClearableLineEdit(self._updateFilter)
        self.horizontalLayout.addWidget(self.searchEditLine)

        # Connect signals
        self.softwareEntriesListWidget.currentRowChanged.connect(
            self.updateTutorialsView)
        self.tutorialEntriesListWidget.currentRowChanged.connect(
            self.updateTutorialDescription)
        self.launchButton.clicked.connect(self.onLaunchButton)
        self.ignoreButton.clicked.connect(self.onIgnoreButton)

        self._layoutSplitter()

    def _layoutSplitter(self):
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 2)
        self.rightSplitter.setStretchFactor(0, 2)
        self.rightSplitter.setStretchFactor(1, 3)

    def _updateFilter(self, filter_text):
        """
        :type filter_text: str
        """
        filter_formatted = filter_text.lower()
        currentRow = self.softwareEntriesListWidget.currentRow()
        first_shown_software = 0
        for i in range(self.softwareEntriesListWidget.count()):
            software = self.softwareEntriesListWidget.getObjectEntry(i)
            """:type: SoftwareEntry"""
            if software:
                tutorial_count = len(software.tutorials)
                hidden_count = 0
                for j in range(tutorial_count):
                    tuto = software.tutorials[j]
                    name = tuto.name.lower()
                    desc = tuto.description.lower()

                    hide = name.find(filter_formatted) == -1 and \
                           desc.find(filter_formatted) == -1

                    if i == currentRow:
                        self.tutorialEntriesListWidget.item(j).setHidden(hide)
                    hidden_count += 1 if hide else 0

                hide_software = hidden_count == len(software.tutorials)
                if not first_shown_software and not hide_software:
                    first_shown_software = i
                self.softwareEntriesListWidget.item(i).setHidden(
                    hide_software)

        if not self.softwareEntriesListWidget.selectedIndexes() and \
            self.softwareEntriesListWidget.count() > 0:
            self.softwareEntriesListWidget.setCurrentRow(
                first_shown_software, QItemSelectionModel.SelectCurrent)

    def onLaunchButton(self):
        tutorial = self.tutorialEntriesListWidget.getCurrentObjectEntry()
        if tutorial:
            self.interpreter_process.start("plustutointerpreter {}".format(
                tutorial.filepath))

    def onIgnoreButton(self):
        software = self.softwareEntriesListWidget.getCurrentObjectEntry()
        """:type: SoftwareEntry"""
        tutorial = self.tutorialEntriesListWidget.getCurrentObjectEntry()
        """:type: TutorialEntry"""
        if software and tutorial:
            done_tutorials = self._done_tutorials()
            software_tuto = done_tutorials.get(software.desktopFilePath) or []
            if tutorial.key not in software_tuto:
                software_tuto.append(tutorial.key)
                done_tutorials[software.desktopFilePath] = software_tuto
                self._done_tutorials_saver(done_tutorials)

    def setTutorials(self, tutorials):
        """
        :param tutorials: dict[(str, str), List[Tutorial]]
        """
        self.softwareEntriesListWidget.setEntries(getSoftwareEntries(tutorials))

    def updateDoneTutorials(self, done_tutorials):
        selected_entry = self.softwareEntriesListWidget.getCurrentObjectEntry()
        if selected_entry:
            done_software_tutorials = done_tutorials.get(
                selected_entry.desktopFilePath, ())
            self.tutorialEntriesListWidget.updateDoneTutorials(
                done_software_tutorials)

    def updateTutorialsView(self, row):
        software = self.softwareEntriesListWidget.getObjectEntry(row)
        if software:
            self.tutorialEntriesListWidget.setEntries(software.tutorials)
            self.updateDoneTutorials(self._done_tutorials())

    def updateTutorialDescription(self, row):
        tutorial = self.tutorialEntriesListWidget.getObjectEntry(row)
        if tutorial:
            self.tutorialDescription.setText(tutorial.description)
