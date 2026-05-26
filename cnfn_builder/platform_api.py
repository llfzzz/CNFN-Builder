from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def search_youtube(api_key: str, query: str, max_results: int = 10) -> list[dict[str, str]]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": str(max_results),
        "key": api_key,
    }
    url = f"https://www.googleapis.com/youtube/v3/search?{urlencode(params)}"
    payload = _json_get(url)
    rows: list[dict[str, str]] = []
    for item in payload.get("items", []):
        video_id = item.get("id", {}).get("videoId", "")
        snippet = item.get("snippet", {})
        thumbs = snippet.get("thumbnails", {})
        thumb_url = (thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url", "")
        rows.append(
            {
                "platform": "youtube",
                "content_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": thumb_url,
            }
        )
    return rows


def search_x(bearer_token: str, query: str, max_results: int = 10) -> list[dict[str, str]]:
    params = {
        "query": query,
        "max_results": str(max(10, min(max_results, 100))),
        "tweet.fields": "created_at,lang,public_metrics",
        "expansions": "attachments.media_keys,author_id",
        "media.fields": "url,preview_image_url,type",
    }
    url = f"https://api.x.com/2/tweets/search/recent?{urlencode(params)}"
    request = Request(url, headers={"Authorization": f"Bearer {bearer_token}"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    media_by_key = {
        item.get("media_key", ""): item
        for item in payload.get("includes", {}).get("media", [])
    }
    rows: list[dict[str, str]] = []
    for tweet in payload.get("data", []):
        media_urls = []
        for key in tweet.get("attachments", {}).get("media_keys", []):
            media = media_by_key.get(key, {})
            media_urls.append(media.get("url") or media.get("preview_image_url") or "")
        tweet_id = tweet.get("id", "")
        rows.append(
            {
                "platform": "x",
                "content_id": tweet_id,
                "url": f"https://x.com/i/web/status/{tweet_id}" if tweet_id else "",
                "text": tweet.get("text", ""),
                "created_at": tweet.get("created_at", ""),
                "author_id": tweet.get("author_id", ""),
                "media_urls": ";".join(url for url in media_urls if url),
            }
        )
    return rows


def _json_get(url: str) -> dict:
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))
