"""Habits page: add habits, tick off the last 7 days, watch streaks grow."""
from __future__ import annotations

from datetime import date

import streamlit as st

from tracker.services import habits
from tracker.ui.components import empty_state, page_header


def _on_toggle(habit_id: int, day: date, key: str) -> None:
    habits.set_log(habit_id, day, st.session_state[key])


def _on_delete(habit_id: int, name: str) -> None:
    habits.delete_habit(habit_id)
    st.toast(f"Deleted “{name}”", icon="🗑️")


def _add_habit_form() -> None:
    with st.container(border=True):
        st.subheader("Add habit")
        with st.form("add_habit_form", clear_on_submit=True, border=False):
            c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
            name = c1.text_input("Habit name", placeholder="e.g. Read 20 pages")
            if c2.form_submit_button("Add", type="primary"):
                try:
                    habits.add_habit(name)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.toast(f"Added “{name.strip()}”", icon="🌱")


def render() -> None:
    page_header("Habits", "Small, consistent actions — one day at a time.")
    _add_habit_form()

    summaries = habits.get_habit_summaries(date.today())
    with st.container(border=True):
        st.subheader("Your habits")
        if not summaries:
            empty_state("No habits yet — add one above to get started.", "🌱")
            return

        widths = [3, *([1] * 7), 1.4, 0.8]
        header = st.columns(widths, vertical_alignment="center")
        header[0].caption("HABIT")
        for col, (day, _) in zip(header[1:8], summaries[0].week):
            col.markdown(f'<div class="day-label">{day:%a}<br>{day:%d}</div>', unsafe_allow_html=True)
        header[8].caption("STREAK")

        for h in summaries:
            row = st.columns(widths, vertical_alignment="center")
            row[0].markdown(f"**{h.name}**")
            for col, (day, done) in zip(row[1:8], h.week):
                key = f"habits_{h.id}_{day.isoformat()}"
                col.checkbox(
                    f"{h.name} on {day:%d %b}",
                    value=done,
                    key=key,
                    label_visibility="collapsed",
                    on_change=_on_toggle,
                    args=(h.id, day, key),
                )
            row[8].markdown(f'<span class="streak">🔥 {h.streak}</span>', unsafe_allow_html=True)
            with row[9].popover("🗑️", help="Delete habit"):
                st.write(f"Delete **{h.name}** and its history?")
                st.button(
                    "Yes, delete",
                    key=f"del_{h.id}",
                    type="primary",
                    on_click=_on_delete,
                    args=(h.id, h.name),
                )


render()
