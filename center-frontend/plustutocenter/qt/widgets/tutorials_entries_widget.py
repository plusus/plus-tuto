from PySide.QtGui import QListWidget, QListWidgetItem, QIcon

from plustutocenter.qt.widgets.base_custom_entries_widget import \
    BaseCustomEntriesWidget
from plustutocenter.utils import resource_filepath


class TutorialEntry(QListWidgetItem):

    def __init__(self, tutorial):
        """
        :type tutorial: Tutorial
        """
        super().__init__(tutorial.name)
        self.tutorial = tutorial
        self._done = False
        self.updateIcon()

    def setDone(self, done):
        if self._done != done:
            self._done = done
            self.updateIcon()

    def updateIcon(self):
        self.setIcon(QIcon(resource_filepath("check_enable.png"))
                     if self._done else
                     QIcon(resource_filepath("check_disable.png")))


class TutorialEntriesWidget(BaseCustomEntriesWidget):
    def __init__(self, delegate):
        """
        :type delegate: QListWidget
        """
        super().__init__(delegate)
        self._customEntries = {}

    def createCustomEntry(self, model):
        """
        :type model: Tutorial
        :return: QListWidgetItem
        """
        customEntry = TutorialEntry(model)
        self._customEntries[model] = customEntry
        return customEntry

    def updateDoneTutorials(self, done_tutorials):
        """
        Set the tutorials to indicate they are done
        :type done_tutorials: set[Tutorial]
        """
        for o in self.getObjectEntries():
            tutorialEntry = self._customEntries[o]
            tutorialEntry.setDone(
                tutorialEntry.tutorial.key in done_tutorials)
