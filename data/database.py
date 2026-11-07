
import os
import sqlite3
from pathlib import Path


APP_DATA = Path(
    os.environ.get(
        "LOCALAPPDATA",
        str(Path.home())
    )
) / "NetworkExplorer"

APP_DATA.mkdir(parents=True, exist_ok=True)

DB_PATH = APP_DATA / "devices.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS device_names (
                mac TEXT PRIMARY KEY,
                custom_name TEXT NOT NULL
            )
        """)


def get_custom_name(mac: str) -> str | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT custom_name
            FROM device_names
            WHERE mac = ?
            """,
            (mac.lower(),),
        ).fetchone()

    return row[0] if row else None


def save_custom_name(mac: str, name: str):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO device_names (mac, custom_name)
            VALUES (?, ?)
            ON CONFLICT(mac)
            DO UPDATE SET custom_name = excluded.custom_name
            """,
            (mac.lower(), name),
        )
