import json

from cnfn_builder.audit import audit_rows
from cnfn_builder.candidates import add_candidate, review_candidate
from cnfn_builder.capture import capture_url
from cnfn_builder.clip_export import clip_rows, split_rows
from cnfn_builder.io_utils import read_csv, write_csv
from cnfn_builder.samples import accept_sample
from cnfn_builder.schema import CANDIDATE_FIELDS, QUEUE_FIELDS, SAMPLE_FIELDS
from cnfn_builder.true_queue import build_true_queue_rows
from cnfn_builder.validators import validate_candidate


def test_valid_candidate_row():
    row = {
        "candidate_id": "CAND_000001",
        "queue_id": "QUEUE_000001",
        "claim_id": "CLAIM_000001",
        "platform": "youtube",
        "candidate_url": "https://www.youtube.com/watch?v=abc",
        "candidate_text": "title and description",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "media_url": "",
        "published_at": "2026-05-26T00:00:00Z",
        "source_method": "manual",
        "match_status": "unreviewed",
        "notes": "",
    }
    assert validate_candidate(row, 2) == []


def test_add_and_review_candidate(tmp_path):
    path = tmp_path / "candidate_posts.csv"
    write_csv(path, CANDIDATE_FIELDS, [])

    created = add_candidate(
        path,
        {
            "queue_id": "QUEUE_000001",
            "claim_id": "CLAIM_000001",
            "platform": "youtube",
            "candidate_url": "https://www.youtube.com/watch?v=abc",
            "candidate_text": "candidate text",
            "source_method": "manual",
        },
    )
    assert created["candidate_id"] == "CAND_000001"
    assert created["match_status"] == "unreviewed"

    reviewed = review_candidate(path, "CAND_000001", "accepted", "usable thumbnail")
    assert reviewed["match_status"] == "accepted"
    assert "usable thumbnail" in reviewed["notes"]


def test_seed_true_queue_only_creates_search_tasks():
    claims = [
        {
            "claim_id": "CLAIM_000001",
            "claim_text": "5月银行存款计息出新规",
            "topic_category": "industry_economy",
            "label": "false_misleading",
        }
    ]
    rows = build_true_queue_rows(claims, limit=1)
    assert rows[0]["queue_id"] == "TRUE_QUEUE_000001"
    assert rows[0]["label"] == "true_verified"
    assert "site:gov.cn" in rows[0]["search_queries"]


def test_accept_sample_from_candidate_updates_files(tmp_path):
    candidates_path = tmp_path / "candidate_posts.csv"
    queue_path = tmp_path / "collection_queue.csv"
    samples_path = tmp_path / "sample_manifest.csv"
    asset = tmp_path / "shot.png"
    asset.write_bytes(b"fake")

    write_csv(
        candidates_path,
        CANDIDATE_FIELDS,
        [
            {
                "candidate_id": "CAND_000001",
                "queue_id": "QUEUE_000001",
                "claim_id": "CLAIM_000001",
                "platform": "youtube",
                "candidate_url": "https://www.youtube.com/watch?v=abc",
                "candidate_text": "candidate text",
                "thumbnail_url": "",
                "media_url": "",
                "published_at": "",
                "source_method": "manual",
                "match_status": "unreviewed",
                "notes": "",
            }
        ],
    )
    write_csv(
        queue_path,
        QUEUE_FIELDS,
        [
            {
                "queue_id": "QUEUE_000001",
                "claim_id": "CLAIM_000001",
                "topic_category": "policy_politics",
                "label": "false_misleading",
                "target_platforms": "x|youtube|tiktok",
                "search_queries": "query",
                "preferred_modalities": "title+thumbnail",
                "status": "todo",
                "candidate_post_url": "",
                "candidate_asset_path": "",
                "review_notes": "",
            }
        ],
    )
    write_csv(samples_path, SAMPLE_FIELDS, [])

    sample = accept_sample(
        samples_path=samples_path,
        candidates_path=candidates_path,
        queue_path=queue_path,
        candidate_id="CAND_000001",
        thumbnail_or_screenshot_path=str(asset),
        label_source="source",
        label_source_url="https://example.com/check",
        collection_date="2026-05-26",
    )

    assert sample["sample_id"] == "CNFN_000001"
    assert sample["post_text"] == "candidate text"
    assert read_csv(candidates_path)[0]["match_status"] == "accepted"
    assert read_csv(queue_path)[0]["status"] == "accepted"


