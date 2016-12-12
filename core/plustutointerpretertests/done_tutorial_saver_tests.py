import unittest
from os import remove
from os.path import join, exists

# noinspection PyProtectedMember
from libtuto.done_tutorials import _set_persistence_file, load_tutorials_done
from libtuto.query_tutorials import peekTutorial
from plustutointerpreter.done_tutorial_saver import DoneTutorialSaver


class DoneTutorialSaverTests(unittest.TestCase):
    PERSISTENCE_FILENAME = "persistence_test.json"
    TEST_TUTO_FILEPATH = join("plustutointerpretertests",
                              "tuto",
                              "test_tutorial.tuto")

    def test_file_doesnt_exist(self):
        self.assertRaises(FileNotFoundError, DoneTutorialSaver, "idontexist")

    def _set_persistence_file(self):
        _set_persistence_file(self.PERSISTENCE_FILENAME)

    def _clean_persistence_file(self):
        try:
            remove(self.PERSISTENCE_FILENAME)
        except FileNotFoundError:
            pass
        self.assertFalse(exists(self.PERSISTENCE_FILENAME))

    def test_save_as_done(self):
        self._clean_persistence_file()
        self._set_persistence_file()

        saver = DoneTutorialSaver(self.TEST_TUTO_FILEPATH)
        saver.save_as_done()
        self.assertTrue(exists(self.PERSISTENCE_FILENAME))

        peeked_tutorial = peekTutorial(self.TEST_TUTO_FILEPATH)
        desktop_filepath = peeked_tutorial[0][0]
        tutorial_name = peeked_tutorial[1]

        done_tutorials = load_tutorials_done()
        self.assertIn(desktop_filepath,
                      done_tutorials)
        self.assertIn(tutorial_name,
                      done_tutorials.get(desktop_filepath))
        self._clean_persistence_file()
