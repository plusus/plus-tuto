from shutil import copyfile, move
from libtuto.config_file_data import ConfigFileData
from os.path import isfile


class InvalidConfigList(Exception):
    pass


class ConfigFileOverride:
    def __init__(self, override_data_list):
        """
        :type override_data_list: List[ConfigFileData]
        """
        if not override_data_list:
            raise InvalidConfigList("Argument override_data_list is invalid: {}"
                                    .format(override_data_list))

        self._override_data_list = override_data_list
        self._create_backups()
        self._override_config_files()

    def _create_backups(self):
        for override_data in self._override_data_list:
            config = override_data.overridden_file()
            if isfile(config):
                override_data.backup_file = config + ".backup"
                """
                :type config: str
                """
                copyfile(config, config + ".backup")

    def _override_config_files(self):
        for override_data in self._override_data_list:
            default_config = override_data.default_config_file()
            file_to_override = override_data.overridden_file()

            if isfile(default_config):
                copyfile(default_config, file_to_override)
            else:
                with open(file_to_override, "w+") as text_file:
                    text_file.write(default_config)

    def restore_backed_up_files(self):
        for override_data in self._override_data_list:
            if hasattr(override_data, "backup_file"):
                move(override_data.backup_file, override_data.overridden_file())
