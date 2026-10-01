"""Insights page: trends for spending and habit consistency."""
from __future__ import annotations

from datetime import date

import streamlit as st

from tracker.dates import month_bounds
from tracker.services import expenses, habits
from tracker.ui import charts
from tracker.ui.components import empty_state, money, page_header


def render() -> None:
    today = date.today()
    page_header("Insights", "Trends in your spending and consistency.")

    spend_tab, habit_tab = st.tabs(["💸 Spending", "🔥 Habits"])

    with spend_tab:
        left, right = st.columns(2)

        with left, st.container(border=True):
            st.subheader("By category")
            scope = st.radio("Scope", ["This month", "All time"], horizontal=True, label_visibility="collapsed")
            start, end = month_bounds(today) if scope == "This month" else (None, None)
            by_cat = expenses.spending_by_category(start, end)
            if by_cat.empty:
                empty_state("No spending in this range.", "📊")
            else:
                st.altair_chart(charts.category_donut(by_cat))
                top = by_cat.iloc[0]
                st.caption(f"Top category: **{top['category']}** ({money(top['total'])})")

        with right, st.container(border=True):
            st.subheader("Last 6 months")
            monthly = expenses.monthly_totals(6, today)
            if monthly["total"].sum() == 0:
                empty_state("Nothing to chart yet.", "📊")
            else:
                st.altair_chart(charts.monthly_bar_chart(monthly))

    with habit_tab:
        summaries = habits.get_habit_summaries(today)
        if not summaries:
            empty_state("Add a habit to see consistency insights.", "🌱")
            return

        with st.container(border=True):
            st.subheader("Last 30 days")
            st.altair_chart(charts.habit_heatmap(habits.completion_frame(30, today)))

        with st.container(border=True):
            st.subheader("Consistency")
            for h in sorted(summaries, key=lambda s: s.completion_30d, reverse=True):
                c1, c2, c3 = st.columns([3, 4, 3], vertical_alignment="center")
                c1.markdown(f"**{h.name}**")
                c2.progress(h.completion_30d, text=f"{h.completion_30d:.0%} of last 30 days")
                c3.caption(f"🔥 current {h.streak} · 🏆 best {h.best_streak}")


render()
