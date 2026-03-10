# FunnelAgent Discord Remote Control Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy FunnelAgent on a single server and control it from Discord while preserving the repo's existing Claude skills and storing run history and outputs in a simple backend.

**Architecture:** Run one small Python Discord bot on the server. The bot invokes the local `claude` CLI with `--plugin-dir` pointed at this repository so the existing `.claude-plugin` metadata and `skills/` folder remain the execution source of truth. Persist session metadata and message history in SQLite, and keep generated funnel artifacts in the existing `output/` directory with a DB index for retrieval. For operator access, also run an official Claude Code Remote Control session on the same server so the agent can be monitored or taken over from `claude.ai/code` or the Claude mobile app.

**Tech Stack:** Python 3.11+, `discord.py`, `pytest`, built-in `sqlite3`, existing `claude` CLI, official Claude Code Remote Control, existing repo `skills/`, existing `scripts/`, systemd plus `tmux` on a single Linux VM.

## Recommended Approach

Use the simplest deployable shape:

- One Ubuntu VM
- One long-running Python bot process
- One optional `tmux`-hosted `claude remote-control` admin session
- One SQLite database file
- One filesystem artifact store (`output/`)
- One Claude Code CLI integration

Do not add:

- Docker for v1
- Redis
- Postgres
- FastAPI
- job queues
- web dashboard

The Discord bot is the automation surface. Claude Code remains the agent runtime. The repo remains the skill/plugin source. Official Remote Control is the operator/admin surface, not the Discord integration layer.

## Operational Flow

1. A Discord slash command starts or continues a run in a channel or thread.
2. The bot looks up the active Claude session UUID for that Discord thread.
3. The bot invokes:

```bash
claude -p \
  --output-format json \
  --permission-mode bypassPermissions \
  --plugin-dir /srv/FunnelAgent \
  --add-dir /srv/FunnelAgent \
  --add-dir /srv/FunnelAgent/output \
  --session-id <uuid> \
  "<user message>"
```

4. Claude executes inside this repo, with access to the existing plugin and `skills/`.
5. FunnelAgent writes outputs into `output/<run-name>/` as it already does.
6. The bot stores the Discord message, Claude response, run state, and artifact index in SQLite.
7. Discord users can request status, latest response, or artifact files from the same channel.

## Official Remote Control Usage

Use Anthropic's official Remote Control on the server for human supervision and recovery, not for Discord transport.

- Start it from the repo directory:

```bash
cd /srv/FunnelAgent
claude remote-control "FunnelAgent Admin"
```

- Keep it running inside `tmux` so the process stays alive.
- Use this session from `claude.ai/code` or the Claude mobile app to:
  - inspect the live server session
  - continue work manually if the Discord bot needs intervention
  - verify the server environment has access to the repo, tools, and output files

Important constraints from the official docs:

- Remote Control requires a supported Claude subscription plan; API keys are not enough.
- Remote Control uses Claude account login via `/login`; API keys are not supported for this feature.
- The Claude process must remain open or the remote session ends.
- Each Claude Code instance supports one remote session at a time.
- Remote Control is off by default unless you start it explicitly or enable it in `/config`.
- If `claude remote-control` is unavailable on the server, update Claude Code before relying on this part of the design.

## Data Model

Use one SQLite database: `remote_control/data/control.db`

Tables:

- `sessions`
  - `id`
  - `discord_guild_id`
  - `discord_channel_id`
  - `discord_thread_id`
  - `claude_session_id`
  - `run_name`
  - `run_dir`
  - `status`
  - `created_at`
  - `updated_at`
- `messages`
  - `id`
  - `session_id`
  - `source` (`discord` or `claude`)
  - `discord_message_id`
  - `content`
  - `created_at`
- `artifacts`
  - `id`
  - `session_id`
  - `relative_path`
  - `size_bytes`
  - `modified_at`
  - `kind`

Do not store generated HTML, images, or research blobs in SQLite. Store those on disk and index them.

## Discord Command Surface

Keep commands narrow:

- `/agent-start prompt:<text>`
  - Starts a new Claude session for the current channel or thread.
- `/agent-send message:<text>`
  - Sends a follow-up message into the active Claude session.
- `/agent-status`
  - Returns session UUID, current run name, last updated time, and latest artifacts.
