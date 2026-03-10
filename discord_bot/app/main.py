"""Entry point for the FunnelAgent Discord bot."""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path

# Remove CLAUDECODE env var so the Agent SDK can spawn CLI subprocesses.
# This var is inherited when the bot is launched from within a Claude Code session.
os.environ.pop("CLAUDECODE", None)

# Remove ANTHROPIC_API_KEY so the SDK uses its own auth (from `claude login`).
# The .env file may contain a stale key that would override working auth.
os.environ.pop("ANTHROPIC_API_KEY", None)

from discord_bot.app.config import Settings
from discord_bot.app.db import init_db
from discord_bot.app.logging_utils import setup_logging
from discord_bot.app.repository import Repository

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover
    load_dotenv = None

logger = logging.getLogger("discord_bot.main")


@dataclass
class App:
    settings: Settings
    repository: Repository


def load_environment() -> None:
    if load_dotenv is None:
        return

    repo_root = Path(__file__).resolve().parents[2]
    # Load in order of precedence (first match wins with python-dotenv):
    # 1. discord_bot/.env (override if exists)
    # 2. remote_control/.env (shared credentials)
    # 3. project root .env
    load_dotenv(repo_root / "discord_bot" / ".env")
    load_dotenv(repo_root / "remote_control" / ".env")
    load_dotenv(repo_root / ".env")


def create_app() -> App:
    load_environment()
    # Remove ANTHROPIC_API_KEY after loading .env so the SDK uses its own
    # auth (from `claude login`) rather than a potentially stale key.
    os.environ.pop("ANTHROPIC_API_KEY", None)
    settings = Settings.from_env()
    setup_logging(settings.log_dir)
    init_db(settings.db_path)
    repository = Repository(settings.db_path)
    return App(settings=settings, repository=repository)


def main() -> None:
    from discord_bot.app.discord_bot import create_discord_bot
    from discord_bot.app.git_updater import pull_on_startup, periodic_pull

    app = create_app()

    bot = create_discord_bot(app)

    original_setup_hook = bot.setup_hook

    async def enhanced_setup_hook():
        await original_setup_hook()

        # Git pull on startup
        if app.settings.git_auto_update:
            result = await pull_on_startup(app.settings.repo_dir)
            logger.info("Startup git pull: %s", result)

            # Start periodic pull background task
            if app.settings.git_update_interval > 0:
                asyncio.create_task(
                    periodic_pull(
                        app.settings.repo_dir,
                        app.settings.git_update_interval,
                    )
                )

    bot.setup_hook = enhanced_setup_hook

    bot.run(app.settings.discord_bot_token)


if __name__ == "__main__":
    main()
