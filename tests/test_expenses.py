from datetime import date

import pytest

from tracker.services import expenses


def test_add_and_list(db):
    expenses.add_expense(120.5, "Food", "Lunch", date(2026, 10, 1))
    expenses.add_expense(40, "", "", date(2026, 10, 2))
    df = expenses.list_expenses()
    assert list(df["category"]) == ["Uncategorized", "Food"]  # newest first
    assert df["amount"].sum() == pytest.approx(160.5)


def test_rejects_non_positive_amount(db):
    with pytest.raises(ValueError):
        expenses.add_expense(0, "Food", "", date.today())
    with pytest.raises(ValueError):
        expenses.add_expense(-5, "Food", "", date.today())


def test_filters_and_totals(db):
    expenses.add_expense(100, "Food", "", date(2026, 9, 30))
    expenses.add_expense(200, "Bills", "", date(2026, 10, 1))
    expenses.add_expense(50, "Food", "", date(2026, 10, 2))

    assert len(expenses.list_expenses(category="Food")) == 2
    assert len(expenses.list_expenses(start=date(2026, 10, 1))) == 2
    assert expenses.total_between(date(2026, 10, 1), date(2026, 10, 31)) == 250
    assert expenses.used_categories() == ["Bills", "Food"]


def test_delete(db):
    a = expenses.add_expense(10, "Food", "", date.today())
    b = expenses.add_expense(20, "Food", "", date.today())
    assert expenses.delete_expenses([a]) == 1
    assert list(expenses.list_expenses()["id"]) == [b]
    assert expenses.delete_expenses([]) == 0


def test_daily_totals_zero_fills(db):
    today = date(2026, 10, 10)
    expenses.add_expense(30, "Food", "", date(2026, 10, 9))
    out = expenses.daily_totals(3, today)
    assert list(out["total"]) == [0.0, 30.0, 0.0]


def test_monthly_totals_and_category_breakdown(db):
    today = date(2026, 10, 15)
    expenses.add_expense(100, "Food", "", date(2026, 9, 5))
    expenses.add_expense(60, "Food", "", date(2026, 10, 5))
    expenses.add_expense(40, "Bills", "", date(2026, 10, 6))
    monthly = expenses.monthly_totals(3, today)
    assert list(monthly["month"]) == ["Aug 2026", "Sep 2026", "Oct 2026"]
    assert list(monthly["total"]) == [0.0, 100.0, 100.0]
    cats = expenses.spending_by_category(date(2026, 10, 1), date(2026, 10, 31))
    assert list(cats["category"]) == ["Food", "Bills"]
