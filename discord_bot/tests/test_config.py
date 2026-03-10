import os
from pathlib import Path

from discord_bot.app.config import Settings


def test_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_APPLICATION_ID", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("FUNNEL_AGENT_REPO_DIR", raising=False)
    monkeypatch.delenv("GIT_AUTO_UPDATE", raising=False)
    monkeypatch.delenv("GIT_UPDATE_INTERVAL", raising=False)

    settings = Settings.from_env()
    assert settings.discord_bot_token == ""
    assert settings.anthropic_api_key == ""
    assert settings.git_auto_update is True
    assert settings.git_update_interval == 3600
    assert isinstance(settings.repo_dir, Path)
    assert isinstance(settings.output_dir, Path)


def test_from_env_custom_values(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "my-token")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("GIT_AUTO_UPDATE", "false")
    monkeypatch.setenv("GIT_UPDATE_INTERVAL", "1800")
    monkeypatch.setenv("FUNNEL_AGENT_REPO_DIR", "/custom/path")

    settings = Settings.from_env()
    assert settings.discord_bot_token == "my-token"
    assert settings.anthropic_api_key == "sk-ant-test"
    assert settings.git_auto_update is False
    assert settings.git_update_interval == 1800
    assert settings.repo_dir == Path("/custom/path")


def test_agent_env(settings):
    env = settings.agent_env()
    assert env["OPENAI_API_KEY"] == "test-openai-key"
    assert env["GEMINI_API_KEY"] == "test-gemini-key"
    assert "R2_ACCESS_KEY_ID" not in env  # empty string not included


def test_agent_env_with_r2():
    s = Settings(
        discord_bot_token="",
        discord_application_id="",
        discord_public_key="",
        anthropic_api_key="",
        repo_dir=Path("."),
        output_dir=Path("output"),
        db_path=Path("db"),
        log_dir=Path("logs"),
        openai_api_key="",
        gemini_api_key="",
        r2_access_key_id="key-id",
        r2_secret_access_key="secret",
        r2_endpoint_url="https://r2.example.com",
        r2_bucket_name="mybucket",
        r2_public_url="https://cdn.example.com",
        git_auto_update=False,
        git_update_interval=0,
    )
    env = s.agent_env()
    assert env["R2_ACCESS_KEY_ID"] == "key-id"
    assert env["R2_BUCKET_NAME"] == "mybucket"
