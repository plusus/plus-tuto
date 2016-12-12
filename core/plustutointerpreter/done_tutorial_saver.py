from libtuto.done_tutorials import load_tutorials_done, save_tutorials_done
from libtuto.query_tutorials import peekTutorial


class DoneTutorialSaver:
    def __init__(self, tuto_filepath):
        """
        :param tuto_filepath: Filepath to the tutorial file
        """
        peeked_tutorial = peekTutorial(tuto_filepath)
        self._desktop_file = peeked_tutorial[0][0]
        self._tuto_name = peeked_tutorial[1]

    def save_as_done(self):
        """
        Save the tutorial as done for the current user
        :return:
        """
        tutos = load_tutorials_done()
        done_list = tutos.get(self._desktop_file) \
            if self._desktop_file in tutos else list()
        if self._tuto_name not in done_list:
            done_list.append(self._tuto_name)
        tutos[self._desktop_file] = done_list
        save_tutorials_done(tutos)
