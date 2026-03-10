from pathlib import Path

from remote_control.app.config import Settings


def test_settings_reads_expected_values(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("FUNNEL_AGENT_REPO_DIR", "/srv/FunnelAgent")
    monkeypatch.setenv("FUNNEL_AGENT_OUTPUT_DIR", "/srv/FunnelAgent/output")
    monkeypatch.setenv(
        "FUNNEL_AGENT_DB_PATH",
        "/srv/FunnelAgent/remote_control/data/control.db",
    )
    monkeypatch.setenv("CLAUDE_BIN", "/usr/local/bin/claude")

    settings = Settings.from_env()

    assert settings.repo_dir == Path("/srv/FunnelAgent")

