"""Tests for agent_runner.py — unit tests with mocked SDK."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from discord_bot.app.agent_runner import AgentBridge, TurnResult

# Check if claude_agent_sdk is available
try:
    from claude_agent_sdk import ClaudeAgentOptions
    HAS_SDK = True
except ModuleNotFoundError:
    HAS_SDK = False


@pytest.fixture
def bridge(tmp_path):
    return AgentBridge(
        repo_dir=tmp_path / "repo",
        output_dir=tmp_path / "output",
        env={"OPENAI_API_KEY": "test"},
    )


def test_bridge_not_connected_by_default(bridge):
    assert bridge.connected is False
    assert bridge.session_id is None


@pytest.mark.skipif(not HAS_SDK, reason="claude-agent-sdk not installed")
def test_build_options(bridge):
    options = bridge._build_options()
    assert options.permission_mode == "bypassPermissions"
    assert "Read" in options.allowed_tools
    assert "Bash" in options.allowed_tools
    assert options.setting_sources == ["project"]


@pytest.mark.asyncio
async def test_run_turn_without_connect_raises(bridge):
    with pytest.raises(RuntimeError, match="not connected"):
        await bridge.run_turn("hello")


def test_turn_result_defaults():
    result = TurnResult()
    assert result.text == ""
    assert result.session_id is None
    assert result.is_question is False
    assert result.is_error is False
    assert result.cost_usd is None
    assert result.tool_progress == []
