import json
import logging
from os import makedirs, listdir
from os.path import join, isfile, isdir, expanduser

from libtuto.config_file_data import ConfigFileData
from libtuto.position import positionFactory
from libtuto.size import Size
from libtuto.tutorial import Tutorial, TUTORIAL_VERSION, TutorialStep
from libtuto.zone import zoneFactory

HOME_TUTO_DIR = expanduser("~/.local/share/libtuto")
if not isdir(HOME_TUTO_DIR):
    makedirs(HOME_TUTO_DIR)

TUTO_DIRS = {HOME_TUTO_DIR}
DEFAULT_CONFIG_DIR = "/usr/share/libtuto/default_config"


class TutorialFileVersionMismatchException(Exception):
    pass


def isValidTutoFile(file):
    return isfile(file) and file.endswith(".tuto")


def _getI18nString(json_dict, key, language, default=None):
    """
    Acquire an internationalized string for a certain language and key in the
    raw json dictionary

    :type json_dict: dict[str, Any]
    :type key: str
    :type language: str
    :param default: Default value to return if no result is found
                    (Defaults to None)
    :type default: str | None
    :return: Internationalized key or default value provided
    """
    res = default
    if language:
        i18n_dict = json_dict.get(key + "_i18n")
        if i18n_dict:
            res = i18n_dict.get(language, default)
    return res


def _parseSteps(raw_steps, lang=None):
    """
    :type raw_steps: Iterable[dict]
    :param lang: (Optional) Descriptor of the language to query the step,
        without any specification of encoding or modifiers.
    :type lang: str | None
    :rtype: Iterable[TutorialStep]
    """

    def getI18nStringForStepKey(step, key):
        return _getI18nString(step, key, lang or "", step[key])

    steps = []
    for s in raw_steps:
        description_position = s.get("descriptionPosition")
        if description_position:
            description_position = positionFactory(*description_position)

        previous_click = s.get("previousStepClick")
        if previous_click:
            previous_click = positionFactory(*previous_click)

        steps.append(TutorialStep(
            getI18nStringForStepKey(s, "title"),
            getI18nStringForStepKey(s, "description"),
            zoneFactory(*s["actionZone"]),
            description_position,
            previous_click))
    return steps


def _loadTutorialAsJson(tutoFilepath):
    """
    Load a tuto file as a Json dict.
    The file version is checked to assert that the library can work with the
    returned dictionary (can assume fields of the supported version work)

    For further versions, populate necessary fields to assure backward
    compatibility and return an instance which can be safely used as a most
    recent version one.

    :type tutoFilepath: str
    :rtype: dict
    :raises: KeyError | TutorialFileVersionMismatchException
    """
    with open(tutoFilepath) as f:
        tuto_json = json.load(f)

    if tuto_json["tutofileversion"] > TUTORIAL_VERSION:
        raise TutorialFileVersionMismatchException(
            "The version found for '{}' was {} while the library supports "
            "up to version {}.".format(tutoFilepath,
                                       tuto_json["tutofileversion"],
                                       TUTORIAL_VERSION))

    # FUTURE: Handle backward compatibility here

    return tuto_json


def loadTutorial(tutoFilepath, language=None):
    """
    Load a tutorial instance from a *.tuto file.

    :param tutoFilepath: Filepath to a known *.tuto file
    :type tutoFilepath: str
    :param language: (Optional) Descriptor of the language to query the tutorial
        The descriptor is of the form lang_COUNTRY.ENCODING@MODIFIER, where only
        lang is required (the rest is omitted for this function).
        If not specified, the default language is used (English)
    :type language: str | None
    :return: 2-Tuple with application key (tuple of desktop file and application
             version) a and descriptor object for the tutorial
    :rtype: ((str, str), Tutorial)
    :raise: KeyError | TutorialFileVersionMismatchException
    """
    tuto_json = _loadTutorialAsJson(tutoFilepath)

    if language:
        language = language.split("_")[0]

    def getI18nStringForKey(key):
        return _getI18nString(tuto_json, key, language or "", tuto_json[key])

    return (tuto_json["application"],
            tuto_json["application_version"]), \
        Tutorial(tutoFilepath,
                 tuto_json["name"],
                 getI18nStringForKey("name"),
                 getI18nStringForKey("description"),
                 _parseSteps(tuto_json["steps"], language),
                 Size(tuto_json["width"], tuto_json["height"]),
                 getI18nStringForKey("windowTitleFilter"),
                 _parseDefaultConfigFiles(tuto_json["configFiles"]
                                          if "configFiles" in tuto_json
                                          else []))


def peekTutorial(tutoFilepath):
    """
    Peek the tuto file to retrieve only the path to the .desktop file, the
    application version and the name of the tutorial (in default English locale)

    :type tutoFilepath: str
    :rtype: ((str, str), str)
    :raise: KeyError | TutorialFileVersionMismatchException
    """
    tuto_json = _loadTutorialAsJson(tutoFilepath)
    return (tuto_json["application"], tuto_json["application_version"]), \
           tuto_json["name"]


def _tuto_files_generator(fct):
    """
    :type fct: (str) -> (str, Any)
    :rtype: (str, Any)
    """

    def get_tuto_files(path):
        for subpath in listdir(path):
            full_path = join(path, subpath)
            if isdir(full_path):
                # Recursive call to sub-directories
                for y in get_tuto_files(full_path):
                    yield y
            elif isValidTutoFile(full_path):
                try:
                    yield fct(full_path)
                except TutorialFileVersionMismatchException as e:
                    logging.warning(e)
                except KeyError as e:
                    logging.warning(
                        "Tuto file '{}' is malformed: Missing field {}".format(
                            full_path, e))

    for d in TUTO_DIRS:
        if isdir(d):
            for x in get_tuto_files(d):
                yield x


def _create_tutorials_dict(fct):
    """
    :type fct: (str) -> ((str, str), Any)
    :rtype: dict[(str, str), Any]
    """
    tutorials = {}
    for key, data in _tuto_files_generator(fct):
        if tutorials.get(key) is None:
            tutorials[key] = []
        tutorials[key].append(data)
    return tutorials


def _parseDefaultConfigFiles(config_files):
    config_list = []
    for config in config_files:
        config_list.append(ConfigFileData(
            expanduser(config.get("defaultConfigFile").replace(
                "#DEFAULT#", DEFAULT_CONFIG_DIR)),
            expanduser(config.get("fileToOverride"))))

    return config_list


def peekTutorials():
    """
    :return: Dictionary with key a tuple of desktop filepath and application
             version and value the list of tutorial keys
    :rtype: dict[(str, str), list[str]]
    """
    return _create_tutorials_dict(peekTutorial)


def getTutorials(language=None):
    """
    :return: Dictionary with key a tuple of desktop filepath and application
             version and value the list of tutorial instances
    :rtype: dict[(str, str), List[Tutorial]]
    """
    return _create_tutorials_dict(
        lambda path: loadTutorial(path, language=language))
