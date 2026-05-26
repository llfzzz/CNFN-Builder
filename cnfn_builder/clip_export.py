from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable

from .schema import LABEL_IDS


def clip_rows(samples: list[dict[str, str]], check_assets: bool = False) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for sample in samples:
        image_path = sample.get("image_path") or sample.get("thumbnail_or_screenshot_path")
        if not sample.get("post_text") or not image_path or sample.get("label") not in LABEL_IDS:
            continue
        if check_assets and not Path(image_path).exists():
            continue
        rows.append(
            {
                "sample_id": sample.get("sample_id", ""),
                "text": sample.get("post_text", ""),
                "image_path": image_path,
                "label": sample.get("label", ""),
                "label_id": LABEL_IDS[sample.get("label", "")],
                "topic_category": sample.get("topic_category", ""),
                "split": "",
                "post_url": sample.get("post_url", ""),
                "label_source_url": sample.get("label_source_url", ""),
            }
        )
    return rows


def split_rows(rows: list[dict[str, object]], seed: int = 42) -> list[dict[str, object]]:
    shuffled = [dict(row) for row in rows]
    random.Random(seed).shuffle(shuffled)
    total = len(shuffled)
    if total == 0:
        return []
    train_count = max(1, int(total * 0.7))
    val_count = 1 if total - train_count > 0 else 0
    if total >= 4:
        val_count = max(1, int(total * 0.15))
    if train_count + val_count > total:
        val_count = max(0, total - train_count)
    for index, row in enumerate(shuffled):
        if index < train_count:
            row["split"] = "train"
        elif index < train_count + val_count:
            row["split"] = "val"
        else:
            row["split"] = "test"
    return sorted(shuffled, key=lambda row: str(row.get("sample_id", "")))


def write_jsonl(path: str | Path, rows: Iterable[dict[str, object]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
