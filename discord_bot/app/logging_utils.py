import logging
from pathlib import Path


def setup_logging(log_dir: Path) -> None:
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    handlers: list[logging.Handler] = []

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    handlers.append(stream_handler)

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        bot_file_handler = logging.FileHandler(
            log_dir / "bot.log", encoding="utf-8"
        )
        bot_file_handler.setFormatter(formatter)
        handlers.append(bot_file_handler)
    except (PermissionError, OSError):
        pass  # Fall back to stderr only (e.g. in Docker)

    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        force=True,
    )

    claude_logger = logging.getLogger("discord_bot.claude_raw")
    claude_logger.handlers.clear()
    claude_logger.setLevel(logging.INFO)
    claude_logger.propagate = False

    try:
        claude_file_handler = logging.FileHandler(
            log_dir / "claude.log", encoding="utf-8"
        )
        claude_file_handler.setFormatter(formatter)
        claude_logger.addHandler(claude_file_handler)
    except (PermissionError, OSError):
        claude_logger.addHandler(stream_handler)  # Fall back to stderr
