"""Small reusable widgets."""
from __future__ import annotations

import streamlit as st

from tracker.config import get_currency


def money(value: float) -> str:
    return f"{get_currency()}{value:,.2f}"


def page_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def empty_state(message: str, icon: str = "🗒️") -> None:
    st.info(f"{icon}  {message}")
