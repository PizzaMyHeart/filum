"""Contains a Database class that interacts with the SQLite database."""

import sqlite3
from sqlite3 import OperationalError, IntegrityError
import pathlib
from filum.helpers import qmarks, current_timestamp


class ItemAlreadyExistsError(Exception):
    """Custom exception that is raised when attempting
    to add an item with a permalink that already exists in the database."""

    pass


class Database(object):
    def __init__(self, db='prod'):
        if db == 'prod':
            db_name = pathlib.Path(__file__).parent.resolve() / 'filum.db'
        elif db == 'test':
            db_name = ':memory:'
        self._conn = self.connect_to_db(db_name)
        # self._conn.set_trace_callback(print)
        self.sql = dict([
            ('ancestors_sequential', 'SELECT *, ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) as num FROM ancestors')  # noqa: E501
            ])

        with self._conn:
            self.create_table_ancestors()
            self.create_table_descendants()

    def connect_to_db(self, db=None):
        """Return a connection object to interact with the database."""

        conn = sqlite3.connect(db)
        # Return Row object from queries to allow accessing columns by name
        conn.row_factory = sqlite3.Row
        return conn

    def create_table_ancestors(self):
        with self._conn:
            sql = (
                'CREATE TABLE IF NOT EXISTS ancestors'
                '(row_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'id TEXT, title TEXT, body TEXT, posted_timestamp INTEGER, saved_timestamp INTEGER, '
                'score INTEGER, permalink TEXT UNIQUE, author TEXT, source TEXT,'
                'tags TEXT);')
            try:
                self._conn.execute(sql)
            except OperationalError as err:
                print(err)

    def create_table_descendants(self):
        with self._conn:
            sql = (
                'CREATE TABLE IF NOT EXISTS descendants'
                '(row_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'ancestor_id INTEGER REFERENCES ancestors(row_id),'
                'id TEXT, parent_id TEXT, text TEXT, permalink TEXT, '
                'author TEXT, author_id TEXT, score INTEGER, timestamp INTEGER, '
                'depth INTEGER);')
            try:
                self._conn.execute(sql)
            except OperationalError as err:
                print(err)

    def insert_row(self, thread: dict, table_name):
        """Insert a row into a table."""

        with self._conn:
            columns = thread.keys()
            values = tuple(thread.values())
            columns_to_insert = f'''({', '.join(columns)}) VALUES ({qmarks(columns)})'''
            sql = f'''INSERT INTO {table_name} ''' + columns_to_insert
            try:
                self._conn.executemany(sql, (values,))
                self._conn.commit()
            except IntegrityError as err:
                # print(err)
                if 'UNIQUE' in str(err):
                    raise ItemAlreadyExistsError

    def update_ancestor(self, thread: dict) -> int:
        """Update a row in the 'ancestors' table.

        Returns an ID (a value returned by the SQLite row_number window function) which
        is used later to delete the associated descendants."""

        with self._conn:
            sql = 'UPDATE ancestors SET saved_timestamp = ?, score = ? WHERE permalink = ?'
            try:
                self._conn.execute(sql, (
                    current_timestamp(),
                    thread['score'],
                    thread['permalink']
                )
                )
                id: int = self._conn.execute(
                            ('SELECT ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) FROM ancestors WHERE permalink = ?'),  # noqa: E501
                            (thread['permalink'], )
                            ) \
                    .fetchone()[0]
            except OperationalError as err:
                print(err)
            return id

    def select_permalink(self, id: int) -> str:
        """Returns the permalink of a row in the 'ancestors' table."""
        with self._conn:
            sql = f'WITH a AS ({self.sql["ancestors_sequential"]}) SELECT permalink FROM a WHERE num = ?'
            permalink = self._conn.execute(sql, (id, )).fetchone()[0]
            return permalink

    def select_all_ancestors(self):
        with self._conn:
            sql = self.sql['ancestors_sequential']
            results = self._conn.execute(sql).fetchall()

            return results

    def select_one_ancestor(self, id: int, cond='', **kwargs) -> sqlite3.Row:
        values = self.get_params_tuple(id, kwargs)
        with self._conn:
            sql = f'WITH a AS ({self.sql["ancestors_sequential"]} {cond})SELECT * FROM a WHERE num = (?)'
            results = self._conn.execute(sql, values).fetchone()
        return results

    def select_all_descendants(self, id: int, cond='', **kwargs) -> sqlite3.Row:
        values = self.get_params_tuple(id, kwargs)
        with self._conn:
            sql = (
                'WITH joined AS ('
                'SELECT d.depth, d.row_id, d.score, d.timestamp, a.id, d.text, d.author, a.num AS key '
                'FROM descendants d '
                f'JOIN ({self.sql["ancestors_sequential"]} a {cond}) a '
                'ON d.ancestor_id = a.id) '
                'SELECT * FROM joined WHERE key = ?'
            )
            results = self._conn.execute(sql, values).fetchall()
            return results

    def get_params_tuple(self, id: int, kwargs) -> tuple:
        """Returns a tuple of parameters to be substituted into SQL query placeholders
        used by select_one_ancestor and select_all_descendants.
        """
        if 'where_param' in kwargs.keys():
            where_param = kwargs['where_param']
            values = (where_param, id)
        else:
            values = (id, )
        return values

    def get_ancestors_length(self) -> int:
        with self._conn:
            sql = 'SELECT rowid FROM ancestors;'
            results = self._conn.execute(sql).fetchall()
            if results is not None:
                return len(results)
            else:
                return 0

    def delete_ancestor(self, id: int) -> None:
        with self._conn:
            sql_ancestors = '''
                                WITH a AS (
                                    SELECT id, ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) AS num FROM ancestors
                                )
                                DELETE FROM ancestors WHERE id IN (SELECT id FROM a WHERE num = ?)
                                '''
            self._conn.execute(sql_ancestors, (id,))

    def delete_descendants(self, id: int) -> None:
        with self._conn:
            sql_descendants = '''
                                WITH a AS (
                                    SELECT id, ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) AS num FROM ancestors
                                )
                                DELETE FROM descendants
                                WHERE ancestor_id IN (SELECT id FROM a WHERE num = ?);
                                '''
            self._conn.execute(sql_descendants, (id,))

    def get_all_tags(self):
        with self._conn:
            sql = 'SELECT tags FROM ancestors'
            rows = self._conn.execute(sql).fetchall()
        return rows

    def get_tags(self, id: int) -> str:
        with self._conn:
            sql = (
                f'WITH a AS ({self.sql["ancestors_sequential"]}) '
                'SELECT tags FROM a WHERE num = ?'
            )

            tags = self._conn.execute(sql, (id, )).fetchone()[0]
        return tags

    def update_tags(self, id: int, tags: str):
        """Update (either add or delete) tags based on user input."""
        with self._conn:
            sql = (
                f'WITH a AS ({self.sql["ancestors_sequential"]}) '
                'UPDATE ancestors SET tags = ? WHERE id IN (SELECT id FROM a WHERE num = ?)'
            )
            self._conn.execute(sql, (tags, id))

    def search(self, column: str, searchstr: str):
        """Search a column in the 'ancestors' table for a user-supplied string."""
        param = f'%{searchstr}%'
        with self._conn:
            sql = (
                'SELECT ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) as num, '
                f'* FROM ancestors WHERE {column} LIKE ?'
            )
            results = self._conn.execute(sql, (param, )).fetchall()
        return results


def main():

    db = Database()
    help(db)


if __name__ == '__main__':
    main()
