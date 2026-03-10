from dataclasses import dataclass
from pathlib import Path

from remote_control.app.config import Settings
from remote_control.app.db import init_db
from remote_control.app.logging_utils import setup_logging
from remote_control.app.repository import Repository

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional until dependencies are installed
    load_dotenv = None


@dataclass
class App:
    settings: Settings
    repository: Repository


def load_environment() -> None:
    if load_dotenv is None:
        return

    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / "remote_control" / ".env")
    load_dotenv(repo_root / ".env")


def create_app():
    load_environment()
    settings = Settings.from_env()
    setup_logging(settings.log_dir)
    init_db(settings.db_path)
    repository = Repository(settings.db_path)
    return App(settings=settings, repository=repository)


def main() -> None:
    from remote_control.app.discord_bot import create_discord_bot

    app = create_app()
    bot = create_discord_bot(app)
    bot.run(app.settings.discord_bot_token)


if __name__ == "__main__":
    main()
