from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def read_csv(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def write_csv(path: str | Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def ensure_csv(path: str | Path, fieldnames: list[str]) -> bool:
    csv_path = Path(path)
    if csv_path.exists():
        return False
    write_csv(csv_path, fieldnames, [])
    return True
