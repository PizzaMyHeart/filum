import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError

db_name = 'filum'

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
            parent_id TEXT, title TEXT, timestamp INTEGER, permalink TEXT, num_comments INTEGER, author TEXT, source TEXT)'''
    # TODO: Add timestamp at time of saving the thread
    try:
        conn.execute(sql)
    except OperationalError as err:
        print(err)



@connect
def create_table_descendants(conn):
    sql = '''CREATE TABLE IF NOT EXISTS descendants 
            (row_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            ancestor_id INTEGER REFERENCES ancestors(parent_id), 
            parent_id TEXT, descendant_id TEXT, text TEXT, permalink TEXT, 
            author TEXT, author_id TEXT, is_submitter INTEGER,
            upvotes INTEGER, downvotes INTEGER, score INTEGER, timestamp INTEGER,
            depth INTEGER, path TEXT)'''
    try:
        conn.execute(sql)
    except OperationalError as err:
        print(err)

@connect
def insert_row(conn, values, table_name):
    if table_name == 'ancestors':
        to_insert = '''
                    ("parent_id", "title", "timestamp", "permalink", "num_comments", "author", "source") 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    '''

    elif table_name == 'descendants':
        to_insert = '''
                    ("ancestor_id", "author", "author_id", "depth", "downvotes", 
                    "is_submitter", "parent_id", "path", "permalink", "score",
                    "text", "timestamp", "upvotes")
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''

    sql = f'''INSERT INTO {table_name}''' + to_insert
    # TODO: Skip insert if already exists
    try:
        conn.executemany(sql, values)
        conn.commit()
    except IntegrityError as err:
        print(err)



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
    
    def insert_row(self, values, table_name):
        return insert_row(self._connection, values, table_name)

if __name__ == '__main__':
    main()