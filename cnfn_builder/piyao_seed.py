from __future__ import annotations

import html
import json
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen

PIYAO_JRPY_SOURCE = "http://www.piyao.org.cn/jrpy/ds_e0bb8399925745768458fc917f771895.json"
PIYAO_LABEL_SOURCE = "中国互联网联合辟谣平台 / 今日辟谣"

FALSE_MARKERS = (
    "谣言",
    "不实",
    "别信",
    "虚假",
    "伪造",
    "编造",
    "造谣",
    "误导",
    "不准确",
    "假的",
    "并非",
    "实为",
    "假消息",
    "系ai生成",
    "ai合成",
    "合成配音",
    "ai魔改",
    "虚构",
    "捏造",
    "不可信",
    "不存在",
    "无关",
    "不是",
    "莫信",
    "误读",
)

EXCLUDE_TITLE_MARKERS = (
    "整治网上涉",
    "从严整治传播",
    "多平台公布",
    "处置情况",
    "网络水军案",
)

TOPIC_KEYWORDS = {
    "technology_narrative": (
        "ai",
        "人工智能",
        "生成",
        "合成",
        "标识",
        "科技",
        "芯片",
        "机器人",
        "量子",
        "卫星",
        "航天",
        "国产",
        "突破",
        "华为",
        "新能源汽车",
        "无人",
        "不明飞行物",
        "低空",
        "5g",
        "6g",
        "核污染",
        "辐射",
    ),
    "industry_economy": (
        "国企",
        "国资",
        "金融",
        "银行",
        "存款",
        "房地产",
        "房产",
        "楼市",
        "制造业",
        "产业",
        "企业",
        "公司",
        "金矿",
        "稀土",
        "海关",
        "走私",
        "农业",
        "基地",
        "小麦",
        "蒜薹",
        "鸡蛋",
        "黑猪",
        "厂房",
        "车险",
        "保险",
        "商贷",
        "贷款",
        "破产",
        "倒闭",
    ),
    "policy_politics": (
        "政策",
        "制度",
        "政务",
        "通知",
        "规定",
        "新规",
        "办理",
        "户籍",
        "驾考",
        "车牌",
        "摇号",
        "高速",
        "交通",
        "封山",
        "停保",
        "养老金",
        "国资委",
        "网信",
        "医保局",
        "公安",
    ),
    "livelihood_economy": (
        "就业",
        "收入",
        "工资",
        "物价",
        "社保",
        "医保",
        "养老",
        "补贴",
        "低保",
        "滞销",
        "菜市场",
        "食品",
        "学校",
        "医院",
        "居民",
        "房贷",
        "物业",
        "快递",
        "招聘",
        "事故",
        "灾害",
        "暴雨",
        "洪水",
        "地震",
        "积水",
        "起火",
        "农业",
        "小麦",
        "鸡蛋",
    ),
}

TOPIC_TARGETS = {
    "policy_politics": 12,
    "livelihood_economy": 18,
    "industry_economy": 8,
    "technology_narrative": 12,
}


