from __future__ import annotations

from pathlib import Path

from .io_utils import read_csv, write_csv
from .schema import CANDIDATE_FIELDS, QUEUE_FIELDS, SAMPLE_FIELDS
from .validators import validate_sample


def accept_sample(
    *,
    samples_path: str | Path,
    candidates_path: str | Path | None = None,
    queue_path: str | Path | None = None,
    candidate_id: str = "",
    platform: str = "",
    post_url: str = "",
    post_text: str = "",
    image_path: str = "",
    thumbnail_or_screenshot_path: str = "",
    topic_category: str = "",
    label: str = "",
    label_source: str = "",
    label_source_url: str = "",
    collection_date: str = "",
    notes: str = "",
) -> dict[str, str]:
    samples = read_csv(samples_path)
    candidate = _find_candidate(candidates_path, candidate_id) if candidate_id and candidates_path else {}
    queue = _find_queue(queue_path, candidate.get("queue_id", "")) if candidate and queue_path else {}

    post_url = post_url or candidate.get("candidate_url", "")
    if post_url and any(row.get("post_url") == post_url for row in samples):
        raise ValueError(f"duplicate post_url: {post_url}")

    asset_path = image_path or thumbnail_or_screenshot_path
    if not asset_path:
        raise ValueError("image_path or thumbnail_or_screenshot_path is required")

    row = {
        "sample_id": _next_sample_id(samples),
        "platform": platform or candidate.get("platform", ""),
        "post_url": post_url,
        "post_text": post_text or candidate.get("candidate_text", ""),
        "image_path": image_path,
        "thumbnail_or_screenshot_path": thumbnail_or_screenshot_path,
        "topic_category": topic_category or queue.get("topic_category", ""),
        "label": label or queue.get("label", ""),
        "label_source": label_source,
        "label_source_url": label_source_url,
        "collection_date": collection_date,
        "notes": notes,
    }
    errors = validate_sample(row, len(samples) + 2)
    if errors:
        raise ValueError("; ".join(errors))
    samples.append(row)
    write_csv(samples_path, SAMPLE_FIELDS, samples)

    if candidate and candidates_path:
        _update_candidate(candidates_path, candidate_id, row["sample_id"])
    if queue and queue_path:
        _update_queue(queue_path, queue["queue_id"], post_url, asset_path, row["sample_id"])
    return row


def _find_candidate(path: str | Path | None, candidate_id: str) -> dict[str, str]:
    for row in read_csv(path or ""):
        if row.get("candidate_id") == candidate_id:
            return row
    raise ValueError(f"candidate not found: {candidate_id}")


def _find_queue(path: str | Path | None, queue_id: str) -> dict[str, str]:
    for row in read_csv(path or ""):
        if row.get("queue_id") == queue_id:
            return row
    return {}


def _update_candidate(path: str | Path, candidate_id: str, sample_id: str) -> None:
    rows = read_csv(path)
    for row in rows:
        if row.get("candidate_id") == candidate_id:
            row["match_status"] = "accepted"
            row["notes"] = _append_note(row.get("notes", ""), f"accepted_as={sample_id}")
            break
    write_csv(path, CANDIDATE_FIELDS, rows)


def _update_queue(path: str | Path, queue_id: str, post_url: str, asset_path: str, sample_id: str) -> None:
    rows = read_csv(path)
    for row in rows:
        if row.get("queue_id") == queue_id:
            row["status"] = "accepted"
            row["candidate_post_url"] = post_url
            row["candidate_asset_path"] = asset_path
            row["review_notes"] = _append_note(row.get("review_notes", ""), f"accepted_as={sample_id}")
            break
    write_csv(path, QUEUE_FIELDS, rows)


def _next_sample_id(rows: list[dict[str, str]]) -> str:
    max_number = 0
    for row in rows:
        value = row.get("sample_id", "")
        if value.startswith("CNFN_"):
            try:
                max_number = max(max_number, int(value.split("_", 1)[1]))
            except ValueError:
                continue
    return f"CNFN_{max_number + 1:06d}"


def _append_note(existing: str, note: str) -> str:
    return f"{existing} | {note}" if existing else note
