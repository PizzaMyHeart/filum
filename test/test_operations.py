import unittest
from unittest.mock import patch

from filum.operations import add, update, show_all, show_thread, delete, modify_tags, show_without_id, open_config


class TestOperations(unittest.TestCase):
    @patch('filum.operations.Controller.add_thread')
    @patch('filum.operations.Controller.download_thread')
    def test_adding_new_url_downloads_then_adds_thread(self, download_thread, add_thread):
        add('https://www.reddit.com/r/Python/comments/pzscwb/whats_your_strategy_on_refactoring/')
        download_thread.assert_called()
        add_thread.assert_called()

    def test_adding_existing_url_updates_record(self):
        pass


if __name__ == '__main__':
    unittest.main()
