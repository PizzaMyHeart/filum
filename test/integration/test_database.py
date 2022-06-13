import unittest
import pathlib
from filum.database import Database, ItemAlreadyExistsError

sql_fp = pathlib.Path(__file__).parent.resolve() / 'test.sql'


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.d = Database('test')
        self.conn = self.d._conn
        with open(sql_fp) as f:
            sql = f.read()
        with self.conn:
            self.conn.executescript(sql)
        self.permalink = 'https://news.ycombinator.com/item?id=31618955'

    def test_insert_row_raises_err_if_duplicate_permalink(self):
        test_thread = {
            'title': 'title',
            'body': 'body',
            'author': 'author',
            'id': 'id',
            'score': 1,
            'permalink': self.permalink,
            'source': 'source',
            'posted_timestamp': 1654404646,
            'saved_timestamp': 1654404646
        }
        with self.conn:
            with self.assertRaises(ItemAlreadyExistsError):
                self.d.insert_row(test_thread, 'ancestors')

    def test_select_permalink_returns_correct_permalink(self):
        with self.conn:
            self.assertEqual(self.d.select_permalink(1), self.permalink)

    def test_delete_ancestor(self):
        with self.conn:
            old_length = self.d.get_ancestors_length()
            self.d.delete_ancestor(1)
            new_length = self.d.get_ancestors_length()
            deleted_row = self.conn.execute('SELECT * FROM ancestors WHERE permalink = ?', (self.permalink,)).fetchone()
            self.assertIsNone(deleted_row)
            self.assertEqual(old_length, new_length + 1)
            self.conn.rollback()

    def test_search_one_tag_singular_instance(self):
        with self.conn:
            results = self.d.search('tags', 'games')
            for count, row in enumerate(results):
                permalink = row['permalink']
            self.assertEqual(permalink, self.permalink)

    def tearDown(self) -> None:
        self.conn.close()


if __name__ == '__main__':
    unittest.main()
