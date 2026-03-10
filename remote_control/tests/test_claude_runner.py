import json
import os
import subprocess
from unittest.mock import Mock, patch

from remote_control.app.claude_runner import (
    build_claude_command,
    collapse_stream_json_output,
    run_prompt,
)


def test_build_claude_command_uses_plugin_dir():
    command = build_claude_command(
        claude_bin="claude",
        repo_dir="/srv/FunnelAgent",
        output_dir="/srv/FunnelAgent/output",
        session_id="11111111-1111-1111-1111-111111111111",
        prompt="Run /funnel-agent:funnel-orchestrator",
    )

    assert "--plugin-dir" in command
    assert "/srv/FunnelAgent" in command
    assert "stream-json" in command
    assert "--verbose" in command


def test_build_claude_command_resumes_existing_session():
    command = build_claude_command(
        claude_bin="claude",
        repo_dir="/srv/FunnelAgent",
        output_dir="/srv/FunnelAgent/output",
        session_id="11111111-1111-1111-1111-111111111111",
        prompt="Continue",
        resume=True,
    )

    assert "--resume" in command
    assert "--session-id" not in command


def test_run_prompt_closes_stdin_for_claude():
    completed = Mock(returncode=0, stdout='{"result":"READY"}', stderr="")

    with patch("remote_control.app.claude_runner.subprocess.run", return_value=completed) as run_mock:
        run_prompt(
            claude_bin="claude",
            repo_dir="/srv/FunnelAgent",
            output_dir="/srv/FunnelAgent/output",
            session_id="11111111-1111-1111-1111-111111111111",
            prompt="Reply with READY",
            resume=False,
        )

    assert run_mock.call_args.kwargs["stdin"] is subprocess.DEVNULL


def test_run_prompt_unsets_anthropic_api_key_for_claude(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    completed = Mock(returncode=0, stdout='{"result":"READY"}', stderr="")

    with patch("remote_control.app.claude_runner.subprocess.run", return_value=completed) as run_mock:
        run_prompt(
            claude_bin="claude",
            repo_dir="/srv/FunnelAgent",
            output_dir="/srv/FunnelAgent/output",
            session_id="11111111-1111-1111-1111-111111111111",
            prompt="Reply with READY",
            resume=False,
        )

    env = run_mock.call_args.kwargs["env"]
    assert "ANTHROPIC_API_KEY" not in env
    assert env.get("PATH") == os.environ.get("PATH")


def test_collapse_stream_json_output_returns_final_result_json():
    stream = "\n".join(
        [
            json.dumps({"type": "system", "subtype": "init"}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "ready"}]}}),
            json.dumps({"type": "result", "result": "ready", "is_error": False}),
        ]
    )

    collapsed = collapse_stream_json_output(stream)

    assert json.loads(collapsed)["result"] == "ready"
