import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError
import pprint

db_name = 'filum'

class ItemAlreadyExistsError(Exception):
    pass

def connect_to_db(db=None):
    if db is None:
        my_db = ':memory:'
        print('New connection to in-memory SQLite db')
    else:
        my_db = f'{db}.db'
    conn = sqlite3.connect(my_db)
    return conn

def connect(func):
    """https://www.giacomodebidda.com/posts/mvc-pattern-in-python-sqlite/
    
    """
    def inner_func(conn, *args, **kwargs):
        try:
            conn.execute('SELECT name FROM sqlite_temp_master WHERE type="table";')
        except (AttributeError, ProgrammingError):
            conn = connect_to_db(db_name)
        return func(conn, *args, **kwargs)
    return inner_func

def disconnect_from_db(db=None, conn=None):
    """Explicitly close a connection rather than waiting for timeout
    """
    if db is not db_name:
        print('Attempting to disconnect from the wrong database.')
    if conn is not None:
        conn.close()



@connect
def create_table_ancestors(conn):
    sql = '''CREATE TABLE IF NOT EXISTS ancestors 
            (row_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            id TEXT, title TEXT, body TEXT, posted_timestamp INTEGER, saved_timestamp INTEGER, 
            score INTEGER, permalink TEXT UNIQUE, num_comments INTEGER, author TEXT, source TEXT,
            tags TEXT
            );'''
    # TODO: Add timestamp at time of saving the thread
    try:
        conn.execute(sql)
    except OperationalError as err:
        print(err)



@connect
def create_table_descendants(conn):
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
        conn.execute(sql)
    except OperationalError as err:
        print(err)

@connect
def insert_row(conn, thread:dict, table_name):
    columns = thread.keys()
    values = tuple(thread.values())
    #pprint.pprint(thread)
    to_insert = f'''({', '.join(columns)}) VALUES ({', '.join(['?']*len(columns))})'''
    sql = f'''INSERT INTO {table_name} ''' + to_insert
    #print(sql)
    try:
        conn.executemany(sql, (values,))
        conn.commit()
    except IntegrityError as err:
        print(err)
        if 'UNIQUE' in str(err):
            raise ItemAlreadyExistsError

@connect
def select_row(conn, columns, table_name, id):
    sql = f'''SELECT ({', '.join(['?']*len(columns))}) FROM (?) WHERE id = (?)'''
    values = columns + tuple(table_name) + tuple(id)
    results = conn.execute(sql, (values)).fetchall()
    # TODO: Rewrite this to return a dict

    return results


@connect
def select_all_ancestors(conn):
    sql = 'SELECT row_id, title, posted_timestamp, saved_timestamp, score, source, tags FROM ancestors;'
    results = conn.execute(sql).fetchall()
    return results

@connect
def select_all_descendants(conn, id) -> list:
    sql = f'''
        WITH joined AS (
            SELECT d.depth, d.row_id, a.id, d.text, d.author, a.row_id AS key 
            FROM descendants d 
            JOIN ancestors a 
            ON d.ancestor_id = a.id
            ) 
        SELECT * FROM joined WHERE key = (?)
    '''
    results = conn.execute(sql, (id,)).fetchall()
    return results


def main():

    conn = connect_to_db('filum')

    create_table_ancestors(conn)
    create_table_descendants(conn)

    conn.close()

class Model_db(object):
    def __init__(self):
        self._connection = connect_to_db('filum')
        create_table_ancestors(self._connection)
        create_table_descendants(self._connection)
    
    def insert_row(self, thread, table_name):
        return insert_row(self._connection, thread, table_name)

    def select_row(self, columns, table_name, id):
        return select_row(self._connection, columns, table_name, id)

    def select_all_ancestors(self):
        return select_all_ancestors(self._connection)

    def select_all_descendants(self, ancestor):
        return select_all_descendants(self._connection, ancestor)


if __name__ == '__main__':
    main()