- `/agent-files`
  - Lists indexed files for the active run.
- `/agent-get path:<relative-path>`
  - Uploads a requested artifact back into Discord.
- `/agent-stop`
  - Marks the session inactive in SQLite.

For FunnelAgent runs, the initial prompt should explicitly invoke the repo skill:

```text
Run /funnel-agent:funnel-orchestrator and continue the workflow in this session.
```

## Files To Create

### Task 1: Create the remote control scaffold

**Files:**
- Create: `remote_control/requirements.txt`
- Create: `remote_control/.env.example`
- Create: `remote_control/app/__init__.py`
- Create: `remote_control/app/main.py`
- Create: `remote_control/tests/test_smoke.py`

**Step 1: Write the failing smoke test**

```python
from remote_control.app.main import create_app


def test_create_app():
    app = create_app()
    assert app is not None
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest remote_control/tests/test_smoke.py -v`
Expected: FAIL with import error because the package does not exist yet.

**Step 3: Write minimal implementation**

- Add dependencies to `remote_control/requirements.txt`:
  - `discord.py`
  - `pytest`
  - `python-dotenv`
- Add `create_app()` in `remote_control/app/main.py`.

```python
class App:
    pass


def create_app():
    return App()
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest remote_control/tests/test_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add remote_control
git commit -m "feat: scaffold discord remote control service"
```

### Task 2: Add configuration and SQLite persistence

**Files:**
- Create: `remote_control/app/config.py`
- Create: `remote_control/app/db.py`
- Create: `remote_control/tests/test_config.py`
- Create: `remote_control/tests/test_db.py`
- Modify: `remote_control/.env.example`
- Modify: `remote_control/app/main.py`

**Step 1: Write the failing tests**

```python
from pathlib import Path

from remote_control.app.config import Settings
from remote_control.app.db import init_db


def test_settings_reads_expected_values(tmp_path, monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("FUNNEL_AGENT_REPO_DIR", "/srv/FunnelAgent")
    settings = Settings.from_env()
    assert settings.repo_dir == Path("/srv/FunnelAgent")


def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "control.db"
    init_db(db_path)
    assert db_path.exists()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest remote_control/tests/test_config.py remote_control/tests/test_db.py -v`
Expected: FAIL because `Settings` and `init_db` do not exist.

**Step 3: Write minimal implementation**

- `config.py` should load:
  - `DISCORD_BOT_TOKEN`
  - `FUNNEL_AGENT_REPO_DIR`
  - `FUNNEL_AGENT_OUTPUT_DIR`
  - `FUNNEL_AGENT_DB_PATH`
  - `CLAUDE_BIN`
- `db.py` should create the `sessions`, `messages`, and `artifacts` tables with plain SQL using `sqlite3`.
- Update `main.py` so `create_app()` loads settings and initializes the DB on startup.

```python
import sqlite3


SCHEMA = """
create table if not exists sessions (...);
create table if not exists messages (...);
create table if not exists artifacts (...);
"""


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.close()
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest remote_control/tests/test_config.py remote_control/tests/test_db.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add remote_control
git commit -m "feat: add remote control config and sqlite storage"
```

### Task 3: Implement the Claude CLI runner with persistent session IDs

**Files:**
- Create: `remote_control/app/claude_runner.py`
- Create: `remote_control/tests/test_claude_runner.py`
- Modify: `remote_control/app/config.py`

**Step 1: Write the failing test**

```python
from remote_control.app.claude_runner import build_claude_command


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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest remote_control/tests/test_claude_runner.py -v`
Expected: FAIL because `build_claude_command` does not exist.

**Step 3: Write minimal implementation**

- Build the command as a list, not a shell string.
- Use caller-generated UUIDs for session continuity instead of parsing IDs from Claude output.
- Add `run_prompt()` which executes the command with `subprocess.run(..., capture_output=True, text=True, check=False)`.
- Return a small result object:
  - `ok`
  - `stdout`
  - `stderr`
  - `returncode`

```python
def build_claude_command(...):
    return [
        claude_bin,
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "bypassPermissions",
        "--plugin-dir",
        str(repo_dir),
        "--add-dir",
        str(repo_dir),
        "--add-dir",
        str(output_dir),
        "--session-id",
        session_id,
        prompt,
    ]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest remote_control/tests/test_claude_runner.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add remote_control
git commit -m "feat: add claude cli runner for discord control"
```

