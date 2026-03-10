"""Tests for discord_bot.py helper functions (no Discord dependency needed)."""

from pathlib import Path

from discord_bot.app.discord_bot import (
    normalize_run_prompt,
    build_funnel_prompt,
    trim_for_discord,
    get_channel_context,
    discover_run_dir,
    FUNNEL_PREFIX,
)


def test_normalize_run_prompt_basic():
    result = normalize_run_prompt("Hello", "/repo", "/output")
    assert "Hello" in result
    assert "/repo" in result
    assert "/output" in result


def test_normalize_run_prompt_empty():
    result = normalize_run_prompt("", "/repo", "/output")
    assert "/repo" in result
    assert "User request:" not in result


def test_normalize_run_prompt_with_attachments():
    result = normalize_run_prompt(
        "Check this",
        "/repo",
        "/output",
        attachment_paths=[Path("/output/uploads/photo.png")],
    )
    assert "photo.png" in result
    assert "uploaded file" in result.lower()


def test_build_funnel_prompt_basic():
    result = build_funnel_prompt("My product URL")
    assert FUNNEL_PREFIX in result
    assert "My product URL" in result


def test_build_funnel_prompt_already_has_prefix():
    original = f"Something {FUNNEL_PREFIX} else"
    # Should not prepend if already contains it
    result = build_funnel_prompt(original)
    assert result == original.strip()


def test_build_funnel_prompt_empty():
    result = build_funnel_prompt("")
    assert result == FUNNEL_PREFIX


def test_trim_for_discord_short():
    assert trim_for_discord("hello") == "hello"


def test_trim_for_discord_long():
    long_text = "x" * 2000
    result = trim_for_discord(long_text, limit=100)
    assert len(result) == 100
    assert result.endswith("...")


def test_trim_for_discord_exact():
    text = "x" * 1900
    result = trim_for_discord(text)
    assert result == text


class FakeChannel:
    def __init__(self, id, parent=None):
        self.id = id
        self.parent = parent


def test_get_channel_context_no_thread():
    channel = FakeChannel(id=12345)
    channel_id, thread_id = get_channel_context(channel)
    assert channel_id == "12345"
    assert thread_id is None


def test_get_channel_context_with_thread():
    parent = FakeChannel(id=11111)
    thread = FakeChannel(id=22222, parent=parent)
    channel_id, thread_id = get_channel_context(thread)
    assert channel_id == "11111"
    assert thread_id == "22222"


def test_discover_run_dir_empty(tmp_path):
    result = discover_run_dir(tmp_path)
    assert result is None


def test_discover_run_dir_nonexistent(tmp_path):
    result = discover_run_dir(tmp_path / "nonexistent")
    assert result is None


def test_discover_run_dir_with_dirs(tmp_path):
    (tmp_path / "project_a").mkdir()
    (tmp_path / "project_b").mkdir()
    # Touch project_b to make it newest
    (tmp_path / "project_b" / "marker").write_text("x")

    result = discover_run_dir(tmp_path)
    assert result is not None
    name, path = result
    assert name == "project_b"
    assert path == tmp_path / "project_b"
