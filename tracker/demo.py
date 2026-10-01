"""Sample data so the app looks alive on first launch."""
from __future__ import annotations

import random
from datetime import date, timedelta

from tracker.services import expenses, habits

_EXPENSES = [
    ("Food", "Lunch", 120, 260),
    ("Food", "Dinner out", 300, 700),
    ("Transport", "Auto / cab", 40, 250),
    ("Groceries", "Weekly vegetables", 250, 800),
    ("Bills", "Mobile recharge", 199, 399),
    ("Entertainment", "Movie", 200, 450),
    ("Shopping", "Misc shopping", 300, 1500),
    ("Health", "Pharmacy", 80, 400),
]
_HABITS = ["Read 20 pages", "Workout", "Drink 3L water", "Meditate"]


def seed_demo_data(days: int = 75, seed: int = 42) -> None:
    rng = random.Random(seed)
    today = date.today()

    for offset in range(days):
        day = today - timedelta(days=offset)
        for _ in range(rng.choice([0, 1, 1, 2])):
            category, note, low, high = rng.choice(_EXPENSES)
            expenses.add_expense(round(rng.uniform(low, high), 2), category, note, day)

    for name in _HABITS:
        try:
            habits.add_habit(name)
        except ValueError:
            pass  # already exists
    probability = {"Read 20 pages": 0.7, "Workout": 0.55, "Drink 3L water": 0.8, "Meditate": 0.45}
    for summary in habits.get_habit_summaries():
        p = probability.get(summary.name, 0.6)
        for offset in range(45):
            if rng.random() < p or offset < 3 and p > 0.6:
                habits.set_log(summary.id, today - timedelta(days=offset), True)
