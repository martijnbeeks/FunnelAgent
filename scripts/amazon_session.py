from __future__ import annotations

import logging
import random
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None


def ensure_session_paths(profile_dir: Path, storage_state_path: Path) -> None:
    profile_dir.mkdir(parents=True, exist_ok=True)
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)


def marketplace_home_url(marketplace: str) -> str:
    host = marketplace.strip() or "www.amazon.com"
    if host.startswith("http://") or host.startswith("https://"):
        return host
    return f"https://{host}"


def has_marketplace_cookies(storage_state: dict, marketplace: str) -> bool:
    host = marketplace.replace("https://", "").replace("http://", "").strip(".")
    cookies = storage_state.get("cookies", [])
    return any(host in cookie.get("domain", "") for cookie in cookies)


def apply_stealth(page) -> None:
    """Apply playwright-stealth to a page to mask browser fingerprints."""
    if stealth_sync is not None:
        stealth_sync(page)
    else:
        logger.warning(
            "playwright-stealth not installed — running without fingerprint masking. "
            "Install with: pip install playwright-stealth"
        )


def simulate_human_behavior(page) -> None:
    """Add realistic mouse movements and scrolling before parsing."""
    viewport = page.viewport_size
    if not viewport:
        return

    # Random mouse movements
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        page.mouse.move(x, y)
        page.wait_for_timeout(random.randint(50, 200))

    # Scroll down a bit, then back up (like a human scanning the page)
    scroll_amount = random.randint(200, 500)
    page.mouse.wheel(0, scroll_amount)
    page.wait_for_timeout(random.randint(300, 800))
    page.mouse.wheel(0, -scroll_amount // 2)
    page.wait_for_timeout(random.randint(200, 500))
