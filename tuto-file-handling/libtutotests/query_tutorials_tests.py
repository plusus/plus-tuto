# coding=utf-8

import os
import unittest
import shutil
from os.path import abspath
from os.path import dirname

from libtuto.tutorial import Tutorial, TutorialStep
from libtuto.zone import Zone
from libtuto.query_tutorials import loadTutorial, peekTutorial, peekTutorials, HOME_TUTO_DIR, \
    TutorialFileVersionMismatchException, TUTO_DIRS, getTutorials
from libtutotests.utils import project_root
from libtuto.config_file_data import ConfigFileData


TEST_FILE = os.path.join(project_root(), "tuto", "test_tutorial.tuto")
MALFORMED_FILE = os.path.join(project_root(), "tuto", "malformed_tuto.tuto")
UNSUPPORTED_FILE = os.path.join(project_root(), "tuto", "unsupported_tuto.tuto")
TEST_CONFIG_DIR = os.path.join(project_root(), "tuto", "config")
TEST_CONFIG_HOME_DIR = os.path.join(os.path.expanduser('~'), ".tutotest/")


def merge_dict(d1, d2):
    """
    :type d1: dict
    :type d2: dict
    """
    merged_d = d1.copy()
    merged_d.update(d2)
    return merged_d

BASE_FIELDS = {
    "width": 800,
    "height": 600,
    "windowTitleFilter": "Writer",
    "zone4_topLeft": (140, 275),
    "zone4_bottomRight": (700, 500),
    "step4_descriptionPosition": (40, 225),
    "step4_previousStepClick": (363, 72),
    "config1_default":os.path.expanduser("~/.tutotest/test_config1.conf"),
    "config1_to_override":os.path.expanduser("~/.tutotest/test_config2.conf"),
    "config2_to_override":os.path.expanduser("~/.tutotest/test_config3.ini")
}
""":type: dict"""

ENGLISH_FIELDS = merge_dict(BASE_FIELDS, {
    "name": "How to select a font",
    "description": "Choosing a nice font",
    "step4_title": "Free writing",
    "step4_description": "Have fun!"
})

FRENCH_FIELDS = merge_dict(BASE_FIELDS, {
    "name": u"Comment sélectionner une police",
    "description": u"Choisir une belle police",
    "step4_title": u"Écriture libre",
    "step4_description": u"Amusez-vous!"
})


class QueryTutorialsTests(unittest.TestCase):

    def _validate_fields(self, tuto_obj, fields):
        self.assertIsNotNone(tuto_obj)
        self.assertEqual(fields["name"], tuto_obj.name)
        self.assertEqual(fields["description"], tuto_obj.description)
        self.assertEqual(fields["width"], tuto_obj.window_size.width())
        self.assertEqual(fields["height"], tuto_obj.window_size.height())
        self.assertEqual(fields["windowTitleFilter"], tuto_obj.windowTitleFilter)

        self.assertEqual(5, len(tuto_obj.steps))

        tuto_obj_step4 = tuto_obj.steps[4]
        """:type: TutorialStep"""
        self.assertIsNotNone(tuto_obj_step4)
        zone = tuto_obj_step4.actionZone
        """:type: Zone"""
        self.assertEquals(fields["zone4_topLeft"], zone.topLeft())
        self.assertEquals(fields["zone4_bottomRight"], zone.bottomRight())
        self.assertEquals(fields["step4_title"], tuto_obj_step4.title)
        self.assertEquals(fields["step4_description"], tuto_obj_step4.description)

        description_position = tuto_obj_step4.descriptionPosition
        """:type: Position"""
        self.assertIsNotNone(description_position)
        self.assertEquals(fields["step4_descriptionPosition"], description_position.topLeft())

        previous_step_click = tuto_obj_step4.previousStepClick
        """:type: Position"""
        self.assertIsNotNone(previous_step_click)
        self.assertEquals(fields["step4_previousStepClick"], previous_step_click.topLeft())

        self.assertEqual(2, len(tuto_obj.config_file_data))
        config_file1 = tuto_obj.config_file_data[0]
        """:type: ConfigFileData"""
        self.assertIsNotNone(config_file1)
        self.assertEquals(fields["config1_default"], config_file1.default_config_file())
        self.assertEquals(fields["config1_to_override"], config_file1.overridden_file())

    def test_load_tutorial(self):
        tutorial = self._load_tutorial_with_config(TEST_FILE)
        self.assertIsNotNone(tutorial)
        self.assertTrue(tutorial[0])  # Not empty
        self.assertEqual(("/usr/share/applications/wps-office-wps.desktop",
                          "10.1.0.5672~a21"),
                         tutorial[0])
        self._validate_fields(tutorial[1], ENGLISH_FIELDS)

    def test_load_tutorial_nonexisting_lang(self):
        # Should default to english
        tutorial = self._load_tutorial_with_config(TEST_FILE, "idontexist")
        self._validate_fields(tutorial[1], ENGLISH_FIELDS)

    def test_load_tutorial_fr(self):
        tutorial = self._load_tutorial_with_config(TEST_FILE, "fr_CA.utf8")
        self._validate_fields(tutorial[1], FRENCH_FIELDS)

    def test_peek_tutorial(self):
        (application, name) = peekTutorial(TEST_FILE)
        self.assertIsNotNone(application)
        self.assertEqual(("/usr/share/applications/wps-office-wps.desktop",
                          "10.1.0.5672~a21"),
                         application)
        self.assertIsNotNone(name)
        self.assertEqual(ENGLISH_FIELDS["name"], name)

    def test_peek_malformed_tutorial(self):
        self.assertRaises(KeyError,
                          peekTutorial,
                          MALFORMED_FILE)

    def test_peek_unsupported_tutorial(self):
        self.assertRaises(TutorialFileVersionMismatchException,
                          peekTutorial,
                          UNSUPPORTED_FILE)

    def test_get_malformed_tutorial(self):
        self.assertRaises(KeyError,
                          loadTutorial,
                          MALFORMED_FILE)

    def test_load_unsupported_tutorial(self):
        self.assertRaises(TutorialFileVersionMismatchException,
                          loadTutorial,
                          UNSUPPORTED_FILE)

    def test_load_tutorials_no_raise(self):
        TUTO_DIRS.clear()
        TUTO_DIRS.add(os.path.join(dirname(abspath(__file__)), "tuto"))

        # No raise
        tutorials = getTutorials()

        # Doesn't have unsupported and malformed tutorials
        self.assertEqual(2, len(tutorials))

    def test_peek_tutorials_no_raise(self):
        TUTO_DIRS.clear()
        TUTO_DIRS.add(os.path.join(dirname(abspath(__file__)), "tuto"))

        # No raise
        tutorials = peekTutorials()

        # Doesn't have unsupported and malformed tutorials
        self.assertEqual(2, len(tutorials))

    @staticmethod
    def _load_tutorial_with_config(tuto_file_path, language=None):
        if os.path.isdir(TEST_CONFIG_HOME_DIR):
            shutil.rmtree(TEST_CONFIG_HOME_DIR)
        shutil.copytree(TEST_CONFIG_DIR, TEST_CONFIG_HOME_DIR)
        tutorial = loadTutorial(tuto_file_path, language)
        shutil.rmtree(TEST_CONFIG_HOME_DIR)
        return tutorial
