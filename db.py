import sqlite3
import os
from logger import get_logger

logger = get_logger(__name__)
DB_PATH = "./data/vinted_notifications.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_or_update_sqlite_db(sql_file):
    with open(sql_file, "r") as f:
        sql = f.read()
    conn = get_db_connection()
    try:
        conn.executescript(sql)
    except Exception as e:
        # Handle duplicate column errors gracefully (SQLite doesn't support IF NOT EXISTS for ALTER TABLE)
        if "duplicate column name" in str(e):
            logger.warning(f"Skipping migration {sql_file}: {e} (column already exists)")
            # Still need to update the version — extract and run only UPDATE statements
            for line in sql.splitlines():
                line = line.strip()
                if line.upper().startswith("UPDATE") or line.upper().startswith("INSERT"):
                    try:
                        conn.execute(line.rstrip(";"), [])
                    except Exception:
                        pass
        else:
            conn.close()
            raise
    conn.commit()
    conn.close()


def get_parameter(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM configuration WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result["value"] if result else None


def set_parameter(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_queries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queries ORDER BY id")
    result = cursor.fetchall()
    conn.close()
    return result


def add_query_to_db(query, name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO queries (query, name) VALUES (?, ?)",
        (query, name),
    )
    conn.commit()
    conn.close()


def is_query_in_db(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queries WHERE query = ?", (query,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def remove_query_from_db(number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM queries WHERE id = ?", (number,))
    conn.commit()
    conn.close()


def remove_all_queries_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM queries")
    conn.commit()
    conn.close()


def update_query_in_db(query_id, query, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE queries SET query = ?, name = ? WHERE id = ?",
        (query, name, query_id),
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def get_allowlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country_code FROM allowlist")
    result = cursor.fetchall()
    conn.close()
    if not result:
        return 0
    return [row["country_code"] for row in result]


def add_to_allowlist(country):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO allowlist (country_code) VALUES (?)", (country,))
    conn.commit()
    conn.close()


def remove_from_allowlist(country):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM allowlist WHERE country_code = ?", (country,))
    conn.commit()
    conn.close()


def get_last_timestamp(query_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp FROM query_timestamps WHERE query_id = ?", (query_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result["timestamp"] if result else None


def update_last_timestamp(query_id, timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO query_timestamps (query_id, timestamp) VALUES (?, ?)",
        (query_id, timestamp),
    )
    conn.commit()
    conn.close()


def is_item_in_db_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_item_to_db(id, timestamp, price, title, photo_url, query_id, currency):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR IGNORE INTO items (id, timestamp, price, title, photo_url, query_id, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id, timestamp, price, title, photo_url, query_id, currency),
    )
    # Also update the query timestamp
    cursor.execute(
        "INSERT OR REPLACE INTO query_timestamps (query_id, timestamp) VALUES (?, ?)",
        (query_id, timestamp),
    )
    conn.commit()
    conn.close()


def get_items(query_id=None, limit=100):
    conn = get_db_connection()
    cursor = conn.cursor()
    if query_id:
        cursor.execute(
            "SELECT * FROM items WHERE query_id = ? ORDER BY timestamp DESC LIMIT ?",
            (query_id, limit),
        )
    else:
        cursor.execute("SELECT * FROM items ORDER BY timestamp DESC LIMIT ?", (limit,))
    result = cursor.fetchall()
    conn.close()
    return result
