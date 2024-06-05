import sqlite3

def init_db_connection():
    cn = sqlite3.connect('hospital.db')
    cn.row_factory = sqlite3.Row
    return cn