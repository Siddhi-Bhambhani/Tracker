"""Habit CRUD, streak logic and summaries."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta

import pandas as pd

from tracker.database import get_connection


# ---------- Pure streak helpers (no DB, easy to unit-test) ----------
def calc_streak(logged: set[date], today: date | None = None) -> int:
    """Consecutive logged days ending today.

    If today isn't logged *yet*, the streak is still alive as long as
    yesterday was — you only lose it once a whole day is missed.
    """
    today = today or date.today()
    day = today if today in logged else today - timedelta(days=1)
    streak = 0
    while day in logged:
        streak += 1
        day -= timedelta(days=1)
    return streak


def longest_streak(logged: set[date]) -> int:
    """Longest run of consecutive logged days ever."""
    best = run = 0
    prev: date | None = None
    for d in sorted(logged):
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        best = max(best, run)
        prev = d
    return best


# ---------- Data access ----------
@dataclass
class HabitSummary:
    id: int
    name: str
    streak: int
    best_streak: int
    done_today: bool
    week: list[tuple[date, bool]] = field(default_factory=list)
    completion_30d: float = 0.0  # 0..1


def add_habit(name: str) -> None:
    """Create a habit. Raises ValueError for empty or duplicate names."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Habit name can't be empty.")
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO habits (name) VALUES (?)", (name,))
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"You already have a habit called “{name}”.") from exc


def delete_habit(habit_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))


def set_log(habit_id: int, day: date, done: bool) -> None:
    """Mark a habit done/not done for a given day (idempotent)."""
    with get_connection() as conn:
        if done:
            conn.execute(
                "INSERT OR IGNORE INTO habit_logs (habit_id, date) VALUES (?, ?)",
                (habit_id, day.isoformat()),
            )
        else:
            conn.execute(
                "DELETE FROM habit_logs WHERE habit_id = ? AND date = ?",
                (habit_id, day.isoformat()),
            )


def _all_logs() -> dict[int, set[date]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT habit_id, date FROM habit_logs").fetchall()
    logs: dict[int, set[date]] = {}
    for r in rows:
        logs.setdefault(r["habit_id"], set()).add(date.fromisoformat(r["date"]))
    return logs


def get_habit_summaries(today: date | None = None, week_days: int = 7) -> list[HabitSummary]:
    """Everything the UI needs to render habits, in one pass over the DB."""
    today = today or date.today()
    with get_connection() as conn:
        habits = conn.execute("SELECT id, name FROM habits ORDER BY name COLLATE NOCASE").fetchall()
    logs = _all_logs()
    days = [today - timedelta(days=i) for i in range(week_days - 1, -1, -1)]
    last_30 = {today - timedelta(days=i) for i in range(30)}

    summaries = []
    for h in habits:
        logged = logs.get(h["id"], set())
        summaries.append(
            HabitSummary(
                id=h["id"],
                name=h["name"],
                streak=calc_streak(logged, today),
                best_streak=longest_streak(logged),
                done_today=today in logged,
                week=[(d, d in logged) for d in days],
                completion_30d=len(logged & last_30) / 30,
            )
        )
    return summaries


def completion_frame(days: int = 30, today: date | None = None) -> pd.DataFrame:
    """Long-format (habit, date, done) frame for the heatmap."""
    today = today or date.today()
    habits = get_habit_summaries(today)
    logs = _all_logs()
    rows = []
    for h in habits:
        logged = logs.get(h.id, set())
        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            rows.append({"habit": h.name, "date": pd.Timestamp(d), "done": d in logged})
    return pd.DataFrame(rows, columns=["habit", "date", "done"])
