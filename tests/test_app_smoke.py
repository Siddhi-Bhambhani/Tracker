"""Boot the real app and visit every page; none of them may raise."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from tracker.demo import seed_demo_data

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["dashboard", "expenses", "habits", "insights"]


def _visit(page: str) -> AppTest:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    if page != "dashboard":
        at = at.switch_page(f"views/{page}.py").run()
    return at


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_with_empty_database(db, page):
    at = _visit(page)
    assert not at.exception, at.exception


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_with_demo_data(db, page):
    seed_demo_data()
    at = _visit(page)
    assert not at.exception, at.exception


def test_add_expense_and_toggle_habit_flow(db):
    from datetime import date

    from tracker.services import expenses, habits

    at = _visit("expenses")
    at.number_input[0].set_value(250.0)
    at.text_input[0].set_value("Pets")  # new category
    at.text_input[1].set_value("Cat food")
    at.button[0].click().run()  # the form's submit button
    assert not at.exception, at.exception
    df = expenses.list_expenses()
    assert len(df) == 1 and df.iloc[0]["category"] == "Pets" and df.iloc[0]["amount"] == 250.0

    habits.add_habit("Workout")
    at = _visit("dashboard")
    at.checkbox[0].check().run()
    assert not at.exception, at.exception
    assert habits.get_habit_summaries()[0].done_today
    assert habits.get_habit_summaries()[0].week[-1][0] == date.today()
