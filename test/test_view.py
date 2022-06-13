import unittest
from unittest.mock import patch

from filum.view import RichView

view = RichView()


class TestView(unittest.TestCase):
    def setUp(self) -> None:
        self.row_dict = {
            'row_id': 2,
            'id': '31618955',
            'title': 'Ask HN: Non-violent video games with great stories?',
            'body': None,
            'posted_timestamp': 1654336734,
            'saved_timestamp': 1654548965.026366,
            'score': 259,
            'permalink': 'https://news.ycombinator.com/item?id=31618955',
            'author': 'recvonline',
            'source': 'hn',
            'tags': 'games',
            'num': 1
            }

    def test_stringify(self):
        query_result = {
            'num': 1,
            'title': 'Some title',
            'posted_timestamp': 1622404036,
            'saved_timestamp': 1654005888.148201,
            'score': 0,
            'source': 'hn',
            'tags': None
        }
        result_values = query_result.values()

        stringified = ('1', 'Some title', '1622404036',
                       '1654005888.148201', '0', 'hn', 'None')

        self.assertEqual(view.stringify(result_values), stringified)

    @patch('filum.view.Table.add_column')
    def test_create_table_makes_seven_columns(self, mock_method):
        row_list = [self.row_dict]
        view.create_table(row_list)
        self.assertEqual(mock_method.call_count, 7)


if __name__ == '__main__':
    unittest.main()
