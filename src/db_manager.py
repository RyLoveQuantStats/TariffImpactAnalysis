import sqlite3
from src.config import DB_PATH
from src.schema import create_tables

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def initialize_database():
    """Initialize the database and create required tables."""
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized and tables created.")


