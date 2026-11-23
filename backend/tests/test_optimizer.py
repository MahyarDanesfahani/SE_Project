from datetime import time
from types import SimpleNamespace

from app.modules.offerings.optimizer import generate_valid_scenarios, overlaps


def session(day: int, start: int, end: int):
    return SimpleNamespace(weekday=day, start_time=time(start), end_time=time(end))


def test_overlapping_sessions_are_rejected() -> None:
    left = SimpleNamespace(sessions=[session(0, 8, 10)])
    right = SimpleNamespace(sessions=[session(0, 9, 11)])
    assert overlaps(left.sessions[0], right.sessions[0])
    assert generate_valid_scenarios([[left], [right]], 5) == []


def test_non_overlapping_groups_produce_scenario() -> None:
    left = SimpleNamespace(sessions=[session(0, 8, 10)])
    right = SimpleNamespace(sessions=[session(0, 10, 12)])
    scenarios = generate_valid_scenarios([[left], [right]], 5)
    assert len(scenarios) == 1
