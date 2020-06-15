from flask import g
from mysql.connector import connect
import os

# database connection funcitons
def db_connect():
    db = connect(
        username=os.environ.get("DB_USERNAME"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_QABLOG")
    )
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