def test_accept_sample_rejects_duplicate_post_url(tmp_path):
    samples_path = tmp_path / "sample_manifest.csv"
    write_csv(
        samples_path,
        SAMPLE_FIELDS,
        [
            {
                "sample_id": "CNFN_000001",
                "platform": "youtube",
                "post_url": "https://www.youtube.com/watch?v=abc",
                "post_text": "old",
                "image_path": "",
                "thumbnail_or_screenshot_path": "shot.png",
                "topic_category": "policy_politics",
                "label": "false_misleading",
                "label_source": "source",
                "label_source_url": "https://example.com/check",
                "collection_date": "2026-05-26",
                "notes": "",
            }
        ],
    )

    try:
        accept_sample(
            samples_path=samples_path,
            post_url="https://www.youtube.com/watch?v=abc",
            post_text="new",
            platform="youtube",
            topic_category="policy_politics",
            label="false_misleading",
            thumbnail_or_screenshot_path="shot2.png",
            label_source="source",
            label_source_url="https://example.com/check",
            collection_date="2026-05-26",
        )
    except ValueError as exc:
        assert "duplicate post_url" in str(exc)
    else:
        raise AssertionError("duplicate URL was accepted")


def test_clip_export_rows_and_splits_are_stable(tmp_path):
    img1 = tmp_path / "a.png"
    img2 = tmp_path / "b.png"
    img1.write_bytes(b"a")
    img2.write_bytes(b"b")
    samples = [
        {
            "sample_id": "CNFN_000001",
            "post_text": "false text",
            "image_path": str(img1),
            "thumbnail_or_screenshot_path": "",
            "label": "false_misleading",
            "topic_category": "policy_politics",
            "post_url": "https://example.com/1",
            "label_source_url": "https://example.com/check1",
        },
        {
            "sample_id": "CNFN_000002",
            "post_text": "true text",
            "image_path": "",
            "thumbnail_or_screenshot_path": str(img2),
            "label": "true_verified",
            "topic_category": "policy_politics",
            "post_url": "https://example.com/2",
            "label_source_url": "https://example.com/check2",
        },
    ]
    rows = clip_rows(samples)
    assert rows[0]["label_id"] == 0
    assert rows[1]["label_id"] == 1
    splits = split_rows(rows, seed=42)
    assert sorted(row["split"] for row in splits) == ["train", "val"]
    json.dumps(splits[0], ensure_ascii=False)


def test_audit_flags_empty_and_missing_assets():
    report = audit_rows(
        claims=[],
        queue=[],
        candidates=[],
        samples=[
            {
                "sample_id": "CNFN_000001",
                "platform": "youtube",
                "post_url": "https://example.com/1",
                "post_text": "text",
                "image_path": "",
                "thumbnail_or_screenshot_path": "",
                "topic_category": "policy_politics",
                "label": "false_misleading",
                "label_source": "source",
                "label_source_url": "not-a-url",
                "collection_date": "2026-05-26",
                "notes": "",
            }
        ],
    )
    assert "Missing visual assets: 1" in report
    assert "Invalid label source URLs: 1" in report
    assert "Label imbalance" in report


def test_capture_url_reports_missing_playwright(tmp_path):
    out = tmp_path / "shot.png"
    result = capture_url("https://example.com", out, browser_timeout_ms=1000)
    if result.ok:
        assert out.exists()
    else:
        assert "Playwright is not installed" in result.message or "playwright install" in result.message
