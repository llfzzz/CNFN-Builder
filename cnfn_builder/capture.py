from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptureResult:
    ok: bool
    message: str
    path: str = ""


def capture_url(url: str, out_path: str | Path, browser_timeout_ms: int = 15000) -> CaptureResult:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return CaptureResult(
            ok=False,
            message="Playwright is not installed. Install with `python -m pip install playwright` and then run `python -m playwright install chromium`.",
        )

    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1365, "height": 900})
            page.goto(url, wait_until="networkidle", timeout=browser_timeout_ms)
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()
    except Exception as exc:
        return CaptureResult(ok=False, message=f"capture failed: {exc}", path=str(output_path))
    return CaptureResult(ok=True, message="capture saved", path=str(output_path))
