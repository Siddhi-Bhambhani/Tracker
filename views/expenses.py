"""Expenses page: add, filter, review, delete and export."""
from __future__ import annotations

from datetime import date

import streamlit as st

from tracker.config import get_currency
from tracker.dates import PERIOD_OPTIONS, resolve_period
from tracker.services import expenses
from tracker.ui.components import empty_state, money, page_header


def _add_expense_form() -> None:
    with st.container(border=True):
        st.subheader("Add expense")
        with st.form("add_expense_form", clear_on_submit=True, border=False):
            c1, c2, c3 = st.columns(3)
            amount = c1.number_input(f"Amount ({get_currency()})", min_value=0.0, step=10.0, format="%.2f")
            category = c2.selectbox("Category", expenses.get_categories())
            expense_date = c3.date_input("Date", value=date.today())

            c4, c5 = st.columns([1, 2])
            new_category = c4.text_input("…or a new category", placeholder="e.g. Pets")
            note = c5.text_input("Note (optional)", placeholder="What was it for?")

            if st.form_submit_button("Add expense", type="primary"):
                try:
                    expenses.add_expense(amount, new_category.strip() or category, note, expense_date)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.toast(f"Added {money(amount)}", icon="✅")


def _filters() -> tuple[str | None, date | None, date | None]:
    f1, f2 = st.columns(2)
    category = f1.selectbox("Category", ["All categories", *expenses.used_categories()])
    period = f2.selectbox("Period", PERIOD_OPTIONS)

    custom = None
    if period == "Custom range":
        picked = st.date_input("Date range", value=(date.today().replace(day=1), date.today()))
        if isinstance(picked, tuple) and len(picked) == 2:
            custom = picked
        else:
            st.caption("Pick both a start and an end date.")

    start, end = resolve_period(period, date.today(), custom)
    return (None if category == "All categories" else category), start, end


def render() -> None:
    page_header("Expenses", "Log what you spend and see where it goes.")
    _add_expense_form()

    with st.container(border=True):
        st.subheader("History")
        category, start, end = _filters()
        df = expenses.list_expenses(category=category, start=start, end=end)

        if df.empty:
            empty_state("No expenses match these filters.", "🧾")
            return

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", money(df["amount"].sum()))
        m2.metric("Entries", len(df))
        m3.metric("Average", money(df["amount"].mean()))
        m4.metric("Largest", money(df["amount"].max()))

        st.caption("Tick rows on the left to select them for deletion.")
        # No `key` on purpose: the selection resets whenever the data changes,
        # so stale row indices can never delete the wrong expense.
        event = st.dataframe(
            df[["date", "category", "note", "amount"]],
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            column_config={
                "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
                "category": "Category",
                "note": "Note",
                "amount": st.column_config.NumberColumn("Amount", format=f"{get_currency()}%.2f"),
            },
        )

        selected = event.selection.rows
        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button(f"Delete selected ({len(selected)})", disabled=not selected):
            removed = expenses.delete_expenses(df.iloc[selected]["id"].tolist())
            st.toast(f"Deleted {removed} expense(s)", icon="🗑️")
            st.rerun()

        b2.download_button(
            "Export CSV",
            data=df.drop(columns="id").to_csv(index=False),
            file_name=f"expenses_{date.today().isoformat()}.csv",
            mime="text/csv",
        )


render()
