import unittest
import pathlib
from filum.database import Database, ItemAlreadyExistsError

sql_fp = pathlib.Path(__file__).parent.resolve() / 'test.sql'


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.d = Database()
        self.conn = self.d.connect_to_db()
        with open(sql_fp) as f:
            sql = f.read()
        self.conn.executescript(sql)

    def test_insert_row_raises_err_if_duplicate_permalink(self):
        test_thread = {
            'title': 'title',
            'body': 'body',
            'author': 'author',
            'id': 'id',
            'score': 1,
            'permalink': 'https://news.ycombinator.com/item?id=31618955',
            'source': 'source',
            'posted_timestamp': 1654404646,
            'saved_timestamp': 1654404646
        }
        with self.conn:
            with self.assertRaises(ItemAlreadyExistsError):
                self.d.insert_row(test_thread, 'ancestors')


if __name__ == '__main__':
    unittest.main()
