from xdg.IconTheme import getIconPath

from PySide.QtGui import QListWidget, QListWidgetItem, QIcon

from plustutocenter.qt.widgets.base_custom_entries_widget import \
    BaseCustomEntriesWidget


class SoftwareEntry:
    def __init__(self, name, iconPath, tutorials, desktopFilePath):
        """
        :type: str
        :type: str
        :type: List[Tutorial]
        :type: str
        """
        self.name = name
        self.iconPath = iconPath
        self.tutorials = tutorials
        self.desktopFilePath = desktopFilePath

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, SoftwareEntry):
            return False
        else:
            return \
                self.name == other.name and \
                self.iconPath == other.iconPath and \
                self.tutorials == other.tutorials and \
                self.desktopFilePath == other.desktopFilePath

    def __hash__(self):
        return hash((self.name,
                     self.iconPath,
                     hash(t for t in self.tutorials),
                     self.desktopFilePath))


class SoftwareEntriesWidget(BaseCustomEntriesWidget):
    def __init__(self, delegate):
        """
        :type delegate: QListWidget
        """
        super().__init__(delegate)
        self._font.setPointSize(14)

    def createCustomEntry(self, model):
        """
        :type model: SoftwareEntry
        :rtype: QListWidgetItem
        """
        return QListWidgetItem(
            QIcon(getIconPath(model.iconPath, theme="gnome")),
            model.name)
