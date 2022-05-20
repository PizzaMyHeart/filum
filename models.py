import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError

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
            parent_id TEXT, title TEXT, timestamp INTEGER, 
            permalink TEXT UNIQUE, num_comments INTEGER, author TEXT, source TEXT,
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
            ancestor_id INTEGER REFERENCES ancestors(parent_id), 
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
def insert_row(conn, values, table_name):
    if table_name == 'ancestors':
        to_insert = '''
                    ("parent_id", "title", "timestamp", "permalink", "num_comments", "author", "source") 
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    '''

    elif table_name == 'descendants':
        to_insert = '''
                    ("ancestor_id", "id", "author", "author_id", "depth", "downvotes", 
                    "is_submitter", "parent_id", "path", "permalink", "score",
                    "text", "timestamp", "upvotes")
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    '''

    sql = f'''INSERT INTO {table_name}''' + to_insert
    # TODO: Skip insert if already exists
    try:
        conn.executemany(sql, values)
        conn.commit()
    except IntegrityError as err:
        print(err)
        if 'UNIQUE' in str(err):
            print('This item already exists in your database.')

@connect
def select_all_ancestors(conn):
    sql = 'SELECT * FROM ancestors;'
    results = conn.execute(sql).fetchall()
    return results

@connect
def select_all_descendants(conn, ancestor):
    sql_r = f'''
        WITH RECURSIVE comment_tree (depth, id, parent_id, text, author) AS (
            SELECT 0, id, parent_id, text, author
            FROM descendants
            WHERE ancestor_id = (?) AND parent_id = (?)
            UNION ALL
            SELECT c.depth + 1, c.id, d.parent_id, c.text, c.author
                FROM comment_tree c
                    JOIN descendants d ON c.id = d.parent_id
        )
        SELECT * FROM comment_tree ORDER BY parent_id, depth, id;
        
    '''
    sql = f'''
        SELECT depth, id, parent_id, text, author
        FROM descendants
        WHERE ancestor_id = (?);
    '''
    results = conn.execute(sql, (ancestor, )).fetchall()
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
    
    def insert_row(self, values, table_name):
        return insert_row(self._connection, values, table_name)

    def select_all_ancestors(self):
        return select_all_ancestors(self._connection)

    def select_all_descendants(self, ancestor):
        return select_all_descendants(self._connection, ancestor)

if __name__ == '__main__':
    main()