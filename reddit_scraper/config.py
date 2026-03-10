from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class RedditScraperConfig:
    client_id: str
    client_secret: str
    user_agent: str

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> "RedditScraperConfig":
        if project_root is None:
            project_root = Path(__file__).resolve().parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
        client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
        user_agent = os.getenv(
            "REDDIT_USER_AGENT", "FunnelAgent/1.0 (research scraper)"
        ).strip()

        config = cls(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        config.validate()
        return config

    def validate(self) -> None:
        missing: list[str] = []
        if not self.client_id:
            missing.append("REDDIT_CLIENT_ID")
        if not self.client_secret:
            missing.append("REDDIT_CLIENT_SECRET")
        if missing:
            print(
                f"Error: missing Reddit credentials: {', '.join(missing)}\n"
                "1. Go to https://www.reddit.com/prefs/apps\n"
                "2. Create a 'script' type application\n"
                "3. Add the credentials to your .env file:\n"
                "   REDDIT_CLIENT_ID=<your-app-id>\n"
                "   REDDIT_CLIENT_SECRET=<your-app-secret>",
                file=sys.stderr,
            )
            sys.exit(1)
