"""Entry point.  Run with:  streamlit run app.py"""
import streamlit as st

from tracker.config import APP_ICON, APP_NAME
from tracker.database import init_db
from tracker.ui.styles import inject_styles

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")

init_db()
inject_styles()

pages = [
    st.Page("views/dashboard.py", title="Dashboard", icon="🏠", url_path="dashboard", default=True),
    st.Page("views/expenses.py", title="Expenses", icon="💸", url_path="expenses"),
    st.Page("views/habits.py", title="Habits", icon="✅", url_path="habits"),
    st.Page("views/insights.py", title="Insights", icon="📈", url_path="insights"),
]

with st.sidebar:
    st.markdown(f"## {APP_ICON} Tracker")
    st.caption("Expenses & habits, in one place.")

st.navigation(pages).run()
