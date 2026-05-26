from __future__ import annotations

from collections import Counter


def counter_by(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(row.get(field, "") or "(blank)" for row in rows)


def print_counter(title: str, counter: Counter[str]) -> None:
    print(title)
    for key, value in sorted(counter.items()):
        print(f"  {key}: {value}")
