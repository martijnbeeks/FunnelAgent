from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from pathlib import Path


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value.strip())
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


# Realistic Chrome User-Agent strings (Windows/Mac, Chrome 120-131)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]


@dataclass(frozen=True)
class ProxyConfig:
    server: str | None = None
    username: str | None = None
    password: str | None = None

    @property
    def enabled(self) -> bool:
        return self.server is not None and self.server != ""

    def to_playwright_proxy(self) -> dict | None:
        if not self.enabled:
            return None
        proxy: dict = {"server": self.server}
        if self.username:
            proxy["username"] = self.username
        if self.password:
            proxy["password"] = self.password
        return proxy


@dataclass(frozen=True)
class DelayConfig:
    min_page_delay: float = 3.0
    max_page_delay: float = 8.0
    initial_load_delay: float = 2.0
    max_retries: int = 3
    backoff_base: float = 10.0
    backoff_max: float = 120.0

    def page_delay(self) -> float:
        """Return a random delay between min and max with jitter."""
        base = random.uniform(self.min_page_delay, self.max_page_delay)
        jitter = random.uniform(-0.5, 0.5)
        return max(1.0, base + jitter)

    def backoff_delay(self, attempt: int) -> float:
        """Exponential backoff with jitter for retries."""
        delay = self.backoff_base * (2 ** attempt)
        delay = min(delay, self.backoff_max)
        jitter = random.uniform(0, delay * 0.3)
        return delay + jitter


@dataclass(frozen=True)
class ReviewFilterConfig:
    star_rating: str | None = None  # "1", "2", "3", "4", "5", or None for all
    verified_only: bool = False
    sort_by: str = "recent"  # "recent", "helpful", "top"


@dataclass(frozen=True)
class AmazonScraperConfig:
    profile_dir: Path
    storage_state_path: Path
    marketplace: str
    headless: bool
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    delays: DelayConfig = field(default_factory=DelayConfig)
    filters: ReviewFilterConfig = field(default_factory=ReviewFilterConfig)

    @classmethod
    def from_project_root(cls, project_root: Path) -> "AmazonScraperConfig":
        profile_dir = Path(os.getenv("AMAZON_PROFILE_DIR", project_root / ".amazon-profile"))
        storage_state_path = Path(
            os.getenv(
                "AMAZON_STORAGE_STATE_PATH",
                project_root / ".amazon-storage-state.json",
            )
        )
        marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.com").strip() or "www.amazon.com"
        headless = _env_flag("AMAZON_HEADLESS", default=False)

        proxy = ProxyConfig(
            server=os.getenv("PROXY_SERVER"),
            username=os.getenv("PROXY_USERNAME"),
            password=os.getenv("PROXY_PASSWORD"),
        )

        delays = DelayConfig(
            min_page_delay=_env_float("AMAZON_MIN_PAGE_DELAY", 3.0),
            max_page_delay=_env_float("AMAZON_MAX_PAGE_DELAY", 8.0),
            max_retries=_env_int("AMAZON_MAX_RETRIES", 3),
        )

        return cls(
            profile_dir=profile_dir,
            storage_state_path=storage_state_path,
            marketplace=marketplace,
            headless=headless,
            proxy=proxy,
            delays=delays,
        )

    def random_viewport(self) -> dict[str, int]:
        """Return a randomized but realistic viewport size."""
        width = random.randint(1280, 1920)
        height = random.randint(720, 1080)
        return {"width": width, "height": height}

    def random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)
