from __future__ import annotations

import sqlite3
from pathlib import Path

import bcrypt

from db.models import SCHEMA
from utils.constants import (
    ADMIN_COUNTRY,
    ADMIN_EMAIL,
    ADMIN_EXPERIENCE,
    ADMIN_MOBILE,
    ADMIN_NAME,
    ADMIN_PASSWORD,
    ADMIN_ROLE,
)
from utils.helpers import utc_iso


DB_PATH = Path(__file__).resolve().parent / "tredalq.sqlite3"


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        _migrate_users_table(connection)
        connection.commit()
    bootstrap_admin_user()


def _migrate_users_table(connection: sqlite3.Connection) -> None:
    columns = _table_columns(connection, "users")
    if "full_name" not in columns:
        connection.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    if "name" in columns:
        connection.execute("UPDATE users SET full_name = COALESCE(full_name, name)")
    else:
        connection.execute("UPDATE users SET full_name = COALESCE(full_name, email)")


def bootstrap_admin_user() -> None:
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (ADMIN_EMAIL.lower(),),
        ).fetchone()
        hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        if existing:
            connection.execute(
                """
                UPDATE users
                SET full_name = ?, password_hash = ?, role = ?, mobile = ?, country = ?,
                    experience = ?
                WHERE email = ?
                """,
                (
                    ADMIN_NAME,
                    hashed,
                    ADMIN_ROLE,
                    ADMIN_MOBILE,
                    ADMIN_COUNTRY,
                    ADMIN_EXPERIENCE,
                    ADMIN_EMAIL.lower(),
                ),
            )
        else:
            connection.execute(
                """
                INSERT INTO users (
                    full_name, email, password_hash, mobile, country,
                    experience, role
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ADMIN_NAME,
                    ADMIN_EMAIL.lower(),
                    hashed,
                    ADMIN_MOBILE,
                    ADMIN_COUNTRY,
                    ADMIN_EXPERIENCE,
                    ADMIN_ROLE,
                ),
            )
        connection.commit()


def database_exists() -> bool:
    return DB_PATH.exists()
