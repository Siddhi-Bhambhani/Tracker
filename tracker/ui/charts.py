"""Altair charts (Altair ships with Streamlit, so no extra dependency)."""
from __future__ import annotations

import altair as alt
import pandas as pd

from tracker.config import ACCENT_COLOR, PRIMARY_COLOR, SUCCESS_COLOR, get_currency


def daily_spending_chart(df: pd.DataFrame) -> alt.Chart:
    cur = get_currency()
    return (
        alt.Chart(df)
        .mark_bar(color=PRIMARY_COLOR, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%d %b", labelAngle=0, tickCount=6)),
            y=alt.Y("total:Q", title=None),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%d %b %Y"),
                alt.Tooltip("total:Q", title=f"Spent ({cur})", format=",.2f"),
            ],
        )
        .properties(height=240)
    )


def category_donut(df: pd.DataFrame) -> alt.Chart:
    cur = get_currency()
    return (
        alt.Chart(df)
        .mark_arc(innerRadius=70)
        .encode(
            theta=alt.Theta("total:Q"),
            color=alt.Color("category:N", title=None, legend=alt.Legend(orient="right")),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("total:Q", title=f"Spent ({cur})", format=",.2f"),
            ],
        )
        .properties(height=280)
    )


def monthly_bar_chart(df: pd.DataFrame) -> alt.Chart:
    cur = get_currency()
    return (
        alt.Chart(df)
        .mark_bar(color=ACCENT_COLOR, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("month:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("total:Q", title=None),
            tooltip=[
                alt.Tooltip("month:N", title="Month"),
                alt.Tooltip("total:Q", title=f"Spent ({cur})", format=",.2f"),
            ],
        )
        .properties(height=280)
    )


def habit_heatmap(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_rect(cornerRadius=2, stroke="white", strokeWidth=1)
        .encode(
            x=alt.X("date:T", title=None, timeUnit="yearmonthdate", axis=alt.Axis(format="%d %b", labelAngle=0, tickCount=6)),
            y=alt.Y("habit:N", title=None),
            color=alt.Color(
                "done:N",
                scale=alt.Scale(domain=[True, False], range=[SUCCESS_COLOR, "#e6e6ee"]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("habit:N", title="Habit"),
                alt.Tooltip("date:T", title="Date", format="%d %b %Y"),
                alt.Tooltip("done:N", title="Done"),
            ],
        )
        .properties(height=max(60, 36 * df["habit"].nunique()))
    )
