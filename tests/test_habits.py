from datetime import date, timedelta

import pytest

from tracker.services import habits

TODAY = date(2026, 10, 1)


def days(*offsets):
    return {TODAY - timedelta(days=o) for o in offsets}


def test_streak_counts_consecutive_days():
    assert habits.calc_streak(days(0, 1, 2), TODAY) == 3


def test_streak_survives_until_end_of_today():
    # Not done yet today, but yesterday and before were -> streak still alive
    assert habits.calc_streak(days(1, 2), TODAY) == 2


def test_streak_breaks_after_missed_day():
    assert habits.calc_streak(days(2, 3), TODAY) == 0
    assert habits.calc_streak(days(0, 2, 3), TODAY) == 1


def test_longest_streak():
    assert habits.longest_streak(set()) == 0
    assert habits.longest_streak(days(0, 1, 5, 6, 7, 8, 20)) == 4


def test_add_habit_validation(db):
    habits.add_habit("Read")
    with pytest.raises(ValueError):
        habits.add_habit("Read")
    with pytest.raises(ValueError):
        habits.add_habit("   ")


def test_toggle_and_summary(db):
    habits.add_habit("Workout")
    hid = habits.get_habit_summaries(TODAY)[0].id
    for o in (0, 1, 2):
        habits.set_log(hid, TODAY - timedelta(days=o), True)
    habits.set_log(hid, TODAY, True)  # idempotent

    s = habits.get_habit_summaries(TODAY)[0]
    assert s.streak == 3 and s.done_today and s.best_streak == 3
    assert len(s.week) == 7 and s.week[-1] == (TODAY, True)

    habits.set_log(hid, TODAY, False)
    assert not habits.get_habit_summaries(TODAY)[0].done_today


def test_delete_habit_removes_logs(db):
    habits.add_habit("Meditate")
    hid = habits.get_habit_summaries(TODAY)[0].id
    habits.set_log(hid, TODAY, True)
    habits.delete_habit(hid)
    assert habits.get_habit_summaries(TODAY) == []
    assert habits.completion_frame(5, TODAY).empty
