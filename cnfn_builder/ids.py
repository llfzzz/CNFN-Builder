from __future__ import annotations

from urllib.parse import parse_qs, urlparse
import re


def platform_content_id(platform: str, url: str) -> str:
    platform = platform.lower().strip()
    if platform == "youtube":
        return _youtube_id(url)
    if platform == "x":
        return _x_status_id(url)
    if platform == "tiktok":
        return _tiktok_video_id(url)
    return ""


def _youtube_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.endswith("youtu.be"):
        return parsed.path.strip("/").split("/")[0]
    query_id = parse_qs(parsed.query).get("v", [""])[0]
    if query_id:
        return query_id
    match = re.search(r"/(?:shorts|embed)/([^/?#]+)", parsed.path)
    return match.group(1) if match else ""


def _x_status_id(url: str) -> str:
    match = re.search(r"/status(?:es)?/(\d+)", url)
    return match.group(1) if match else ""


def _tiktok_video_id(url: str) -> str:
    match = re.search(r"/video/(\d+)", url)
    return match.group(1) if match else ""
