import sqlite3
import pandas as pd
from src.config import DB_PATH

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def store_dataframe(df, table_name, if_exists='replace'):
    """Store a pandas DataFrame in the specified table."""
    with get_connection() as conn:
        df.to_sql(table_name, conn, index=False, if_exists=if_exists)

def fetch_query(query):
    """Fetch data from the database as a pandas DataFrame."""
    with get_connection() as conn:
        return pd.read_sql(query, conn)
