"""Expense CRUD and aggregate queries."""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from tracker.config import DEFAULT_CATEGORIES
from tracker.database import get_connection

COLUMNS = ["id", "date", "category", "note", "amount"]


def add_expense(amount: float, category: str, note: str, expense_date: date) -> int:
    """Insert an expense and return its id. Raises ValueError on bad input."""
    if amount is None or amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    category = (category or "").strip() or "Uncategorized"
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
            (float(amount), category, (note or "").strip(), expense_date.isoformat()),
        )
        return int(cur.lastrowid)


def delete_expenses(expense_ids: list[int]) -> int:
    """Delete the given expenses and return how many rows were removed."""
    if not expense_ids:
        return 0
    placeholders = ",".join("?" * len(expense_ids))
    with get_connection() as conn:
        cur = conn.execute(f"DELETE FROM expenses WHERE id IN ({placeholders})", list(expense_ids))
        return cur.rowcount


def list_expenses(
    category: str | None = None,
    start: date | None = None,
    end: date | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    """Return expenses (newest first) as a DataFrame with a real ``date`` column."""
    query = "SELECT id, date, category, note, amount FROM expenses WHERE 1=1"
    params: list = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if start:
        query += " AND date >= ?"
        params.append(start.isoformat())
    if end:
        query += " AND date <= ?"
        params.append(end.isoformat())
    query += " ORDER BY date DESC, id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["note"] = df["note"].fillna("")
    return df


def get_categories() -> list[str]:
    """Defaults plus anything the user has used before, sorted."""
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM expenses").fetchall()
    used = {r["category"] for r in rows}
    return sorted(set(DEFAULT_CATEGORIES) | used)


def used_categories() -> list[str]:
    """Only categories that actually appear in the data (for filters)."""
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM expenses ORDER BY category").fetchall()
    return [r["category"] for r in rows]


def total_between(start: date, end: date) -> float:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE date BETWEEN ? AND ?",
            (start.isoformat(), end.isoformat()),
        ).fetchone()
    return round(float(row["total"]), 2)


def spending_by_category(start: date | None = None, end: date | None = None) -> pd.DataFrame:
    df = list_expenses(start=start, end=end)
    if df.empty:
        return pd.DataFrame(columns=["category", "total"])
    out = df.groupby("category", as_index=False)["amount"].sum().rename(columns={"amount": "total"})
    return out.sort_values("total", ascending=False).reset_index(drop=True)


def daily_totals(days: int, today: date | None = None) -> pd.DataFrame:
    """Spend per day for the last ``days`` days, with zero-filled gaps."""
    today = today or date.today()
    start = today - timedelta(days=days - 1)
    df = list_expenses(start=start, end=today)
    index = pd.date_range(start, today, freq="D")
    if df.empty:
        series = pd.Series(0.0, index=index)
    else:
        df["date"] = pd.to_datetime(df["date"])
        series = df.groupby("date")["amount"].sum().reindex(index, fill_value=0.0)
    return pd.DataFrame({"date": index, "total": series.values})


def monthly_totals(months: int = 6, today: date | None = None) -> pd.DataFrame:
    """Total spend per calendar month for the last ``months`` months."""
    today = today or date.today()
    periods = pd.period_range(end=pd.Period(today, freq="M"), periods=months, freq="M")
    start = periods[0].start_time.date()
    df = list_expenses(start=start, end=today)
    if df.empty:
        totals = pd.Series(0.0, index=periods)
    else:
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
        totals = df.groupby("month")["amount"].sum().reindex(periods, fill_value=0.0)
    return pd.DataFrame({"month": [p.strftime("%b %Y") for p in periods], "total": totals.values})


def has_any_data() -> bool:
    with get_connection() as conn:
        e = conn.execute("SELECT COUNT(*) AS n FROM expenses").fetchone()["n"]
        h = conn.execute("SELECT COUNT(*) AS n FROM habits").fetchone()["n"]
    return (e + h) > 0
