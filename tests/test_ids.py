from cnfn_builder.ids import platform_content_id


def test_youtube_watch_id():
    assert platform_content_id("youtube", "https://www.youtube.com/watch?v=abc123") == "abc123"


def test_youtube_short_id():
    assert platform_content_id("youtube", "https://youtu.be/abc123") == "abc123"


def test_x_status_id():
    assert platform_content_id("x", "https://x.com/user/status/1234567890") == "1234567890"


def test_tiktok_video_id():
    assert platform_content_id("tiktok", "https://www.tiktok.com/@user/video/1234567890") == "1234567890"
