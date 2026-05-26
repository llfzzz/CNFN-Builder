from __future__ import annotations

from .ids import platform_content_id
from .schema import PUBLIC_FIELDS


def public_manifest_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    exported: list[dict[str, str]] = []
    for row in rows:
        exported.append(
            {
                "sample_id": row.get("sample_id", ""),
                "platform": row.get("platform", ""),
                "platform_content_id": platform_content_id(row.get("platform", ""), row.get("post_url", "")),
                "post_url": row.get("post_url", ""),
                "topic_category": row.get("topic_category", ""),
                "label": row.get("label", ""),
                "label_source": row.get("label_source", ""),
                "label_source_url": row.get("label_source_url", ""),
                "collection_date": row.get("collection_date", ""),
                "notes": row.get("notes", ""),
            }
        )
    return exported


__all__ = ["PUBLIC_FIELDS", "public_manifest_rows"]
