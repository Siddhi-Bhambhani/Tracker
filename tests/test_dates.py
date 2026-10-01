from datetime import date

from tracker.dates import month_bounds, previous_month_to_date, resolve_period, week_bounds


def test_week_bounds_monday_to_sunday():
    start, end = week_bounds(date(2026, 10, 1))  # Thursday
    assert (start, end) == (date(2026, 9, 28), date(2026, 10, 4))


def test_month_bounds_handles_leap_february():
    assert month_bounds(date(2024, 2, 10)) == (date(2024, 2, 1), date(2024, 2, 29))


def test_previous_month_to_date_clamps_day():
    # 31st of March -> February only has 28 days in 2026
    assert previous_month_to_date(date(2026, 3, 31)) == (date(2026, 2, 1), date(2026, 2, 28))
    assert previous_month_to_date(date(2026, 1, 15)) == (date(2025, 12, 1), date(2025, 12, 15))


def test_resolve_period():
    today = date(2026, 10, 1)
    assert resolve_period("All time", today) == (None, None)
    assert resolve_period("Last 30 days", today) == (date(2026, 9, 2), today)
    assert resolve_period("Custom range", today, (date(2026, 1, 1), date(2026, 1, 5))) == (
        date(2026, 1, 1),
        date(2026, 1, 5),
    )