def fetch_piyao_items(source_url: str = PIYAO_JRPY_SOURCE) -> list[dict[str, object]]:
    request = Request(source_url, headers={"User-Agent": "CNFN-Builder/0.1"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    items = payload.get("datasource", [])
    if not isinstance(items, list):
        raise ValueError("piyao datasource is not a list")
    return [item for item in items if isinstance(item, dict)]


def build_seed_rows(
    items: list[dict[str, object]],
    limit: int = 50,
    source_url: str = PIYAO_JRPY_SOURCE,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    selected = select_seed_items(items, limit)
    claims: list[dict[str, str]] = []
    queue: list[dict[str, str]] = []
    for index, item in enumerate(selected, start=1):
        title = _clean_text(str(item.get("title") or item.get("showTitle") or ""))
        claim_text = _claim_from_title(title)
        topic = classify_topic(title)
        label_source_url = urljoin(source_url.replace("http://", "https://", 1), str(item.get("publishUrl") or ""))
        keywords = _clean_text(str(item.get("keywords") or ""))
        search_queries = _search_queries(claim_text)
        claim_id = f"CLAIM_{index:06d}"
        claims.append(
            {
                "claim_id": claim_id,
                "claim_text": claim_text,
                "topic_category": topic,
                "label": "false_misleading",
                "label_source": PIYAO_LABEL_SOURCE,
                "label_source_url": label_source_url,
                "keywords": keywords,
                "search_queries": search_queries,
                "notes": (
                    f"seeded_from=piyao_jrpy; publish_time={item.get('publishTime', '')}; "
                    f"source_content_id={item.get('contentId', '')}; needs_platform_match"
                ),
            }
        )
        queue.append(
            {
                "queue_id": f"QUEUE_{index:06d}",
                "claim_id": claim_id,
                "topic_category": topic,
                "label": "false_misleading",
                "target_platforms": "x|youtube|tiktok",
                "search_queries": search_queries,
                "preferred_modalities": "post_text+image|title+thumbnail|screenshot",
                "status": "todo",
                "candidate_post_url": "",
                "candidate_asset_path": "",
                "review_notes": "Find public platform post/video matching this checked claim; do not add to sample_manifest until URL and visual evidence are saved.",
            }
        )
    return claims, queue


def select_seed_items(items: list[dict[str, object]], limit: int = 50) -> list[dict[str, object]]:
    candidates = [item for item in items if is_false_or_misleading_title(str(item.get("title") or ""))]
    buckets: dict[str, list[dict[str, object]]] = {topic: [] for topic in TOPIC_TARGETS}
    for item in candidates:
        buckets[classify_topic(str(item.get("title") or ""))].append(item)

    selected: list[dict[str, object]] = []
    seen: set[str] = set()
    for topic, target in TOPIC_TARGETS.items():
        for item in buckets[topic][:target]:
            key = str(item.get("contentId") or item.get("publishUrl") or item.get("title"))
            if key in seen:
                continue
            selected.append(item)
            seen.add(key)

    for item in candidates:
        if len(selected) >= limit:
            break
        key = str(item.get("contentId") or item.get("publishUrl") or item.get("title"))
        if key not in seen:
            selected.append(item)
            seen.add(key)
    return selected[:limit]


def is_false_or_misleading_title(title: str) -> bool:
    normalized = _clean_text(title)
    lowered = normalized.lower()
    if any(marker.lower() in lowered for marker in EXCLUDE_TITLE_MARKERS):
        return False
    return any(marker in lowered for marker in FALSE_MARKERS)


def classify_topic(text: str) -> str:
    lowered = _clean_text(text).lower()
    scores = {
        topic: sum(1 for keyword in keywords if keyword.lower() in lowered)
        for topic, keywords in TOPIC_KEYWORDS.items()
    }
    best_topic = max(scores, key=lambda topic: (scores[topic], _topic_order(topic)))
    if scores[best_topic] == 0:
        return "livelihood_economy"
    return best_topic


def _topic_order(topic: str) -> int:
    order = ["technology_narrative", "industry_economy", "policy_politics", "livelihood_economy"]
    return len(order) - order.index(topic)


def _claim_from_title(title: str) -> str:
    title = re.sub(r"[（(]20\d{2}[·年.\-/]\d{1,2}(?:[·月.\-/]\d{1,2}日?)?[）)]", "", title)
    title = re.sub(r"——?今日辟谣.*$", "", title)
    ai_match = re.search(r"利用AI造谣[“\"]?([^”\"]+)[”\"]?", title)
    if ai_match:
        return ai_match.group(1).strip(" 、，。")
    ai_fabrication_match = re.search(r"利用AI编造[“\"]?([^”\"]+)[”\"]?", title)
    if ai_fabrication_match:
        return ai_fabrication_match.group(1).strip(" 、，。")
    title = title.replace("“", "").replace("”", "").replace('"', "")
    title = re.sub(r"^网传", "", title)
    title = re.sub(r"^造谣", "", title)
    title = re.sub(r"^编造(.+)，涉事账号被处罚$", r"\1", title)
    title = re.sub(r"^涉(.+)，这些信息是谣言$", r"\1相关不实信息", title)
    title = re.sub(r"视频实为.*$", "", title)
    title = re.sub(r"为AI合成配音.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"系AI生成.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"为AI生成.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"系网民编造.*$", "", title)
    title = re.sub(r"系谣言.*$", "", title)
    title = re.sub(r"纯属谣言.*$", "", title)
    title = re.sub(r"是谣言.*$", "", title)
    title = re.sub(r"纯属造谣.*$", "", title)
    title = re.sub(r"不实.*$", "", title)
    title = re.sub(r"别信.*$", "", title)
    title = re.sub(r"系编造.*$", "", title)
    title = re.sub(r"编造炒作.*$", "", title)
    title = re.sub(r"是不准确的信息解读.*$", "", title)
    title = re.sub(r"，?没有这个.*$", "", title)
    title = re.sub(r"者被处罚.*$", "", title)
    return title.strip(" 、，。")


def _search_queries(claim_text: str) -> str:
    compact = claim_text.strip(" “”、，。")
    compact = re.sub(r"[“”\"']", "", compact)
    compact = compact[:80]
    return "; ".join(
        [
            compact,
            f"{compact} 图片",
            f"{compact} 视频",
            f"{compact} site:x.com OR site:youtube.com OR site:tiktok.com",
        ]
    )


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()
