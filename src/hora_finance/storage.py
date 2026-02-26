from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              google_sub TEXT UNIQUE NOT NULL,
              email TEXT NOT NULL,
              name TEXT,
              picture TEXT,
              credentials_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS active_session (
              id INTEGER PRIMARY KEY CHECK (id = 1),
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def upsert_user(db_path: Path, user_info: dict[str, str], credentials_json: str) -> int:
    now = _utc_now()
    google_sub = user_info["sub"]
    email = user_info["email"]
    name = user_info.get("name")
    picture = user_info.get("picture")

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO users (google_sub, email, name, picture, credentials_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(google_sub) DO UPDATE SET
              email = excluded.email,
              name = excluded.name,
              picture = excluded.picture,
              credentials_json = excluded.credentials_json,
              updated_at = excluded.updated_at
            """,
            (google_sub, email, name, picture, credentials_json, now, now),
        )
        row = conn.execute("SELECT id FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
        conn.commit()

    if row is None:
        raise RuntimeError("Failed to fetch user id after upsert.")
    return int(row[0])


def set_active_session(db_path: Path, user_id: int) -> None:
    now = _utc_now()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO active_session (id, user_id, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              user_id = excluded.user_id,
              updated_at = excluded.updated_at
            """,
            (user_id, now),
        )
        conn.commit()


def clear_active_session(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM active_session WHERE id = 1")
        conn.commit()


def get_active_user(db_path: Path) -> dict[str, str] | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT
              u.google_sub AS sub,
              u.email AS email,
              u.name AS name,
              u.picture AS picture
            FROM users u
            JOIN active_session s ON s.user_id = u.id
            WHERE s.id = 1
            """
        ).fetchone()

    if row is None:
        return None
    return {k: (row[k] or "") for k in row.keys()}
