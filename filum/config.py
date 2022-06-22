import configparser
from pathlib import Path

from logger.logger import create_logger

logger = create_logger()


class FilumConfig(object):
    def __init__(self):
        self.config_filepath_default = Path(__file__).parent.resolve() / 'config.ini'
        self.config_filepath_current = self.set_config_filepath(self.config_filepath_default)
        self.config = configparser.ConfigParser(inline_comment_prefixes=';', allow_no_value=True)
        self.config_output_default_options = {
            '; pager: enable automatic piping of output into the default terminal pager. [true (default) | false]': None,  # noqa: E501
            '; pager_colours: enable colour in pager output. only works if the pager supports colour. otherwise set this to false. [true | false (default)]': None,  # noqa: E501
            '; hyperlinks: change this to true to render markdown links in the terminal. [true | false (default)]': None,  # noqa: E501
            '; max_rows_without_pager: number of table items beyond which the table should be displayed in the pager. [20 (default) | any integer]': None,  # noqa: E501
            'pager': 'true ',
            'pager_colours': 'false',
            'hyperlinks': 'false',
            'max_rows_without_pager': '20'
        }

    def get_config(self, reset=False):

        if not self.config_filepath_current.is_file():
            logger.debug('No config.ini yet.')
            filepath = self.config_filepath_default
        else:
            filepath = self.config_filepath_current

        self.config.read(filepath)

        if not self.config.has_section('output') or reset:
            self.config['output'] = {}

        logger.debug(f'Current output options: {self.config.items("output")}')
        new_options_to_add = self.get_new_options()

        if new_options_to_add:
            options = self.get_updated_output_section(new_options_to_add)
        else:
            options = self.config_output_default_options

        self._assign_to_output_section(options)
        self.write_to_file(filepath)
        self.config.read(self.config_filepath_current)

        return self.config

    def get_updated_output_section(self, options: list) -> dict:
        """Update the config options without overwriting existing values.

        """
        new_config_options = {}
        for key, value in self.config_output_default_options.items():
            if key in options:
                new_config_options[key] = value
            else:
                new_config_options[key] = self.config['output'][key]

        return new_config_options

    def get_new_options(self) -> list:
        existing_keys = [key for key in self.config['output']]
        keys_to_add = [key for key in self.config_output_default_options if key not in existing_keys]
        logger.debug(f'Existing keys: {existing_keys}')
        logger.debug(f'The following keys are new: {keys_to_add}')
        return keys_to_add

    def _assign_to_output_section(self, content):
        logger.debug(content)
        self.config['output'] = content

    def set_config_filepath(self, path):
        return path

    def write_to_file(self, path):
        logger.debug(f'Writing to {path}')
        with open(path, 'w') as config_file:
            self.config.write(config_file)


if __name__ == '__main__':
    config = FilumConfig()
    config.get_config()
