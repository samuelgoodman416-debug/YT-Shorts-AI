"""SQLite log of generated videos, used to avoid repeating the same story."""

import hashlib
import sqlite3
from pathlib import Path

DB_PATH = Path("state.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            story_hash TEXT NOT NULL UNIQUE,
            output_path TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def _story_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def already_used(story_text: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM videos WHERE story_hash = ?", (_story_hash(story_text),)
        ).fetchone()
        return row is not None


def record_video(title: str, story_text: str, output_path: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO videos (title, story_hash, output_path) VALUES (?, ?, ?)",
            (title, _story_hash(story_text), output_path),
        )


def recent_titles(limit: int = 20) -> list[str]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT title FROM videos ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [row[0] for row in rows]
