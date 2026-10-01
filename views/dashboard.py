"""Dashboard: spending totals, recent expenses and today's habits."""
from __future__ import annotations

from datetime import date

import streamlit as st

from tracker.config import get_currency
from tracker.dates import month_bounds, previous_month_to_date, week_bounds
from tracker.demo import seed_demo_data
from tracker.services import expenses, habits
from tracker.ui import charts
from tracker.ui.components import empty_state, money, page_header


def _on_habit_toggle(habit_id: int, day: date, key: str) -> None:
    habits.set_log(habit_id, day, st.session_state[key])


def _load_demo() -> None:
    seed_demo_data()
    st.toast("Demo data loaded", icon="✨")


def render() -> None:
    today = date.today()
    page_header("Dashboard", today.strftime("%A, %d %B %Y"))

    if not expenses.has_any_data():
        st.info("👋 Welcome! Start by adding an expense or a habit — or load some sample data to explore.")
        st.button("Load demo data", on_click=_load_demo, type="primary")

    summaries = habits.get_habit_summaries(today)

    week_total = expenses.total_between(*week_bounds(today))
    month_total = expenses.total_between(*month_bounds(today))
    last_month_same_period = expenses.total_between(*previous_month_to_date(today))
    done_today = sum(h.done_today for h in summaries)
    best_streak = max((h.streak for h in summaries), default=0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("This week", money(week_total))
    c2.metric(
        "This month",
        money(month_total),
        delta=f"{money(abs(month_total - last_month_same_period))} vs last month"
        if last_month_same_period
        else None,
        delta_color="inverse",
        delta_arrow="up" if month_total >= last_month_same_period else "down",
        help="Compared with the same days of last month.",
    )
    c3.metric("Habits today", f"{done_today}/{len(summaries)}" if summaries else "—")
    c4.metric("Best live streak", f"🔥 {best_streak}" if summaries else "—")

    left, right = st.columns([3, 2])

    with left, st.container(border=True):
        st.subheader("Recent expenses")
        recent = expenses.list_expenses(limit=5)
        if recent.empty:
            empty_state("No expenses logged yet.", "🧾")
        else:
            st.dataframe(
                recent[["date", "category", "amount"]],
                hide_index=True,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="DD MMM"),
                    "category": "Category",
                    "amount": st.column_config.NumberColumn("Amount", format=f"{get_currency()}%.2f"),
                },
            )
        st.page_link("views/expenses.py", label="View all expenses →")

    with right, st.container(border=True):
        st.subheader("Today's habits")
        if not summaries:
            empty_state("No habits yet.", "🌱")
        for h in summaries:
            key = f"dash_{h.id}_{today.isoformat()}"
            name_col, streak_col = st.columns([4, 1.4], vertical_alignment="center")
            name_col.checkbox(
                h.name,
                value=h.done_today,
                key=key,
                on_change=_on_habit_toggle,
                args=(h.id, today, key),
            )
            streak_col.markdown(f'<span class="streak">🔥 {h.streak}</span>', unsafe_allow_html=True)
        st.page_link("views/habits.py", label="Manage habits →")

    with st.container(border=True):
        st.subheader("Spending — last 30 days")
        daily = expenses.daily_totals(30, today)
        if daily["total"].sum() == 0:
            empty_state("Nothing to chart yet.", "📊")
        else:
            st.altair_chart(charts.daily_spending_chart(daily))


render()
