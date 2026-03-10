from __future__ import annotations

import os
import random
from dataclasses import dataclass


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


# Real Chrome user-agent strings for rotation
_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


@dataclass(frozen=True)
class GoogleShoppingConfig:
    headless: bool
    max_review_pages: int
    delay_ms: int
    timeout_ms: int
    user_agent: str
    locale: str
    country: str
    stealth: bool
    profile_dir: str | None

    @classmethod
    def from_env(cls, project_root: "Path | None" = None) -> "GoogleShoppingConfig":
        from pathlib import Path

        headless = _env_flag("GOOGLE_HEADLESS", default=True)
        max_review_pages = _env_int("GOOGLE_MAX_REVIEW_PAGES", default=10)
        delay_ms = _env_int("GOOGLE_DELAY_MS", default=3000)
        timeout_ms = _env_int("GOOGLE_TIMEOUT_MS", default=30000)
        user_agent = os.getenv("GOOGLE_USER_AGENT", "").strip() or random.choice(_USER_AGENTS)
        locale = os.getenv("GOOGLE_LOCALE", "en").strip() or "en"
        country = os.getenv("GOOGLE_COUNTRY", "us").strip() or "us"
        stealth = _env_flag("GOOGLE_STEALTH", default=True)
        default_profile = str(project_root / ".google-profile") if project_root else ".google-profile"
        profile_dir = os.getenv("GOOGLE_PROFILE_DIR", "").strip() or default_profile
        return cls(
            headless=headless,
            max_review_pages=max_review_pages,
            delay_ms=delay_ms,
            timeout_ms=timeout_ms,
            user_agent=user_agent,
            locale=locale,
            country=country,
            stealth=stealth,
            profile_dir=profile_dir,
        )
