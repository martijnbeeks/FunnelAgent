"""Discord bot with slash commands and streaming Claude Agent SDK integration."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from discord_bot.app.agent_runner import AgentBridge, TurnResult
from discord_bot.app.artifacts import scan_artifacts, diff_artifacts, ArtifactRecord
from discord_bot.app.stream_buffer import StreamBuffer

try:
    import discord
    from discord import app_commands
except ModuleNotFoundError:  # pragma: no cover
    discord = None
    app_commands = None


FUNNEL_PREFIX = (
    "Run /funnel-agent:funnel-orchestrator and continue the workflow in this session."
)
AUTO_ATTACH_KINDS = {"document", "html", "image"}
MAX_AUTO_ATTACHMENTS = 8
MAX_AUTO_ATTACH_SIZE_BYTES = 8 * 1024 * 1024

logger = logging.getLogger("discord_bot.discord_bot")


# --- Active session tracking ---
# Maps (channel_id, thread_id) to running session state
_active_bridges: dict[tuple[str, str | None], AgentBridge] = {}
_previous_artifacts: dict[int, list[ArtifactRecord]] = {}


# --- Helper functions ---


def normalize_run_prompt(
    prompt: str,
    repo_dir: str | Path,
    output_dir: str | Path,
    attachment_paths: list[Path] | None = None,
) -> str:
    stripped = prompt.strip()
    guidance = (
        f"You are operating inside the local workspace root at {repo_dir}. "
        f"The output directory {output_dir} is also available, including project folders under output/. "
        "If the user mentions a project or folder name, search the workspace before saying it is unavailable. "
        "Do not invoke slash-command skills unless the user explicitly asks for them."
    )
    if attachment_paths:
        joined_paths = "\n".join(f"- {path}" for path in attachment_paths)
        guidance = (
            f"{guidance} "
            "The user also uploaded file(s) into the workspace. Use them when relevant, "
            "especially if the request mentions a product image or reference image.\n"
            f"Uploaded file paths:\n{joined_paths}"
        )
    if not stripped:
        return guidance
    return f"{guidance}\n\nUser request:\n{stripped}"


def build_funnel_prompt(prompt: str) -> str:
    stripped = prompt.strip()
    if "/funnel-agent:funnel-orchestrator" in stripped:
        return stripped
    if not stripped:
        return FUNNEL_PREFIX
    return f"{FUNNEL_PREFIX}\n\n{stripped}"


def trim_for_discord(text: str, limit: int = 1900) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3]}..."


def get_channel_context(channel: Any) -> tuple[str, str | None]:
    parent = getattr(channel, "parent", None)
    thread_id = str(channel.id) if parent is not None else None
    channel_id = str(parent.id) if parent is not None else str(channel.id)
    return channel_id, thread_id


def discover_run_dir(output_dir: Path) -> tuple[str, Path] | None:
    if not output_dir.exists():
        return None
    directories = [path for path in output_dir.iterdir() if path.is_dir()]
    if not directories:
        return None
    latest = max(directories, key=lambda item: item.stat().st_mtime)
    return latest.name, latest


def collect_auto_attachment_paths(
    repository: Any,
    session_row: Any,
    limit: int = MAX_AUTO_ATTACHMENTS,
) -> list[Path]:
    run_dir = session_row["run_dir"]
    if not run_dir:
        return []

    ranked_artifacts = sorted(
        repository.list_artifacts(session_row["id"]),
        key=lambda item: (int(item["modified_at"]), item["relative_path"]),
        reverse=True,
    )

    attachment_paths = []
    base_dir = Path(run_dir)
    for artifact in ranked_artifacts:
        if artifact["kind"] not in AUTO_ATTACH_KINDS:
            continue
        if int(artifact["size_bytes"]) > MAX_AUTO_ATTACH_SIZE_BYTES:
            continue
        file_path = base_dir / artifact["relative_path"]
        if not file_path.exists() or not file_path.is_file():
            continue
        attachment_paths.append(file_path)
        if len(attachment_paths) >= limit:
            break
    return attachment_paths


def collect_new_attachment_paths(
    session_id: int,
    run_dir: Path,
    limit: int = MAX_AUTO_ATTACHMENTS,
) -> list[Path]:
    """Collect only files that are new or modified since the last scan."""
    current = scan_artifacts(run_dir)
    previous = _previous_artifacts.get(session_id, [])
    _previous_artifacts[session_id] = current

    new_artifacts = diff_artifacts(previous, current)
    # Sort by modification time, newest first
    new_artifacts.sort(key=lambda a: int(a.modified_at), reverse=True)

    paths = []
    for artifact in new_artifacts:
        if artifact.kind not in AUTO_ATTACH_KINDS:
            continue
        if artifact.size_bytes > MAX_AUTO_ATTACH_SIZE_BYTES:
            continue
        file_path = run_dir / artifact.relative_path
        if file_path.exists() and file_path.is_file():
            paths.append(file_path)
        if len(paths) >= limit:
            break
    return paths


async def save_attachment_to_workspace(
    attachment: Any, destination_dir: Path
) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = (
        Path(getattr(attachment, "filename", "upload.bin")).name or "upload.bin"
    )
    destination = destination_dir / filename
    suffix = destination.suffix
    stem = destination.stem
    counter = 1
    while destination.exists():
        destination = destination_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    await attachment.save(destination)
    return destination


# --- Bot factory ---


def create_discord_bot(app: Any):
    if discord is None or app_commands is None:
        raise RuntimeError(
            "discord.py is not installed. Install discord_bot/requirements.txt first."
        )

    intents = discord.Intents.default()
    intents.message_content = True
    application_id = (
        int(app.settings.discord_application_id)
        if getattr(app.settings, "discord_application_id", "")
        else None
    )

    class SlashClient(discord.Client):
        def __init__(self):
            super().__init__(intents=intents, application_id=application_id)
            self.tree = app_commands.CommandTree(self)

        async def setup_hook(self):
            await self.tree.sync()

    bot = SlashClient()

    # --- Session management helpers ---

    def _get_bridge_key(channel: Any) -> tuple[str, str | None]:
        return get_channel_context(channel)

    def _get_bridge(channel: Any) -> AgentBridge | None:
        return _active_bridges.get(_get_bridge_key(channel))

    def _set_bridge(channel: Any, bridge: AgentBridge) -> None:
        _active_bridges[_get_bridge_key(channel)] = bridge

    def _remove_bridge(channel: Any) -> AgentBridge | None:
        return _active_bridges.pop(_get_bridge_key(channel), None)

    # --- Core session handlers ---

    async def run_agent_turn(
        channel: Any,
        session_row: Any,
        bridge: AgentBridge,
        prompt: str,
        user_mention: str,
    ) -> None:
        """Run a single agent turn with streaming to Discord."""
        session_id = session_row["id"]

        async def send_to_channel(text: str) -> None:
            await channel.send(trim_for_discord(text))

        buffer = StreamBuffer(send_to_channel)

        async def on_text(text: str) -> None:
            await buffer.append(text)

        async def on_progress(line: str) -> None:
            await buffer.append_line(f"> {line}")

        try:
            app.repository.update_session_status(session_id, "active")

            result = await bridge.run_turn(
                prompt=prompt,
                on_text=on_text,
                on_progress=on_progress,
            )

            await buffer.flush()

            # Update session with SDK session ID
            if result.session_id and not session_row["claude_session_id"]:
                app.repository.update_session_claude_id(
                    session_id, result.session_id
                )

            # Discover and update run directory
            discovered = discover_run_dir(app.settings.output_dir)
            if discovered is not None:
                run_name, run_dir = discovered
                app.repository.update_session_run(
                    session_id, run_name=run_name, run_dir=str(run_dir)
                )
                # Scan and save artifacts
                current_artifacts = scan_artifacts(run_dir)
                app.repository.replace_artifacts(session_id, current_artifacts)

                # Auto-attach new files
                new_paths = collect_new_attachment_paths(
                    session_id, run_dir
                )
                if new_paths:
                    files = [discord.File(p) for p in new_paths]
                    try:
                        await channel.send(
                            f"{user_mention} New files generated:",
                            files=files,
                        )
                    except Exception:
                        logger.exception("Failed to send artifact attachments")

            # Update session status
            if result.is_question:
                app.repository.update_session_status(
                    session_id, "waiting_input"
                )
            elif result.is_error:
                app.repository.update_session_status(session_id, "error")
            else:
                # Keep active — the pipeline may have more steps
                app.repository.update_session_status(session_id, "active")

            if result.cost_usd is not None:
                logger.info(
                    "Turn cost: $%.4f, duration: %dms",
                    result.cost_usd,
                    result.duration_ms,
                )

        except Exception as exc:
            logger.exception("Agent turn failed")
            await buffer.flush()
            await channel.send(
                trim_for_discord(f"{user_mention} Agent error:\n{exc}")
            )
            app.repository.update_session_status(session_id, "error")

    async def handle_start(
        channel: Any,
        guild_id: str | None,
        prompt: str,
        user_mention: str,
        is_funnel: bool = False,
        attachment: Any | None = None,
    ) -> None:
        channel_id, thread_id = get_channel_context(channel)

        # Stop existing session if any
        existing = app.repository.get_active_session(channel_id, thread_id)
        if existing is not None:
            app.repository.stop_session(existing["id"])
            old_bridge = _remove_bridge(channel)
            if old_bridge:
                await old_bridge.disconnect()

        # Create new session
        session_id = app.repository.create_session(
            discord_guild_id=guild_id,
            discord_channel_id=channel_id,
            discord_thread_id=thread_id,
            status="active",
            is_funnel=is_funnel,
        )
        app.repository.add_message(session_id, "discord", prompt)

        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            await channel.send(f"{user_mention} Failed to create session.")
            return

        # Handle attachment
        attachment_paths: list[Path] = []
        if attachment is not None:
            upload_dir = (
                app.settings.output_dir / "_discord_uploads" / str(session_id)
            )
            attachment_paths.append(
                await save_attachment_to_workspace(attachment, upload_dir)
            )

        # Build the prompt
        if is_funnel:
            full_prompt = normalize_run_prompt(
                build_funnel_prompt(prompt),
                repo_dir=app.settings.repo_dir,
                output_dir=app.settings.output_dir,
                attachment_paths=attachment_paths,
            )
        else:
            full_prompt = normalize_run_prompt(
                prompt,
                repo_dir=app.settings.repo_dir,
                output_dir=app.settings.output_dir,
                attachment_paths=attachment_paths,
            )

        # Create and connect the agent bridge
        bridge = AgentBridge(
            repo_dir=app.settings.repo_dir,
            output_dir=app.settings.output_dir,
            env=app.settings.agent_env(),
        )
        try:
            await bridge.connect()
        except Exception as exc:
            logger.exception("Failed to connect AgentBridge")
            await channel.send(
                trim_for_discord(
                    f"{user_mention} Failed to start agent: {exc}"
                )
            )
            app.repository.update_session_status(session_id, "error")
            return

        _set_bridge(channel, bridge)

        # Run the first turn
        await run_agent_turn(
            channel, session, bridge, full_prompt, user_mention
        )

    async def handle_send(
        channel: Any,
        message: str,
        user_mention: str,
        attachment: Any | None = None,
    ) -> None:
        channel_id, thread_id = get_channel_context(channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            await channel.send(
                f"{user_mention} No active session. Start one with `/agent-start` or `/agent-funnel`."
            )
            return

        app.repository.add_message(session["id"], "discord", message)

        # Handle attachment
        attachment_paths: list[Path] = []
        if attachment is not None:
            if session["run_dir"]:
                upload_dir = Path(session["run_dir"]) / "user_uploads"
            else:
                upload_dir = (
                    app.settings.output_dir
                    / "_discord_uploads"
                    / str(session["id"])
                )
            attachment_paths.append(
                await save_attachment_to_workspace(attachment, upload_dir)
            )

        full_prompt = normalize_run_prompt(
            message,
            repo_dir=app.settings.repo_dir,
            output_dir=app.settings.output_dir,
            attachment_paths=attachment_paths,
        )

        # Get or create bridge
        bridge = _get_bridge(channel)
        if bridge is None or not bridge.connected:
            # Reconnect — session exists but bot may have restarted
            bridge = AgentBridge(
                repo_dir=app.settings.repo_dir,
                output_dir=app.settings.output_dir,
                env=app.settings.agent_env(),
            )
            try:
                await bridge.connect()
            except Exception as exc:
                logger.exception("Failed to reconnect AgentBridge")
                await channel.send(
                    trim_for_discord(
                        f"{user_mention} Failed to resume agent: {exc}"
                    )
                )
                return
            _set_bridge(channel, bridge)

        await run_agent_turn(
            channel, session, bridge, full_prompt, user_mention
        )

    # --- Slash commands ---

    @bot.event
    async def on_ready():
        # tree.sync() already runs in setup_hook — don't repeat here
        # as on_ready fires on every reconnect and blocks the event loop
        logger.info("Discord bot connected as %s", bot.user)
        print(f"Discord bot connected as {bot.user}", flush=True)

    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user or message.author.bot:
            return
        if not message.attachments:
            return

        channel_id, thread_id = get_channel_context(message.channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            return

        text = message.content or ""
        attachment_paths: list[Path] = []
        for att in message.attachments:
            if session["run_dir"]:
                upload_dir = Path(session["run_dir"]) / "user_uploads"
            else:
                upload_dir = (
                    app.settings.output_dir
                    / "_discord_uploads"
                    / str(session["id"])
                )
            attachment_paths.append(
                await save_attachment_to_workspace(att, upload_dir)
            )

        app.repository.add_message(session["id"], "discord", text)

        prompt = normalize_run_prompt(
            text,
            repo_dir=app.settings.repo_dir,
            output_dir=app.settings.output_dir,
            attachment_paths=attachment_paths,
        )

        bridge = _get_bridge(message.channel)
        if bridge is None or not bridge.connected:
            bridge = AgentBridge(
                repo_dir=app.settings.repo_dir,
                output_dir=app.settings.output_dir,
                env=app.settings.agent_env(),
            )
            try:
                await bridge.connect()
            except Exception as exc:
                logger.exception("Failed to connect AgentBridge for attachment")
                await message.channel.send(
                    trim_for_discord(f"Failed to process attachment: {exc}")
                )
                return
            _set_bridge(message.channel, bridge)

        asyncio.create_task(
            run_agent_turn(
                message.channel,
                session,
                bridge,
                prompt,
                message.author.mention,
            )
        )

    @bot.tree.command(
        name="agent-start",
        description="Start a new Claude session in this channel",
    )
    @app_commands.describe(prompt="The prompt to send to Claude")
    @app_commands.describe(
        attachment="Optional image or file for Claude to use"
    )
    async def agent_start_slash(
        interaction: discord.Interaction,
        prompt: str,
        attachment: discord.Attachment | None = None,
    ):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Session starting. Streaming progress to this channel...",
            ephemeral=True,
        )
        asyncio.create_task(
            handle_start(
                interaction.channel,
                str(interaction.guild_id) if interaction.guild_id else None,
                prompt,
                interaction.user.mention,
                is_funnel=False,
                attachment=attachment,
            )
        )

    @bot.tree.command(
        name="agent-funnel",
        description="Start a new FunnelAgent pipeline in this channel",
    )
    @app_commands.describe(
        prompt="Product URL or funnel brief for FunnelAgent"
    )
    @app_commands.describe(
        attachment="Optional product image for FunnelAgent"
    )
    async def agent_funnel_slash(
        interaction: discord.Interaction,
        prompt: str,
        attachment: discord.Attachment | None = None,
    ):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Funnel pipeline starting. Streaming progress to this channel...",
            ephemeral=True,
        )
        asyncio.create_task(
            handle_start(
                interaction.channel,
                str(interaction.guild_id) if interaction.guild_id else None,
                prompt,
                interaction.user.mention,
                is_funnel=True,
                attachment=attachment,
            )
        )

    @bot.tree.command(
        name="agent-send",
        description="Send a follow-up message to the active session",
    )
    @app_commands.describe(message="The message to send to Claude")
    @app_commands.describe(
        attachment="Optional image or file for Claude to use"
    )
    async def agent_send_slash(
        interaction: discord.Interaction,
        message: str,
        attachment: discord.Attachment | None = None,
    ):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            "Message sent. Streaming response...",
            ephemeral=True,
        )
        asyncio.create_task(
            handle_send(
                interaction.channel,
                message,
                interaction.user.mention,
                attachment=attachment,
            )
        )

    @bot.tree.command(
        name="agent-status",
        description="Show the current session status",
    )
    async def agent_status_slash(interaction: discord.Interaction):
        channel_id, thread_id = get_channel_context(interaction.channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            await interaction.response.send_message(
                "No active session.", ephemeral=True
            )
            return

        lines = [
            f"**Session ID:** {session['id']}",
            f"**Status:** {session['status']}",
            f"**Type:** {'Funnel Pipeline' if session['is_funnel'] else 'Generic'}",
        ]
        if session["current_step"]:
            lines.append(f"**Current Step:** {session['current_step']}")
        if session["run_name"]:
            lines.append(f"**Run:** {session['run_name']}")

        artifacts = app.repository.list_artifacts(session["id"])
        if artifacts:
            lines.append(f"**Artifacts:** {len(artifacts)} files")
            lines.extend(
                f"  - `{item['relative_path']}`" for item in artifacts[:10]
            )
            if len(artifacts) > 10:
                lines.append(f"  ... and {len(artifacts) - 10} more")

        await interaction.response.send_message(
            "\n".join(lines), ephemeral=True
        )

    @bot.tree.command(
        name="agent-files",
        description="List generated files for the active run",
    )
    async def agent_files_slash(interaction: discord.Interaction):
        channel_id, thread_id = get_channel_context(interaction.channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            await interaction.response.send_message(
                "No active session.", ephemeral=True
            )
            return

        artifacts = app.repository.list_artifacts(session["id"])
        if not artifacts:
            await interaction.response.send_message(
                "No files generated yet.", ephemeral=True
            )
            return

        lines = [
            f"`{item['relative_path']}` ({item['kind']}, {item['size_bytes']} bytes)"
            for item in artifacts
        ]
        await interaction.response.send_message(
            trim_for_discord("\n".join(lines)), ephemeral=True
        )

    @bot.tree.command(
        name="agent-get",
        description="Download a file from the active run",
    )
    @app_commands.describe(
        path="The relative file path inside the run directory"
    )
    async def agent_get_slash(interaction: discord.Interaction, path: str):
        channel_id, thread_id = get_channel_context(interaction.channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None or not session["run_dir"]:
            await interaction.response.send_message(
                "No active run directory.", ephemeral=True
            )
            return

        file_path = Path(session["run_dir"]) / path
        if not file_path.exists() or not file_path.is_file():
            await interaction.response.send_message(
                f"File not found: `{path}`", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Uploading `{path}`",
            file=discord.File(file_path),
            ephemeral=True,
        )

    @bot.tree.command(
        name="agent-stop",
        description="Stop the current session",
    )
    async def agent_stop_slash(interaction: discord.Interaction):
        channel_id, thread_id = get_channel_context(interaction.channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            await interaction.response.send_message(
                "No active session.", ephemeral=True
            )
            return

        # Disconnect the bridge
        bridge = _remove_bridge(interaction.channel)
        if bridge:
            await bridge.interrupt()
            await bridge.disconnect()

        app.repository.stop_session(session["id"])
        await interaction.response.send_message(
            "Session stopped.", ephemeral=True
        )

    return bot
