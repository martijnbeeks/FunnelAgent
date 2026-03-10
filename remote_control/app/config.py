import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    discord_application_id: str
    discord_public_key: str
    repo_dir: Path
    output_dir: Path
    db_path: Path
    log_dir: Path
    claude_bin: str

    @classmethod
    def from_env(cls) -> "Settings":
        cwd = Path.cwd()
        return cls(
            discord_bot_token=os.environ.get("DISCORD_BOT_TOKEN", ""),
            discord_application_id=os.environ.get("DISCORD_APPLICATION_ID", ""),
            discord_public_key=os.environ.get("DISCORD_PUBLIC_KEY", ""),
            repo_dir=Path(os.environ.get("FUNNEL_AGENT_REPO_DIR", cwd)),
            output_dir=Path(
                os.environ.get("FUNNEL_AGENT_OUTPUT_DIR", cwd / "output")
            ),
            db_path=Path(
                os.environ.get(
                    "FUNNEL_AGENT_DB_PATH",
                    cwd / "remote_control" / "data" / "control.db",
                )
            ),
            log_dir=Path(
                os.environ.get(
                    "FUNNEL_AGENT_LOG_DIR",
                    cwd / "remote_control" / "logs",
                )
            ),
            claude_bin=os.environ.get("CLAUDE_BIN", "claude"),
        )
