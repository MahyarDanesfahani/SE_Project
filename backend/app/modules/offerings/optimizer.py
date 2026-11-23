from itertools import product
from typing import Any


def overlaps(left: Any, right: Any) -> bool:
    return left.weekday == right.weekday and left.start_time < right.end_time and right.start_time < left.end_time


def generate_valid_scenarios(groups: list[list[Any]], limit: int) -> list[list[Any]]:
    scenarios: list[list[Any]] = []
    for candidate in product(*groups):
        sessions = [session for offering in candidate for session in offering.sessions]
        if any(overlaps(left, right) for index, left in enumerate(sessions) for right in sessions[index + 1 :]):
            continue
        scenarios.append(list(candidate))
        if len(scenarios) >= limit:
            break
    return scenarios
