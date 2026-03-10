from pathlib import Path
from types import SimpleNamespace

import pytest

from remote_control.app import discord_bot
from remote_control.app.discord_bot import (
    BackgroundJobResult,
    build_funnel_prompt,
    collect_auto_attachment_paths,
    create_discord_bot,
    execute_background_job,
    extract_response_text,
    normalize_run_prompt,
    save_attachment_to_workspace,
)


def test_normalize_run_prompt_keeps_plain_prompt():
    prompt = normalize_run_prompt(
        "Create a funnel for a sleep supplement",
        repo_dir="/repo",
        output_dir="/repo/output",
    )

    assert "Create a funnel for a sleep supplement" in prompt
    assert "Do not invoke slash-command skills" in prompt


def test_normalize_run_prompt_adds_workspace_context():
    prompt = normalize_run_prompt(
        "Can you tell me about the dermaunder project?",
        repo_dir="/repo",
        output_dir="/repo/output",
    )

    assert "workspace root" in prompt.lower()
    assert "output/" in prompt
    assert "search the workspace" in prompt.lower()
    assert prompt.endswith("Can you tell me about the dermaunder project?")


def test_normalize_run_prompt_includes_uploaded_attachment_paths():
    prompt = normalize_run_prompt(
        "Use the uploaded product image",
        repo_dir="/repo",
        output_dir="/repo/output",
        attachment_paths=[Path("/repo/output/_discord_uploads/session-1/product.png")],
    )

    assert "uploaded file" in prompt.lower()
    assert "/repo/output/_discord_uploads/session-1/product.png" in prompt
    assert "product image" in prompt.lower()


def test_build_funnel_prompt_includes_funnel_skill():
    prompt = build_funnel_prompt("Create a funnel for a sleep supplement")

    assert "/funnel-agent:funnel-orchestrator" in prompt


def test_extract_response_text_reads_json_result():
    payload = '{"result":"hello from claude"}'

    assert extract_response_text(payload) == "hello from claude"


def test_create_discord_bot_does_not_request_message_content_intent(tmp_path):
    app = SimpleNamespace(
        settings=SimpleNamespace(
            discord_application_id="1479563592331296778",
            output_dir=tmp_path,
            claude_bin="claude",
            repo_dir=tmp_path,
        ),
        repository=SimpleNamespace(),
    )

    bot = create_discord_bot(app)

    assert bot.intents.message_content is False


@pytest.mark.asyncio
async def test_execute_background_job_posts_result_to_channel():
    sent_messages = []

    class FakeChannel:
        async def send(self, content, files=None):
            sent_messages.append((content, files))

    async def job():
        return "Session started.\n\nREADY"

    await execute_background_job(FakeChannel(), "<@123>", job)

    assert sent_messages == [("<@123>\nSession started.\n\nREADY", None)]


@pytest.mark.asyncio
async def test_execute_background_job_posts_error_to_channel():
    sent_messages = []

    class FakeChannel:
        async def send(self, content, files=None):
            sent_messages.append((content, files))

    async def job():
        raise RuntimeError("boom")

    await execute_background_job(FakeChannel(), "<@123>", job)

    assert len(sent_messages) == 1
    assert sent_messages[0][0].startswith("<@123>\nAgent error:")
    assert sent_messages[0][1] is None


def test_collect_auto_attachment_paths_filters_and_orders_recent_files(tmp_path):
    run_dir = tmp_path / "demo"
    run_dir.mkdir()
    (run_dir / "older.html").write_text("<html></html>")
    (run_dir / "latest.png").write_bytes(b"png")
    (run_dir / "notes.md").write_text("hello")
    (run_dir / "ignore.bin").write_bytes(b"x")

    repository = SimpleNamespace(
        list_artifacts=lambda session_id: [
            {"relative_path": "older.html", "size_bytes": 100, "modified_at": "10", "kind": "html"},
            {"relative_path": "latest.png", "size_bytes": 200, "modified_at": "30", "kind": "image"},
            {"relative_path": "notes.md", "size_bytes": 150, "modified_at": "20", "kind": "document"},
            {"relative_path": "ignore.bin", "size_bytes": 10, "modified_at": "40", "kind": "other"},
        ]
    )
    session_row = {"id": 1, "run_dir": str(run_dir)}

    paths = collect_auto_attachment_paths(repository, session_row, limit=3)

    assert [path.name for path in paths] == ["latest.png", "notes.md", "older.html"]


@pytest.mark.asyncio
async def test_execute_background_job_posts_result_with_attachments(tmp_path, monkeypatch):
    sent_messages = []
    run_dir = tmp_path / "demo"
    run_dir.mkdir()
    artifact_path = run_dir / "brief.md"
    artifact_path.write_text("summary")

    class FakeChannel:
        async def send(self, content, files=None):
            sent_messages.append((content, files))

    monkeypatch.setattr(discord_bot, "discord", SimpleNamespace(File=lambda path: f"FILE:{Path(path).name}"))

    async def job():
        return BackgroundJobResult(
            message="Finished",
            attachment_paths=[artifact_path],
        )

    await execute_background_job(FakeChannel(), "<@123>", job)

    assert sent_messages == [("<@123>\nFinished", ["FILE:brief.md"])]


@pytest.mark.asyncio
async def test_save_attachment_to_workspace_saves_basename_only(tmp_path):
    class FakeAttachment:
        filename = "../product.png"

        async def save(self, destination):
            Path(destination).write_bytes(b"png")

    saved_path = await save_attachment_to_workspace(FakeAttachment(), tmp_path)

    assert saved_path == tmp_path / "product.png"
    assert saved_path.read_bytes() == b"png"
