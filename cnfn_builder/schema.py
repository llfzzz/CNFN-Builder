from __future__ import annotations

CLAIM_FIELDS = [
    "claim_id",
    "claim_text",
    "topic_category",
    "label",
    "label_source",
    "label_source_url",
    "keywords",
    "search_queries",
    "notes",
]

SAMPLE_FIELDS = [
    "sample_id",
    "platform",
    "post_url",
    "post_text",
    "image_path",
    "thumbnail_or_screenshot_path",
    "topic_category",
    "label",
    "label_source",
    "label_source_url",
    "collection_date",
    "notes",
]

PUBLIC_FIELDS = [
    "sample_id",
    "platform",
    "platform_content_id",
    "post_url",
    "topic_category",
    "label",
    "label_source",
    "label_source_url",
    "collection_date",
    "notes",
]

PLATFORMS = {"x", "youtube", "tiktok", "fact_check_site", "other"}

LABELS = {"false_misleading", "true_verified"}

TOPIC_CATEGORIES = {
    "policy_politics",
    "livelihood_economy",
    "industry_economy",
    "technology_narrative",
}

DEFAULT_DIRS = [
    "data",
    "assets_local/images",
    "assets_local/screenshots",
    "assets_local/thumbnails",
]
