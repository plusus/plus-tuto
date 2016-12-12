import json
import unittest
from os import remove
from unittest.mock import MagicMock, Mock

from os.path import exists

from libtuto.done_tutorials import _set_persistence_file, save_tutorials_done
from plustutocenter.controller.concretecontroller import ConcreteController
from plustutocenter.definitions.mvp import View


class CustomPersistence:

    PERSISTENCE_FILENAME = "persistence_tests.json"

    def __enter__(self):
        _set_persistence_file(self.PERSISTENCE_FILENAME)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            remove(self.PERSISTENCE_FILENAME)
        except FileNotFoundError:
            pass


class ConcreteControllerTests(unittest.TestCase):

    def _set_view_mock(self):
        view_mock = Mock(spec=View)
        # noinspection PyTypeChecker
        self.controller.setView(view_mock)
        return view_mock

    def setUp(self):
        self.controller = ConcreteController()

    def test_init(self):
        self.assertIsNone(self.controller._view)
        done_tutorials = self.controller.getDoneTutorials()
        self.assertIsNotNone(done_tutorials)

    def test_set_view(self):
        view_mock = self._set_view_mock()
        self.assertIs(view_mock, self.controller._view)

    def test_start(self):
        # No view
        self.assertRaises(AssertionError, self.controller.startApp)
        view_mock = self._set_view_mock()
        self.controller.startApp()
        self.assertTrue(view_mock.launch.called)

    def test_save_done_tutorials(self):
        self.assertRaises(AssertionError, self.controller.updateDoneTutorials)
        view_mock = self._set_view_mock()

        with CustomPersistence():
            done_tutorials = {"some.desktop": ["some tutorial"]}
            self.controller.saveDoneTutorials(done_tutorials)
            self.assertEquals(done_tutorials,
                              self.controller.getDoneTutorials())
            self.assertTrue(view_mock.updateDoneTutorials.called)

            with open(CustomPersistence.PERSISTENCE_FILENAME, 'r') as f:
                done_tutorials_json = json.load(f)

            self.assertIn("some.desktop", done_tutorials_json)
            self.assertEquals(["some tutorial"],
                              done_tutorials.get("some.desktop"))

    def test_update_done_tutorials(self):
        self.assertRaises(AssertionError, self.controller.updateDoneTutorials)
        view_mock = self._set_view_mock()

        with CustomPersistence():
            done_tutorials = {"some.desktop": ["some tutorial"]}
            save_tutorials_done(done_tutorials)

            self.controller.updateDoneTutorials()
            self.assertEquals(done_tutorials,
                              self.controller.getDoneTutorials())
            self.assertTrue(view_mock.updateDoneTutorials.called)
