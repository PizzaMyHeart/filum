import unittest
import pathlib
from filum.database import Database
from filum.exceptions import ItemAlreadyExistsError

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
            self.assertEqual(self.d.select_one_value_from_ancestors(1), self.permalink)

    def test_delete_ancestor(self):
        with self.conn:
            old_length = self.d.get_ancestors_length()
            self.d.delete_ancestor(1)
            new_length = self.d.get_ancestors_length()
            deleted_row = self.conn.execute('SELECT * FROM ancestors WHERE permalink = ?', (self.permalink,)).fetchone()
            self.assertIsNone(deleted_row)
            self.assertEqual(old_length, new_length + 1)

    def test_delete_descendants(self):
        with self.conn:
            sql = ('WITH a AS (SELECT id, ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) AS num FROM ancestors) '
                   'SELECT ancestor_id FROM descendants '
                   'WHERE ancestor_id IN (SELECT id FROM a WHERE num = ?);')
            ancestor_id = self.conn.execute(sql, (1,)).fetchall()[0][0]
            self.d.delete_descendants(1)
            deleted_rows = self.conn.execute(
                'SELECT * FROM descendants WHERE ancestor_id = ?', (ancestor_id,)
                ).fetchall()
            self.assertTrue(len(deleted_rows) == 0)

    def test_select_one_ancestor_without_conditions(self):
        with self.conn:
            results = self.d.select_one_ancestor(1)
            self.assertEqual(results['title'], 'Ask HN: Non-violent video games with great stories?')

    def test_select_one_ancestor_with_tag_condition(self):
        with self.conn:
            results = self.d.select_one_ancestor(1, cond='WHERE tags LIKE ?', where_param='python')
            self.assertEqual(
                results['title'],
                'Creating a class with all the elements specified in a file using ConfigParser')

    def test_select_all_descendants_without_conditions(self):
        with self.conn:
            results = self.d.select_all_descendants(1)
            ids = [row['id'] for row in results]
            self.assertEqual(''.join(set(ids)), '31618955')

    def test_select_all_descendants_with_condition(self):
        pass

    def test_search_one_tag_singular_instance(self):
        with self.conn:
            results = self.d.search('tags', 'games')
            results = [dict(i) for i in results]
            self.assertEqual(results[0]['permalink'], self.permalink)

    def tearDown(self) -> None:
        self.conn.rollback()
        self.conn.close()


if __name__ == '__main__':
    unittest.main()
