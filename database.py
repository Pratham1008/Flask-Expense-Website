import sqlite3
from flask import g


def connect_database():
    conn = sqlite3.connect('expensedata.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


def get_database():
    if not hasattr(g, 'expense_db'):
        g.expense_db = connect_database()
    return g.expense_db
