import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.database import init_db  # noqa: E402


@pytest.fixture()
def db(tmp_path, monkeypatch):
    """Fresh, isolated SQLite database for every test."""
    monkeypatch.setenv("TRACKER_DB_PATH", str(tmp_path / "test.db"))
    init_db()
    return tmp_path / "test.db"
