from __future__ import annotations

from collections import Counter
from urllib.parse import urlparse


def audit_rows(
    *,
    claims: list[dict[str, str]],
    queue: list[dict[str, str]],
    candidates: list[dict[str, str]],
    samples: list[dict[str, str]],
) -> str:
    label_counts = Counter(row.get("label", "") for row in samples if row.get("label"))
    topic_counts = Counter(row.get("topic_category", "") for row in samples if row.get("topic_category"))
    platform_counts = Counter(row.get("platform", "") for row in samples if row.get("platform"))
    missing_assets = sum(1 for row in samples if not row.get("image_path") and not row.get("thumbnail_or_screenshot_path"))
    duplicate_urls = _duplicate_count([row.get("post_url", "") for row in samples])
    invalid_label_urls = sum(1 for row in samples if not _is_http_url(row.get("label_source_url", "")))
    clip_exportable = sum(1 for row in samples if row.get("post_text") and (row.get("image_path") or row.get("thumbnail_or_screenshot_path")) and row.get("label"))

    lines = [
        "# Dataset Audit",
        "",
        "## Counts",
        "",
        f"- Claims: {len(claims)}",
        f"- Queue tasks: {len(queue)}",
        f"- Candidates: {len(candidates)}",
        f"- Samples: {len(samples)}",
        f"- CLIP exportable samples: {clip_exportable}",
        "",
        "## Labels",
        "",
    ]
    lines.extend(_counter_lines(label_counts))
    lines.extend(["", "## Topics", ""])
    lines.extend(_counter_lines(topic_counts))
    lines.extend(["", "## Platforms", ""])
    lines.extend(_counter_lines(platform_counts))
    lines.extend(
        [
            "",
            "## Quality Checks",
            "",
            f"- Missing visual assets: {missing_assets}",
            f"- Duplicate post URLs: {duplicate_urls}",
            f"- Invalid label source URLs: {invalid_label_urls}",
            "",
            "## Risk Flags",
            "",
        ]
    )
    risks = _risk_flags(samples, label_counts, missing_assets, invalid_label_urls, duplicate_urls)
    lines.extend(f"- {risk}" for risk in risks)
    return "\n".join(lines) + "\n"


def _counter_lines(counter: Counter[str]) -> list[str]:
    if not counter:
        return ["- None"]
    return [f"- {key}: {value}" for key, value in sorted(counter.items())]


def _risk_flags(
    samples: list[dict[str, str]],
    label_counts: Counter[str],
    missing_assets: int,
    invalid_label_urls: int,
    duplicate_urls: int,
) -> list[str]:
    risks: list[str] = []
    if not samples:
        risks.append("No accepted training samples yet.")
    if set(label_counts) != {"false_misleading", "true_verified"}:
        risks.append("Label imbalance: both false_misleading and true_verified are required for binary classification.")
    elif min(label_counts.values()) / max(label_counts.values()) < 0.5:
        risks.append("Label imbalance: classes are not close enough for a stable thesis experiment.")
    if missing_assets:
        risks.append("Some samples cannot be used by CLIP because visual assets are missing.")
    if invalid_label_urls:
        risks.append("Some samples are not reviewable because label source URLs are invalid.")
    if duplicate_urls:
        risks.append("Duplicate post URLs may leak train/test information.")
    if not risks:
        risks.append("None")
    return risks


def _duplicate_count(values: list[str]) -> int:
    counts = Counter(value for value in values if value)
    return sum(count - 1 for count in counts.values() if count > 1)


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
