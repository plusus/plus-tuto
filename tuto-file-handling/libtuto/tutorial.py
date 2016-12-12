from libtuto.position import Position
from libtuto.zone import Zone
from libtuto.size import Size
from libtuto.config_file_data import ConfigFileData

TUTORIAL_VERSION = 0


class TutorialStep:
    def __init__(self, title, description, actionZone,
                 descriptionPosition=None, previousStepClick = None):
        """
        :type title: str
        :type description: str
        :type actionZone: Zone
        :type descriptionPosition: Position
        :type previousStepClick: Position
        """
        self.title = title
        self.description = description
        self.actionZone = actionZone
        self.descriptionPosition = descriptionPosition
        self.previousStepClick = previousStepClick


class Tutorial:
    def __init__(self, filepath,
                 key,
                 name,
                 description,
                 steps,
                 window_size,
                 windowTitleFilter=None,
                 config_file_data=None):
        """
        :type filepath: str
        :type app_version: str
        :type key: str
        :type name: str
        :type description: str
        :type steps: collections.Iterable[TutorialStep]
        :type window_size: Size
        :type windowTitleFilter: str | None
        :type config_file_data: Iterable[ConfigFileData] | None
        """
        self.filepath = filepath
        self.key = key
        self.name = name
        self.description = description
        self.steps = steps
        self.window_size = window_size
        self.windowTitleFilter = windowTitleFilter
        self.config_file_data = config_file_data

    def __eq__(self, other):
        if isinstance(other, Tutorial):
            return False
        else:
            return self.key == other.key and \
                   self.name == other.name and \
                   self.description == other.description and \
                   self.steps == other.steps and \
                   self.windowTitleFilter == other.windowTitleFilter and \
                   self.config_file_data == other.config_file_data

    def __hash__(self):
        return hash((self.key, self.name))
