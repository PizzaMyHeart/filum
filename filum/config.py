import configparser
from pathlib import Path

from logger.logger import create_logger

logger = create_logger()


class FilumConfig(object):
    def __init__(self):
        self.config_filepath_default = Path(__file__).parent.resolve() / 'config.ini'
        self.config_filepath_current = self.set_config_filepath(self.config_filepath_default)
        self.config = configparser.ConfigParser(inline_comment_prefixes=';', allow_no_value=True)
        self.config_output_options = {
            '; pager: Enable automatic piping of output into the default terminal pager.': None,
            '; pager_colours: Enable colour in pager output. Only works if the pager supports colour. Otherwise change this to false.': None,  # noqa: E501
            '; hyperlinks: Change this to true to render Markdown links in the terminal.': None,
            '; max_rows_without_pager: Number of table rows beyond which the table should be displayed in the pager.': None,  # noqa: E501
            'pager': 'true ',
            'pager_colours': 'true',
            'hyperlinks': 'false',
            'max_rows_without_pager': '10'
        }

    def get_parser(self):

        if not self.config_filepath_current.is_file():
            logger.debug('No config.ini yet.')
            self.create_config(self.config_output_options)
            self.write_to_file(self.config_filepath_default)
            self.config.read(self.config_filepath_current)
            self.config_filepath_current = self.set_config_filepath(self.config_filepath_default)
            return self.config

        self.config.read(self.config_filepath_current)

        if not self.config.has_section('output'):
            logger.debug('No "output" section yet.')
            self.config['output'] = {}
            self.create_config(self.config_output_options)
            self.write_to_file(self.config_filepath_current)
            self.config.read(self.config_filepath_current)
            return self.config

        self.update_config_output()

        return self.config

    def update_config_output(self):
        existing_keys = [key for key in self.config['output']]
        keys_to_add = [key for key in self.config_output_options if key not in existing_keys]
        logger.debug(f'Existing keys: {existing_keys}')
        logger.debug(f'The following keys are new: {keys_to_add}')
        new_config_options = {}
        if keys_to_add:
            for key, value in self.config_output_options.items():
                if key in keys_to_add:
                    new_config_options[key] = value
                else:
                    new_config_options[key] = self.config['output'][key]
            print(new_config_options)

            self.create_config(new_config_options)
            self.write_to_file(self.config_filepath_current)
            self.config.read(self.config_filepath_current)
            '''
                print(key)
                print(self.config_output_options[key])
                print(self.config['output'].values())
                # self.config['output'][key] = self.config_content[key]
                self.config.read_dict({
                    'output': {
                        key: self.config_output_options[key]
                    }
                })
                print(self.config['output'][key])
            self.write_to_file(self.config_filepath_current)
            '''

    def create_config(self, content):
        logger.debug(content)
        self.config['output'] = content
        '''
        for key in content.keys():
            self.config['output'][key] = content[key]
        '''

    def set_config_filepath(self, path):
        return path

    def write_to_file(self, path):
        with open(path, 'w') as config_file:
            self.config.write(config_file)


if __name__ == '__main__':
    config = FilumConfig()
    config.get_parser()
