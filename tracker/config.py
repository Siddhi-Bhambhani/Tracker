"""Central place for app-wide settings.

Everything can be overridden with environment variables, which keeps the code
free of hard-coded paths and makes testing easy.

    TRACKER_DB_PATH   -> where the SQLite file lives (default: data/tracker.db)
    TRACKER_CURRENCY  -> currency symbol shown in the UI (default: ₹)
"""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Expense & Habit Tracker"
APP_ICON = "💰"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "tracker.db"

DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Groceries",
    "Bills",
    "Shopping",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]

PRIMARY_COLOR = "#6c5ce7"
ACCENT_COLOR = "#e17055"
SUCCESS_COLOR = "#00b894"


def get_db_path() -> Path:
    """Resolve the DB path at call time so tests can point it elsewhere."""
    return Path(os.getenv("TRACKER_DB_PATH", str(DEFAULT_DB_PATH)))


def get_currency() -> str:
    return os.getenv("TRACKER_CURRENCY", "₹")
