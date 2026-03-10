import logging
from pathlib import Path


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    bot_file_handler = logging.FileHandler(
        log_dir / "bot.log", encoding="utf-8"
    )
    bot_file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[stream_handler, bot_file_handler],
        force=True,
    )

    claude_logger = logging.getLogger("discord_bot.claude_raw")
    claude_logger.handlers.clear()
    claude_logger.setLevel(logging.INFO)
    claude_logger.propagate = False

    claude_file_handler = logging.FileHandler(
        log_dir / "claude.log", encoding="utf-8"
    )
    claude_file_handler.setFormatter(formatter)
    claude_logger.addHandler(claude_file_handler)
