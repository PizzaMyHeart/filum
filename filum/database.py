"""Contains the Database class that interacts with the SQLite database."""

import pathlib
import sqlite3
from sqlite3 import IntegrityError, OperationalError

from logger.logger import create_logger

from filum.exceptions import ItemAlreadyExistsError
from filum.helpers import current_timestamp, qmarks

logger = create_logger()


class Database(object):
    # TODO: Return results as dicts or lists of dicts
    def __init__(self, db='prod'):
        if db == 'prod':
            db_name = pathlib.Path(__file__).parent.resolve() / 'filum.db'
        elif db == 'test':
            db_name = ':memory:'
        self._conn = self.connect_to_db(db_name)
        # self._conn.set_trace_callback(print)
        self.sql = dict([
            ('ancestors_sequential', 'SELECT *, ROW_NUMBER() OVER (ORDER BY row_id DESC) as num FROM ancestors')  # noqa: E501
            ])

        with self._conn:
            self.create_table_ancestors()
            self.create_table_descendants()

    def connect_to_db(self, db_name):
        """Return a connection object to interact with the database.

        Args:
            db_name: The path to the database.

        Returns:
            conn: An SQLite Connection object.
        """
        logger.debug(db_name)
        conn = sqlite3.connect(db_name)
        # Return Row object from queries to allow accessing columns by name
        conn.row_factory = sqlite3.Row
        return conn

    def create_table_ancestors(self):
        with self._conn:
            sql = (
                'CREATE TABLE IF NOT EXISTS ancestors'
                '(row_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'id TEXT, title TEXT, body TEXT, posted_timestamp INTEGER, saved_timestamp INTEGER, '
                'score INTEGER, item_permalink TEXT UNIQUE, parent_permalink TEXT, author TEXT, source TEXT, '
                'web_archive_url TEXT, tags TEXT);')
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
                if 'UNIQUE' in str(err):
                    raise ItemAlreadyExistsError(thread['title'])

    def update_ancestor(self, thread: dict) -> int:
        """Update a row in the 'ancestors' table.

        Returns an ID (a value returned by the SQLite row_number window function) which
        is used later to delete the associated descendants."""

        with self._conn:
            sql = 'UPDATE ancestors SET saved_timestamp = ?, score = ? WHERE item_permalink = ?'
            try:
                self._conn.execute(sql, (
                    current_timestamp(),
                    thread['score'],
                    thread['item_permalink']
                )
                )
                id: int = self._conn.execute(
                            ('SELECT ROW_NUMBER() OVER (ORDER BY saved_timestamp DESC) FROM ancestors WHERE item_permalink = ?'),  # noqa: E501
                            (thread['item_permalink'], )
                            ) \
                    .fetchone()[0]
            except OperationalError as err:
                print(err)
            return id

    def select_one_value_from_ancestors(self, id: int, column: str) -> str:
        """Returns the a column value from the 'ancestors' table."""
        with self._conn:
            sql = f'WITH a AS ({self.sql["ancestors_sequential"]}) SELECT {column} FROM a WHERE num = ?'
            value = self._conn.execute(sql, (id, )).fetchone()[0]
            return value

    def select_all_ancestors(self):
        with self._conn:
            sql = self.sql['ancestors_sequential']
            results = self._conn.execute(sql).fetchall()

            return results

    def select_one_ancestor(self, id: int, cond='', where_param='') -> sqlite3.Row:
        values = self.get_params_tuple(id, where_param)
        with self._conn:
            sql = f'WITH a AS ({self.sql["ancestors_sequential"]} {cond})SELECT * FROM a WHERE num = (?)'
            results = self._conn.execute(sql, values).fetchone()
        return results

    def select_all_descendants(self, id: int, cond='', where_param='') -> sqlite3.Row:
        values = self.get_params_tuple(id, where_param)
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

    def get_params_tuple(self, id: int, where_param) -> tuple:
        """Returns a tuple of parameters to be substituted into SQL query placeholders
        used by select_one_ancestor and select_all_descendants.
        """
        if where_param != '':
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
            sql_ancestors = (
                f'WITH A AS ({self.sql["ancestors_sequential"]})'
                'DELETE FROM ancestors WHERE id IN (SELECT id FROM a WHERE num = ?)'
            )
            self._conn.execute(sql_ancestors, (id,))

    def delete_descendants(self, id: int) -> None:
        with self._conn:
            sql_descendants = (
                f'WITH A AS ({self.sql["ancestors_sequential"]})'
                'DELETE FROM descendants WHERE ancestor_id IN (SELECT id FROM a WHERE num = ?)'
            )
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

    def _check_column_exists(self, column: str, table: str) -> bool:
        """Checks whether a column exists in a given table.
        Returns a Boolean.
        """

        with self._conn:
            sql = f'PRAGMA table_info({table})'
            results = self._conn.execute(sql).fetchall()
            columns = [dict(result)['name'] for result in results]
            if column in columns:
                return True
            return False

    def _create_new_column(self, column: str, table: str = 'ancestors'):
        try:
            with self._conn:
                sql = f'ALTER TABLE {table} ADD COLUMN {column} TEXT'
                self._conn.execute(sql)
        except OperationalError as err:
            print(err)

    def create_column_if_not_exists(func):
        def wrapped(self, *args, **kwargs):
            column = kwargs['column']
            table = kwargs['table']
            if not self._check_column_exists(column, table):
                self._create_new_column(column, table)
            func(self, *args, **kwargs)
        return wrapped

    # Non-core features. These functions add the relevant column if it does not exist.
    @create_column_if_not_exists
    def update_web_archive_link(self, item_permalink: str, web_archive_url: str, column, table) -> None:
        """Given an ancestor item's permalink, update its web archive URL.

        Args:
            item_permalink: The permalink of the saved item
            web_archive_url: The URL of the item saved in the web archive
            column: The name of the column that stores web_archive_url
            table: The name of the containing table

        Returns:
            None
        """

        with self._conn:
            sql = 'UPDATE ancestors SET web_archive_url = ? WHERE item_permalink = ?'
            try:
                self._conn.execute(sql, (web_archive_url, item_permalink))
            except OperationalError as err:
                print(err)


def main():

    db = Database()
    help(db)


if __name__ == '__main__':
    main()
