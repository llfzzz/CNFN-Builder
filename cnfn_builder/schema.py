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

QUEUE_FIELDS = [
    "queue_id",
    "claim_id",
    "topic_category",
    "label",
    "target_platforms",
    "search_queries",
    "preferred_modalities",
    "status",
    "candidate_post_url",
    "candidate_asset_path",
    "review_notes",
]

CANDIDATE_FIELDS = [
    "candidate_id",
    "queue_id",
    "claim_id",
    "platform",
    "candidate_url",
    "candidate_text",
    "thumbnail_url",
    "media_url",
    "published_at",
    "source_method",
    "match_status",
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

QUEUE_STATUSES = {"todo", "candidate_found", "accepted", "rejected", "blocked"}

CANDIDATE_STATUSES = {"unreviewed", "accepted", "rejected", "blocked"}

LABEL_IDS = {"false_misleading": 0, "true_verified": 1}

TOPIC_CATEGORIES = {
    "policy_politics",
    "livelihood_economy",
    "industry_economy",
    "technology_narrative",
}

DEFAULT_DIRS = [
    "data",
    "data/splits",
    "reports",
    "assets_local/images",
    "assets_local/screenshots",
    "assets_local/thumbnails",
]
