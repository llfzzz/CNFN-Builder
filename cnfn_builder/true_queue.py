from __future__ import annotations

from .schema import QUEUE_FIELDS

AUTHORITY_QUERY_SUFFIX = (
    "site:gov.cn OR site:xinhuanet.com OR site:people.com.cn OR "
    "site:cctv.com OR site:news.cn"
)


def build_true_queue_rows(claims: list[dict[str, str]], limit: int = 50) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    false_claims = [row for row in claims if row.get("label") == "false_misleading"]
    for index, claim in enumerate(false_claims[:limit], start=1):
        claim_text = claim.get("claim_text", "")
        topic = claim.get("topic_category", "")
        row = {
            "queue_id": f"TRUE_QUEUE_{index:06d}",
            "claim_id": f"{claim.get('claim_id', f'CLAIM_{index:06d}')}_TRUE",
            "topic_category": topic,
            "label": "true_verified",
            "target_platforms": "other|youtube|x",
            "search_queries": _true_queries(claim_text, topic),
            "preferred_modalities": "authority_page+screenshot|title+thumbnail|post_text+image",
            "status": "todo",
            "candidate_post_url": "",
            "candidate_asset_path": "",
            "review_notes": "Find an authoritative same-topic true/verified item; do not accept without a real URL and visual asset.",
        }
        rows.append({field: row.get(field, "") for field in QUEUE_FIELDS})
    return rows


def _true_queries(claim_text: str, topic: str) -> str:
    topic_hint = {
        "policy_politics": "官方 通知 政策",
        "livelihood_economy": "官方 回应 民生",
        "industry_economy": "权威 发布 经济",
        "technology_narrative": "权威 科技 发布",
    }.get(topic, "权威 发布")
    return "; ".join(
        [
            f"{claim_text} {topic_hint}",
            f"{claim_text} {AUTHORITY_QUERY_SUFFIX}",
            f"{topic_hint} {AUTHORITY_QUERY_SUFFIX}",
        ]
    )
