from cnfn_builder.piyao_seed import build_seed_rows, classify_topic, is_false_or_misleading_title


def test_false_marker_detection():
    assert is_false_or_misleading_title("网传“5月银行存款计息出新规”不实")
    assert not is_false_or_misleading_title("近期政策解读")


def test_topic_classification_prefers_tech_for_ai_content():
    assert classify_topic("利用AI编造假视频") == "technology_narrative"
    assert classify_topic("5月银行存款计息出新规不实") == "industry_economy"


def test_build_seed_rows_outputs_claims_and_queue():
    items = [
        {
            "title": "网传“5月银行存款计息出新规”不实（2026·05·11）",
            "publishUrl": "../20260511/example/c.html",
            "publishTime": "2026-05-11 10:00:00",
            "contentId": "abc",
            "keywords": "银行,存款",
        }
    ]
    claims, queue = build_seed_rows(items, 1, "http://www.piyao.org.cn/jrpy/ds.json")
    assert claims[0]["claim_id"] == "CLAIM_000001"
    assert claims[0]["claim_text"] == "5月银行存款计息出新规"
    assert claims[0]["topic_category"] == "industry_economy"
    assert claims[0]["label"] == "false_misleading"
    assert queue[0]["claim_id"] == claims[0]["claim_id"]
    assert queue[0]["status"] == "todo"
