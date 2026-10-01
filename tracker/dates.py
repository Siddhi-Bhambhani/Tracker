"""Small date helpers shared by services and views (pure functions, easy to test)."""
from __future__ import annotations

import calendar
from datetime import date, timedelta


def week_bounds(today: date) -> tuple[date, date]:
    """Monday..Sunday of the week containing ``today``."""
    start = today - timedelta(days=today.weekday())
    return start, start + timedelta(days=6)


def month_bounds(today: date) -> tuple[date, date]:
    """First..last day of the month containing ``today``."""
    last_day = calendar.monthrange(today.year, today.month)[1]
    return today.replace(day=1), today.replace(day=last_day)


def previous_month_to_date(today: date) -> tuple[date, date]:
    """Same slice of the previous month, e.g. 1st..15th when today is the 15th.

    Used for a fair "this month vs last month" comparison.
    """
    first_this_month = today.replace(day=1)
    last_prev = first_this_month - timedelta(days=1)
    first_prev = last_prev.replace(day=1)
    return first_prev, first_prev.replace(day=min(today.day, last_prev.day))


PERIOD_OPTIONS = ["All time", "This week", "This month", "Last 30 days", "This year", "Custom range"]


def resolve_period(label: str, today: date, custom: tuple[date, date] | None = None) -> tuple[date | None, date | None]:
    """Turn a period label from the UI into (start, end). ``None`` means unbounded."""
    if label == "This week":
        return week_bounds(today)
    if label == "This month":
        return month_bounds(today)
    if label == "Last 30 days":
        return today - timedelta(days=29), today
    if label == "This year":
        return today.replace(month=1, day=1), today.replace(month=12, day=31)
    if label == "Custom range" and custom:
        return custom
    return None, None
