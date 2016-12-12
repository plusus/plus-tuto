import unittest
from os.path import abspath, join
from os.path import dirname

# noinspection PyProtectedMember
from libtuto.done_tutorials import count_tutorials_todo, _set_persistence_file
from libtuto.query_tutorials import TUTO_DIRS


def _set_persistence_folder(folder):
    _set_persistence_file(join(dirname(abspath(__file__)),
                               "persistence", folder, "persistence.json"))


class DoneTutorialsTests(unittest.TestCase):

    def test_count_tutorials_todo(self):
        TUTO_DIRS.clear()
        TUTO_DIRS.add(join(dirname(abspath(__file__)), "tuto"))

        _set_persistence_folder("empty")
        self.assertEqual(2, count_tutorials_todo())

        _set_persistence_folder("one")
        self.assertEqual(1, count_tutorials_todo())

        _set_persistence_folder("all")
        self.assertEqual(0, count_tutorials_todo())