### Task 4: Implement session repository and artifact indexing

**Files:**
- Create: `remote_control/app/repository.py`
- Create: `remote_control/app/artifacts.py`
- Create: `remote_control/tests/test_repository.py`
- Create: `remote_control/tests/test_artifacts.py`

**Step 1: Write the failing tests**

```python
from pathlib import Path

from remote_control.app.artifacts import scan_artifacts


def test_scan_artifacts_finds_html_and_images(tmp_path):
    run_dir = tmp_path / "demo"
    run_dir.mkdir()
    (run_dir / "advertorial.html").write_text("<html></html>")
    (run_dir / "logo.png").write_bytes(b"png")
    artifacts = scan_artifacts(run_dir)
    assert {item.kind for item in artifacts} == {"html", "image"}
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest remote_control/tests/test_repository.py remote_control/tests/test_artifacts.py -v`
Expected: FAIL because the repository and scanner modules do not exist.

**Step 3: Write minimal implementation**

- `repository.py`
  - create session
  - get active session for a Discord thread/channel
  - append message
  - replace artifact index for a session
- `artifacts.py`
  - recursively scan a run directory
  - classify file kinds:
    - `.html` -> `html`
    - `.png`, `.jpg`, `.jpeg`, `.webp` -> `image`
    - `.md`, `.js`, `.json`, `.txt` -> `document`
    - fallback -> `other`

```python
def scan_artifacts(run_dir):
    items = []
    for path in run_dir.rglob("*"):
        if path.is_file():
            items.append(...)
    return items
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest remote_control/tests/test_repository.py remote_control/tests/test_artifacts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add remote_control
git commit -m "feat: track sessions and generated artifacts"
```

### Task 5: Add Discord slash commands and message loop

**Files:**
- Create: `remote_control/app/discord_bot.py`
- Create: `remote_control/tests/test_discord_bot.py`
- Modify: `remote_control/app/main.py`
- Modify: `remote_control/app/repository.py`

**Step 1: Write the failing tests**

```python
from remote_control.app.discord_bot import normalize_run_prompt


def test_normalize_run_prompt_includes_funnel_skill():
    prompt = normalize_run_prompt("Create a funnel for a sleep supplement")
    assert "/funnel-agent:funnel-orchestrator" in prompt
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest remote_control/tests/test_discord_bot.py -v`
Expected: FAIL because the Discord bot module does not exist.

**Step 3: Write minimal implementation**

- Register these slash commands:
  - `/agent-start`
  - `/agent-send`
  - `/agent-status`
  - `/agent-files`
  - `/agent-get`
  - `/agent-stop`
- Use the Discord thread ID when available; otherwise use channel ID as the session key.
- On `/agent-start`:
  - generate a UUID
  - create a session row
  - call Claude with a normalized prompt that prepends:

```text
Run /funnel-agent:funnel-orchestrator and continue the workflow in this session.
```

- On `/agent-send`:
  - fetch the active session
  - call Claude again with the same session UUID
- After each Claude response:
  - store the Claude message
  - rescan the run directory if known
  - send the summarized response back to Discord

**Step 4: Run tests to verify they pass**

Run: `python -m pytest remote_control/tests/test_discord_bot.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add remote_control
git commit -m "feat: add discord commands for remote claude control"
```

### Task 6: Add deployment assets and ops documentation

**Files:**
- Create: `deploy/systemd/funnelagent-discord.service`
- Create: `deploy/tmux/start-remote-control.sh`
- Create: `docs/discord-remote-control.md`
- Modify: `README.md`

**Step 1: Write the failing verification step**

Run: `test -f deploy/systemd/funnelagent-discord.service && test -f deploy/tmux/start-remote-control.sh && test -f docs/discord-remote-control.md`
Expected: FAIL because the deployment files do not exist.

**Step 2: Create the deployment artifacts**

- `deploy/systemd/funnelagent-discord.service`
  - `WorkingDirectory=/srv/FunnelAgent`
  - `ExecStart=/usr/bin/python3 -m remote_control.app.main`
  - `EnvironmentFile=/srv/FunnelAgent/remote_control/.env`
  - `Restart=always`
