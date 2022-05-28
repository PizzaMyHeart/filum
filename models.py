import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError
import pprint

db_name = 'filum'

class ItemAlreadyExistsError(Exception):
    pass

class Model_db(object):
    def __init__(self):
        self._conn = self.connect_to_db('filum')
        with self._conn:
            self.create_table_ancestors()
            self.create_table_descendants()

    def connect_to_db(self, db=None):
        if db is None:
            my_db = ':memory:'
            print('New connection to in-memory SQLite db')
        else:
            my_db = f'{db}.db'
        conn = sqlite3.connect(my_db)
        # Return Row object from queries to allow accessing columns by name
        conn.row_factory = sqlite3.Row
        return conn

    def create_table_ancestors(self):
        with self._conn:
            sql = '''CREATE TABLE IF NOT EXISTS ancestors 
                    (row_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    id TEXT, title TEXT, body TEXT, posted_timestamp INTEGER, saved_timestamp INTEGER, 
                    score INTEGER, permalink TEXT UNIQUE, num_comments INTEGER, author TEXT, source TEXT,
                    tags TEXT
                    );'''
            try:
                self._conn.execute(sql)
            except OperationalError as err:
                print(err)

    def create_table_descendants(self):
        with self._conn:
            sql = '''CREATE TABLE IF NOT EXISTS descendants 
                    (row_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    ancestor_id INTEGER REFERENCES ancestors(row_id), 
                    id TEXT,
                    parent_id TEXT,
                    text TEXT, permalink TEXT, 
                    author TEXT, author_id TEXT, is_submitter INTEGER,
                    upvotes INTEGER, downvotes INTEGER, score INTEGER, timestamp INTEGER,
                    depth INTEGER, path TEXT,
                    FOREIGN KEY (parent_id) REFERENCES descendants(id));'''
            try:
                self._conn.execute(sql)
            except OperationalError as err:
                print(err)

    def insert_row(self, thread:dict, table_name):
        with self._conn:
            print(self)
            columns = thread.keys()
            values = tuple(thread.values())
            to_insert = f'''({', '.join(columns)}) VALUES ({', '.join(['?']*len(columns))})'''
            sql = f'''INSERT INTO {table_name} ''' + to_insert
            try:
                self._conn.executemany(sql, (values,))
                self._conn.commit()
            except IntegrityError as err:
                print(err)
                if 'UNIQUE' in str(err):
                    raise ItemAlreadyExistsError

    def select_one_ancestor(self, columns, id):
        with self._conn:
            columns = ', '.join(columns)
            sql = f'''SELECT {columns} FROM ancestors WHERE row_id = ?'''
            results = self._conn.execute(sql, (id,)).fetchall()

            return results
    
    def select_all_ancestors(self):
        with self._conn:
            sql = 'SELECT row_id, title, posted_timestamp, saved_timestamp, score, source, tags FROM ancestors;'
            results = self._conn.execute(sql).fetchall()
            return results

    def select_all_descendants(self, id) -> list:
        with self._conn:
            sql = f'''
                WITH joined AS (
                    SELECT d.depth, d.row_id, a.id, d.text, d.author, a.row_id AS key 
                    FROM descendants d 
                    JOIN ancestors a 
                    ON d.ancestor_id = a.id
                    ) 
                SELECT * FROM joined WHERE key = (?)
            '''
            results = self._conn.execute(sql, (id,)).fetchall()
            return results
       
def main():

    db = Model_db()

if __name__ == '__main__':
    main()