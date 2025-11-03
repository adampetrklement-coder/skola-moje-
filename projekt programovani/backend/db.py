import sqlite3
import os
from config import DATABASE_PATH

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        # Zapnout cizí klíče (pokud bychom je používali)
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn
    except sqlite3.Error as err:
        print(f"Chyba připojení k databázi: {err}")
        raise

def init_db():
    """Inicializuje databázi podle schema.sql"""
    try:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        with get_db_connection() as conn:
            conn.executescript(schema_sql)
        print("Databáze (SQLite) úspěšně inicializována")
    except sqlite3.Error as err:
        print(f"Chyba při inicializaci databáze: {err}")
        raise
    except Exception as e:
        print(f"Neočekávaná chyba: {e}")
        raise