- `deploy/tmux/start-remote-control.sh`
  - starts `claude remote-control "FunnelAgent Admin"` inside a named `tmux` session
  - prints a warning if the local Claude build does not expose `remote-control`
- `docs/discord-remote-control.md`
  - server prerequisites
  - Claude auth setup
  - Discord app setup
  - systemd install
  - `tmux` admin remote-control startup
  - log inspection
  - rollback and restart steps
- `README.md`
  - add a short section linking to the Discord remote control flow

**Step 3: Add minimal systemd unit**

```ini
[Unit]
Description=FunnelAgent Discord Remote Control
After=network.target

[Service]
WorkingDirectory=/srv/FunnelAgent
EnvironmentFile=/srv/FunnelAgent/remote_control/.env
ExecStart=/usr/bin/python3 -m remote_control.app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /srv/FunnelAgent
tmux new-session -d -s funnelagent-rc 'claude remote-control "FunnelAgent Admin"'
tmux attach -t funnelagent-rc
```

**Step 4: Run verification**

Run: `test -f deploy/systemd/funnelagent-discord.service && test -f deploy/tmux/start-remote-control.sh && test -f docs/discord-remote-control.md && rg -n "Discord remote control" README.md`
Expected: PASS

**Step 5: Commit**

```bash
git add deploy docs README.md
git commit -m "docs: add discord remote deployment guide"
```

## Manual Verification Checklist

Run these commands on the target server after implementation:

```bash
cd /srv/FunnelAgent
python3 -m venv .venv
. .venv/bin/activate
pip install -r scripts/requirements.txt
pip install -r remote_control/requirements.txt
claude setup-token
python -m pytest remote_control/tests -v
python -m remote_control.app.main
tmux new-session -d -s funnelagent-rc 'cd /srv/FunnelAgent && claude remote-control "FunnelAgent Admin"'
```

Expected checks:

- Bot logs in to Discord successfully
- `/agent-start` creates a SQLite session row
- Claude runs with `--plugin-dir /srv/FunnelAgent`
- The prompt can invoke `/funnel-agent:funnel-orchestrator`
- Generated files appear in `output/<run-name>/`
- `/agent-files` lists those files
- `/agent-get` uploads a selected artifact back to Discord
- The admin Remote Control session is visible from `claude.ai/code`

## Deployment Steps

1. Provision one Linux VM.
2. Install Python 3.11+, Node.js, and Claude Code CLI.
3. Clone this repository to `/srv/FunnelAgent`.
4. Run `claude` once in `/srv/FunnelAgent`, use `/login`, and accept workspace trust.
5. If `claude remote-control` is missing, update Claude Code before continuing.
6. Authenticate any non-Remote-Control automation path as needed with `claude setup-token`.
7. Create `remote_control/.env` with:
   - `DISCORD_BOT_TOKEN`
   - `FUNNEL_AGENT_REPO_DIR=/srv/FunnelAgent`
   - `FUNNEL_AGENT_OUTPUT_DIR=/srv/FunnelAgent/output`
   - `FUNNEL_AGENT_DB_PATH=/srv/FunnelAgent/remote_control/data/control.db`
   - `CLAUDE_BIN=/usr/local/bin/claude` or the actual path
8. Install the systemd unit and start the Discord bot service.
9. Start the admin Remote Control session in `tmux`.
10. Create a private Discord channel for bot control.
11. Test one end-to-end run before adding more channels or users.

## Open Questions To Confirm Before Implementation

1. Discord model: one shared channel or one thread per funnel run?
2. Backend definition: is SQLite + filesystem acceptable for v1, or do you want managed storage from day one?
3. Artifact retention: keep everything indefinitely, or auto-expire old runs?
4. Should the admin Remote Control session be restricted to you only, or shared with a small operator group?

## Why This Is The KISS Option

- It reuses the current repo exactly as the Claude skill/plugin source.
- It avoids rebuilding FunnelAgent as a second application.
- It avoids introducing extra infrastructure before usage proves the need.
- It keeps deployment understandable by one person on one machine.
- It leaves a clean upgrade path to Postgres, S3, or a web UI later without changing the core agent execution model.
