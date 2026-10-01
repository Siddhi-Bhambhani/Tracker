"""Light custom CSS layered on top of Streamlit's theme."""
import streamlit as st

_CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 1100px; }
[data-testid="stMetricValue"] { color: #6c5ce7; font-weight: 700; }
[data-testid="stMetricLabel"] p { text-transform: uppercase; letter-spacing: .05em; font-size: .75rem; opacity: .7; }
.page-subtitle { margin-top: -.6rem; margin-bottom: 1.2rem; opacity: .65; }
.streak { color: #e17055; font-weight: 600; white-space: nowrap; }
.day-label { text-align: center; font-size: .75rem; opacity: .6; line-height: 1.2; }
</style>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
