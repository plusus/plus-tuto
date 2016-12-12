import locale
from libtuto.done_tutorials import load_tutorials_done, save_tutorials_done
from libtuto.persistence_dbus import register_todo_update
from libtuto.query_tutorials import getTutorials
from plustutocenter.definitions.mvp import Controller, View


class ConcreteController(Controller):
    """
    Controller for the application
    """

    def __init__(self):
        self._view = None
        """:type: View"""
        self._tutorials = getTutorials(locale.getdefaultlocale()[0])
        self._done_tutorials = load_tutorials_done()
        register_todo_update(self.updateDoneTutorials)

    def setView(self, view):
        """
        :type view: View
        """
        self._view = view

    def getTutorials(self):
        """
        :rtype: dict[(str, str), List[Tutorial]]
        """
        return self._tutorials

    def getDoneTutorials(self):
        """
        :return: Dictionary with keys being the path desktop files and values
                 the list of tutorial keys done
        :rtype: dict[str, list[str]]
        """
        return self._done_tutorials

    def updateDoneTutorials(self):
        """
        Update the cached dictionary of tutorials marked as done.
        This method also alerts the view to update the tutorials done it is
        displaying.
        Assumes the view exists.
        """
        assert self._view
        self._done_tutorials = load_tutorials_done()
        self._view.updateDoneTutorials()

    def saveDoneTutorials(self, done_tutorials):
        """
        Saves a version of the tutorials marked as done, also settings it as
        cached dictionary.
        Assumes the view exists.
        :type done_tutorials: dict[str, list[str]]
        """
        assert self._view
        self._done_tutorials = done_tutorials
        save_tutorials_done(done_tutorials)
        self._view.updateDoneTutorials()

    def startApp(self):
        """
        Start the application's view, assuming it exists.
        """
        assert self._view
        self._view.launch()
