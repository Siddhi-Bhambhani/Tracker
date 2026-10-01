# 💰 Expense & Habit Tracker

A personal finance + habit-building dashboard built with **Streamlit**.
Log what you spend, tick off daily habits, and see trends at a glance.

## Features

| Page | What it does |
|------|--------------|
| 🏠 **Dashboard** | Weekly / monthly spend (with comparison vs last month), today's habits you can tick off, recent expenses, 30-day spending chart |
| 💸 **Expenses** | Add expenses, filter by category and period, select & delete rows, export to CSV |
| ✅ **Habits** | Add habits, tick off the last 7 days, 🔥 streaks, delete with confirmation |
| 📈 **Insights** | Category donut, 6-month trend, 30-day habit heatmap, per-habit consistency and best streaks |

Data is stored locally in SQLite — no accounts, no external services.

## Quick start

**1. Create a virtual environment and install dependencies**

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
```

**2. Run the app**

```bash
streamlit run app.py
```

It opens at http://localhost:8501. The database (`data/tracker.db`) is created automatically.

**3. (Optional) Load sample data** — click **Load demo data** on the dashboard, or:

```bash
python scripts/seed_demo_data.py
```

## Project structure

```
expense_habit_tracker/
├── app.py                  # Entry point: page config + navigation
├── views/                  # One script per page (UI only)
│   ├── dashboard.py
│   ├── expenses.py
│   ├── habits.py
│   └── insights.py
├── tracker/                # Application package
│   ├── config.py           # Settings (DB path, currency, colours)
│   ├── database.py         # SQLite connection + schema
│   ├── dates.py            # Week/month/period helpers
│   ├── demo.py             # Sample-data generator
│   ├── services/
│   │   ├── expenses.py     # Expense CRUD + aggregates
│   │   └── habits.py       # Habit CRUD + streak logic
│   └── ui/
│       ├── components.py   # Reusable widgets
│       ├── charts.py       # Altair charts
│       └── styles.py       # Custom CSS
├── tests/                  # pytest suite (services, dates, app smoke tests)
├── scripts/seed_demo_data.py
├── .streamlit/config.toml  # Theme
├── data/                   # SQLite DB lives here (git-ignored)
└── requirements.txt
```

**Design rule:** views never touch SQL — they call `tracker.services`, which
call `tracker.database`. That keeps the logic testable without launching the UI.

## Configuration

Set environment variables before running:

| Variable | Default | Purpose |
|----------|---------|---------|
| `TRACKER_DB_PATH` | `data/tracker.db` | Location of the SQLite file |
| `TRACKER_CURRENCY` | `₹` | Currency symbol shown in the UI |

```bash
# macOS / Linux
TRACKER_CURRENCY='$' streamlit run app.py
# Windows (PowerShell)
$env:TRACKER_CURRENCY='$'; streamlit run app.py
```

## Migrating data from the Flask version

The schema is unchanged. Copy your old `tracker.db` to `data/tracker.db` and you're done.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Notes on behaviour

- A habit streak stays alive until the day ends: if you haven't ticked today *yet* but did yesterday, the streak isn't reset to 0.
- Expense amounts must be greater than zero.

## Ideas for next steps

- Per-category budgets with alerts
- Recurring expenses
- Habit reminders / weekly goals
- Multi-user support with authentication
- Deploy free on [Streamlit Community Cloud](https://streamlit.io/cloud)
