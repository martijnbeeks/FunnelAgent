from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import subprocess

logger = logging.getLogger("remote_control.claude")
raw_logger = logging.getLogger("remote_control.claude_raw")


@dataclass(frozen=True)
class ClaudeRunResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int


def build_claude_command(
    claude_bin: str,
    repo_dir: str | Path,
    output_dir: str | Path,
    session_id: str,
    prompt: str,
    resume: bool = False,
) -> list[str]:
    command = [
        str(claude_bin),
        "-p",
        "--verbose",
        "--output-format",
        "stream-json",
        "--permission-mode",
        "bypassPermissions",
        "--plugin-dir",
        str(repo_dir),
        "--add-dir",
        str(repo_dir),
        "--add-dir",
        str(output_dir),
    ]
    if resume:
        command.extend(["--resume", session_id])
    else:
        command.extend(["--session-id", session_id])
    command.append(prompt)
    return command


def collapse_stream_json_output(output: str) -> str:
    result_event = None
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            result_event = event
    if result_event is not None:
        return json.dumps(result_event)
    return output


def run_prompt(
    claude_bin: str,
    repo_dir: str | Path,
    output_dir: str | Path,
    session_id: str,
    prompt: str,
    resume: bool = False,
) -> ClaudeRunResult:
    command = build_claude_command(
        claude_bin=claude_bin,
        repo_dir=repo_dir,
        output_dir=output_dir,
        session_id=session_id,
        prompt=prompt,
        resume=resume,
    )
    logger.info(
        "Starting Claude prompt for session %s with plugin dir %s",
        session_id,
        repo_dir,
    )
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    logger.info(
        "Claude prompt finished for session %s with return code %s",
        session_id,
        completed.returncode,
    )
    normalized_stdout = collapse_stream_json_output(completed.stdout)
    if completed.stdout.strip():
        raw_logger.info("session=%s stdout=%s", session_id, completed.stdout.strip())
    if completed.stderr.strip():
        raw_logger.info("session=%s stderr=%s", session_id, completed.stderr.strip())
    return ClaudeRunResult(
        ok=completed.returncode == 0,
        stdout=normalized_stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )
