from __future__ import annotations

from pathlib import Path

from .io_utils import read_csv, write_csv
from .schema import CANDIDATE_FIELDS, CANDIDATE_STATUSES


def add_candidate(path: str | Path, values: dict[str, str]) -> dict[str, str]:
    rows = read_csv(path)
    row = {field: values.get(field, "") for field in CANDIDATE_FIELDS}
    row["candidate_id"] = row.get("candidate_id") or _next_id(rows)
    row["match_status"] = row.get("match_status") or "unreviewed"
    row["source_method"] = row.get("source_method") or "manual"
    rows.append(row)
    write_csv(path, CANDIDATE_FIELDS, rows)
    return row


def import_candidate_rows(path: str | Path, imported_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    created: list[dict[str, str]] = []
    for row in imported_rows:
        created.append(add_candidate(path, normalize_imported_candidate(row)))
    return created


def normalize_imported_candidate(row: dict[str, str]) -> dict[str, str]:
    if "candidate_url" in row:
        return row
    if row.get("platform") == "youtube" or row.get("url", "").startswith("https://www.youtube.com/"):
        text = " ".join(part for part in [row.get("title", ""), row.get("description", "")] if part)
        return {
            "queue_id": row.get("queue_id", ""),
            "claim_id": row.get("claim_id", ""),
            "platform": "youtube",
            "candidate_url": row.get("url", ""),
            "candidate_text": text,
            "thumbnail_url": row.get("thumbnail_url", ""),
            "media_url": "",
            "published_at": row.get("published_at", ""),
            "source_method": row.get("source_method", "youtube_api"),
            "notes": row.get("notes", ""),
        }
    return {
        "queue_id": row.get("queue_id", ""),
        "claim_id": row.get("claim_id", ""),
        "platform": row.get("platform", "x"),
        "candidate_url": row.get("url", row.get("candidate_url", "")),
        "candidate_text": row.get("text", row.get("candidate_text", "")),
        "thumbnail_url": row.get("thumbnail_url", ""),
        "media_url": row.get("media_urls", row.get("media_url", "")),
        "published_at": row.get("created_at", row.get("published_at", "")),
        "source_method": row.get("source_method", "manual_import"),
        "notes": row.get("notes", ""),
    }


def review_candidate(path: str | Path, candidate_id: str, status: str, notes: str = "") -> dict[str, str]:
    if status not in CANDIDATE_STATUSES:
        raise ValueError(f"invalid match_status: {status}")
    rows = read_csv(path)
    for row in rows:
        if row.get("candidate_id") == candidate_id:
            row["match_status"] = status
            if notes:
                row["notes"] = _append_note(row.get("notes", ""), notes)
            write_csv(path, CANDIDATE_FIELDS, rows)
            return row
    raise ValueError(f"candidate not found: {candidate_id}")


def _next_id(rows: list[dict[str, str]]) -> str:
    max_number = 0
    for row in rows:
        value = row.get("candidate_id", "")
        if value.startswith("CAND_"):
            try:
                max_number = max(max_number, int(value.split("_", 1)[1]))
            except ValueError:
                continue
    return f"CAND_{max_number + 1:06d}"


def _append_note(existing: str, note: str) -> str:
    return f"{existing} | {note}" if existing else note
