from cnfn_builder.validators import validate_claim, validate_sample


def test_valid_claim():
    row = {
        "claim_id": "CLAIM_000001",
        "claim_text": "example claim",
        "topic_category": "policy_politics",
        "label": "false_misleading",
        "label_source": "source",
        "label_source_url": "https://example.com/check",
        "keywords": "example",
        "search_queries": "example query",
        "notes": "",
    }
    assert validate_claim(row, 2) == []


def test_invalid_sample_requires_visual_asset():
    row = {
        "sample_id": "CNFN_000001",
        "platform": "x",
        "post_url": "https://x.com/u/status/1",
        "post_text": "text",
        "image_path": "",
        "thumbnail_or_screenshot_path": "",
        "topic_category": "policy_politics",
        "label": "false_misleading",
        "label_source": "source",
        "label_source_url": "https://example.com/check",
        "collection_date": "2026-05-26",
        "notes": "",
    }
    errors = validate_sample(row, 2)
    assert any("image_path or thumbnail_or_screenshot_path" in error for error in errors)
