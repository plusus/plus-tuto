from PySide.QtGui import QFont, QListWidgetItem

from plustutocenter.proxy import Proxy


class BaseCustomEntriesWidget(Proxy):
    def __init__(self, delegate):
        """
        :type delegate: QListWidget
        """
        Proxy.__init__(self, delegate)

        self._font = QFont()
        self._object_entries = {}

    def createCustomEntry(self, model):
        """
        :rtype: QListWidgetItem
        """
        raise NotImplementedError()

    def getCurrentObjectEntry(self):
        return self.getObjectEntry(self.currentRow())

    def getObjectEntry(self, row):
        return self._object_entries.get(row)

    def getObjectEntries(self):
        return {self.getObjectEntry(row) for row in range(self.count())}

    def setEntries(self, entries):
        """
        :param entries: Iterable of custom type entry
        """
        self.clear()
        for i, entry in zip(range(len(entries)), entries):
            item = self.createCustomEntry(entry)
            item.setFont(self._font)
            self.addItem(item)
            self._object_entries[i] = entry
        self.setCurrentRow(0)
