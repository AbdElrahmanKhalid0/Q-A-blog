from flask import g
# from mysql.connector import connect
from psycopg2 import connect
from psycopg2.extras import DictCursor
import os

# database connection funcitons
def db_connect():
    # db = connect(
    #     username=os.environ.get("DB_USERNAME"),
    #     password=os.environ.get("DB_PASSWORD"),
    #     host=os.environ.get("DB_HOST"),
    #     database=os.environ.get("DB_QABLOG")
    # )
    # cursor = db.cursor(buffered=True, dictionary=True)
    db = connect(os.environ.get("DATABASE_URL"), cursor_factory=DictCursor)
    cursor = db.cursor()
    g.mysql_db = db
    g.mysql_cursor = cursor

def get_db():
    if not hasattr(g, 'mysql_db'):
        db_connect()
    return g.mysql_db

def get_db_cursor():
    if not hasattr(g, 'mysql_cursor'):
        db_connect()
    return g.mysql_cursor

def dictionarizeData(data, columnsData, oneRow=False):
    columns = tuple([column[0] for column in columnsData])
    if not oneRow:
        results = []
        for row in data:
            results.append(dict(zip(columns, row)))
        return results
    return dict(zip(columns, data))

def init_db():
    schema = open('schema.sql','r').read()
    db = connect(os.environ.get("DATABASE_URL"), cursor_factory=DictCursor)
    cursor = db.cursor()
    cursor.execute(schema)
    db.commit()
