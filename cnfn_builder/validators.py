from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from .schema import CLAIM_FIELDS, LABELS, PLATFORMS, QUEUE_FIELDS, QUEUE_STATUSES, SAMPLE_FIELDS, TOPIC_CATEGORIES


def validate_claim(row: dict[str, str], row_number: int) -> list[str]:
    errors: list[str] = []
    _require_fields(row, CLAIM_FIELDS, row_number, errors)
    _require_value(row, "claim_id", row_number, errors)
    _require_value(row, "claim_text", row_number, errors)
    _validate_topic(row, row_number, errors)
    _validate_label(row, row_number, errors)
    _require_url(row, "label_source_url", row_number, errors)
    return errors


def validate_sample(row: dict[str, str], row_number: int, check_assets: bool = False) -> list[str]:
    errors: list[str] = []
    _require_fields(row, SAMPLE_FIELDS, row_number, errors)
    _require_value(row, "sample_id", row_number, errors)
    _validate_platform(row, row_number, errors)
    _require_url(row, "post_url", row_number, errors)
    _require_value(row, "post_text", row_number, errors)
    _validate_topic(row, row_number, errors)
    _validate_label(row, row_number, errors)
    _require_value(row, "label_source", row_number, errors)
    _require_url(row, "label_source_url", row_number, errors)
    _validate_date(row, row_number, errors)
    if not row.get("image_path") and not row.get("thumbnail_or_screenshot_path"):
        errors.append(f"row {row_number}: image_path or thumbnail_or_screenshot_path is required")
    if check_assets:
        _validate_local_asset(row, "image_path", row_number, errors)
        _validate_local_asset(row, "thumbnail_or_screenshot_path", row_number, errors)
    return errors


def validate_queue(row: dict[str, str], row_number: int) -> list[str]:
    errors: list[str] = []
    _require_fields(row, QUEUE_FIELDS, row_number, errors)
    _require_value(row, "queue_id", row_number, errors)
    _require_value(row, "claim_id", row_number, errors)
    _validate_topic(row, row_number, errors)
    _validate_label(row, row_number, errors)
    _validate_target_platforms(row, row_number, errors)
    _require_value(row, "search_queries", row_number, errors)
    _validate_queue_status(row, row_number, errors)
    candidate_url = row.get("candidate_post_url", "").strip()
    if candidate_url:
        _require_url(row, "candidate_post_url", row_number, errors)
    return errors


def _require_fields(row: dict[str, str], fields: list[str], row_number: int, errors: list[str]) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        errors.append(f"row {row_number}: missing columns {', '.join(missing)}")


def _require_value(row: dict[str, str], field: str, row_number: int, errors: list[str]) -> None:
    if not row.get(field, "").strip():
        errors.append(f"row {row_number}: {field} is required")


def _require_url(row: dict[str, str], field: str, row_number: int, errors: list[str]) -> None:
    value = row.get(field, "").strip()
    if not value:
        errors.append(f"row {row_number}: {field} is required")
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append(f"row {row_number}: {field} must be an http(s) URL")


def _validate_platform(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    value = row.get("platform", "").strip()
    if value not in PLATFORMS:
        errors.append(f"row {row_number}: platform must be one of {', '.join(sorted(PLATFORMS))}")


def _validate_target_platforms(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    value = row.get("target_platforms", "").strip()
    if not value:
        errors.append(f"row {row_number}: target_platforms is required")
        return
    platforms = [platform.strip() for platform in value.split("|") if platform.strip()]
    invalid = [platform for platform in platforms if platform not in PLATFORMS or platform in {"fact_check_site", "other"}]
    if invalid:
        errors.append(f"row {row_number}: invalid target_platforms values {', '.join(invalid)}")


def _validate_queue_status(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    value = row.get("status", "").strip()
    if value not in QUEUE_STATUSES:
        errors.append(f"row {row_number}: status must be one of {', '.join(sorted(QUEUE_STATUSES))}")


def _validate_topic(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    value = row.get("topic_category", "").strip()
    if value not in TOPIC_CATEGORIES:
        errors.append(
            f"row {row_number}: topic_category must be one of {', '.join(sorted(TOPIC_CATEGORIES))}"
        )


def _validate_label(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    value = row.get("label", "").strip()
    if value not in LABELS:
        errors.append(f"row {row_number}: label must be one of {', '.join(sorted(LABELS))}")


def _validate_date(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    value = row.get("collection_date", "").strip()
    if not value:
        errors.append(f"row {row_number}: collection_date is required")
        return
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        errors.append(f"row {row_number}: collection_date must use YYYY-MM-DD")


def _validate_local_asset(row: dict[str, str], field: str, row_number: int, errors: list[str]) -> None:
    value = row.get(field, "").strip()
    if value and not Path(value).exists():
        errors.append(f"row {row_number}: {field} does not exist locally: {value}")
