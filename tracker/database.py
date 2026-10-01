"""SQLite connection handling and schema creation.

The schema is identical to the original Flask version, so an existing
``tracker.db`` can simply be copied into ``data/`` and keeps working.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from tracker.config import get_db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    note TEXT,
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits (id),
    UNIQUE(habit_id, date)
);

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses (date);
CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs (date);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a connection that commits on success and rolls back on error."""
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they don't exist yet (safe to call on every run)."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
