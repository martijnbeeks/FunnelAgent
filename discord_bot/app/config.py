import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    discord_application_id: str
    discord_public_key: str
    anthropic_api_key: str
    repo_dir: Path
    output_dir: Path
    db_path: Path
    log_dir: Path
    openai_api_key: str
    gemini_api_key: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_endpoint_url: str
    r2_bucket_name: str
    r2_public_url: str
    git_auto_update: bool
    git_update_interval: int

    @classmethod
    def from_env(cls) -> "Settings":
        cwd = Path.cwd()
        return cls(
            discord_bot_token=os.environ.get("DISCORD_BOT_TOKEN", ""),
            discord_application_id=os.environ.get("DISCORD_APPLICATION_ID", ""),
            discord_public_key=os.environ.get("DISCORD_PUBLIC_KEY", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            repo_dir=Path(os.environ.get("FUNNEL_AGENT_REPO_DIR", cwd)),
            output_dir=Path(
                os.environ.get("FUNNEL_AGENT_OUTPUT_DIR", cwd / "output")
            ),
            db_path=Path(
                os.environ.get(
                    "FUNNEL_AGENT_DB_PATH",
                    cwd / "discord_bot" / "data" / "bot.db",
                )
            ),
            log_dir=Path(
                os.environ.get(
                    "FUNNEL_AGENT_LOG_DIR",
                    cwd / "discord_bot" / "logs",
                )
            ),
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
            r2_access_key_id=os.environ.get("R2_ACCESS_KEY_ID", ""),
            r2_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
            r2_endpoint_url=os.environ.get("R2_ENDPOINT_URL", ""),
            r2_bucket_name=os.environ.get("R2_BUCKET_NAME", ""),
            r2_public_url=os.environ.get("R2_PUBLIC_URL", ""),
            git_auto_update=os.environ.get("GIT_AUTO_UPDATE", "true").lower()
            in ("true", "1", "yes"),
            git_update_interval=int(
                os.environ.get("GIT_UPDATE_INTERVAL", "3600")
            ),
        )

    def agent_env(self) -> dict[str, str]:
        """Environment variables to pass through to the Claude Agent SDK."""
        env: dict[str, str] = {}
        if self.anthropic_api_key:
            env["ANTHROPIC_API_KEY"] = self.anthropic_api_key
        if self.openai_api_key:
            env["OPENAI_API_KEY"] = self.openai_api_key
        if self.gemini_api_key:
            env["GEMINI_API_KEY"] = self.gemini_api_key
        if self.r2_access_key_id:
            env["R2_ACCESS_KEY_ID"] = self.r2_access_key_id
        if self.r2_secret_access_key:
            env["R2_SECRET_ACCESS_KEY"] = self.r2_secret_access_key
        if self.r2_endpoint_url:
            env["R2_ENDPOINT_URL"] = self.r2_endpoint_url
        if self.r2_bucket_name:
            env["R2_BUCKET_NAME"] = self.r2_bucket_name
        if self.r2_public_url:
            env["R2_PUBLIC_URL"] = self.r2_public_url
        return env
