

class ConfigFileData:
    def __init__(self, default_config_file, overridden_file):
        """
        :type default_config_file: str
        :type overridden_file: str
        """
        self._default_config_file = default_config_file
        self._overridden_file = overridden_file

    def default_config_file(self):
        return self._default_config_file

    def overridden_file(self):
        return self._overridden_file
