from pathlib import Path
import unittest
from unittest.mock import patch

from filum.config import FilumConfig


class TestConfig(unittest.TestCase):

    @patch('filum.config.FilumConfig.write_to_file')
    def test_creates_config_file_if_not_exists(self, write_to_file):
        config = FilumConfig()
        config.config_filepath_current = Path('/nonexistent/path')
        self.assertFalse(config.config_filepath_current.is_file())
        config.get_parser()
        write_to_file.assert_called_with(config.config_filepath_default)
        self.assertTrue(config.config_filepath_current.is_file())

    def test_update_config_file_if_output_section_not_exists(self):
        pass

    def test_append_new_options_to_config_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
