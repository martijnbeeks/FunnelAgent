import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from remote_control.app.artifacts import scan_artifacts
from remote_control.app.claude_runner import run_prompt

try:
    import discord
    from discord import app_commands
except ModuleNotFoundError:  # pragma: no cover - exercised in runtime, not unit tests
    discord = None
    app_commands = None


FUNNEL_PREFIX = (
    "Run /funnel-agent:funnel-orchestrator and continue the workflow in this session."
)
AUTO_ATTACH_KINDS = {"document", "html", "image"}
MAX_AUTO_ATTACHMENTS = 8
MAX_AUTO_ATTACH_SIZE_BYTES = 8 * 1024 * 1024
logger = logging.getLogger("remote_control.discord_bot")


@dataclass(frozen=True)
class BackgroundJobResult:
    message: str
    attachment_paths: list[Path]


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
            "The user also uploaded file(s) into the workspace. Use them when relevant, especially if the request mentions a product image or reference image.\n"
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


def _extract_text(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("result", "text", "message"):
            if key in value:
                extracted = _extract_text(value[key])
                if extracted:
                    return extracted
        for item in value.values():
            extracted = _extract_text(item)
            if extracted:
                return extracted
    if isinstance(value, list):
        for item in value:
            extracted = _extract_text(item)
            if extracted:
                return extracted
    return None


def extract_response_text(payload: str) -> str:
    stripped = payload.strip()
    if not stripped:
        return ""
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped
    return _extract_text(parsed) or stripped


def trim_for_discord(text: str, limit: int = 1900) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3]}..."


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


async def save_attachment_to_workspace(attachment: Any, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(getattr(attachment, "filename", "upload.bin")).name or "upload.bin"
    destination = destination_dir / filename
    suffix = destination.suffix
    stem = destination.stem
    counter = 1
    while destination.exists():
        destination = destination_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    await attachment.save(destination)
    return destination


async def execute_background_job(channel: Any, user_mention: str, job: Any) -> None:
    try:
        result = await job()
        if isinstance(result, BackgroundJobResult):
            files = [discord.File(path) for path in result.attachment_paths] if result.attachment_paths else None
            await channel.send(
                trim_for_discord(f"{user_mention}\n{result.message}"),
                files=files,
            )
            return
        await channel.send(trim_for_discord(f"{user_mention}\n{result}"))
    except Exception as exc:  # pragma: no cover - exercised in runtime
        logger.exception("Background Discord job failed")
        await channel.send(trim_for_discord(f"{user_mention}\nAgent error:\n{exc}"))


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


async def call_claude(app: Any, session_row: Any, prompt: str, resume: bool = False) -> str:
    result = await asyncio.to_thread(
        run_prompt,
        claude_bin=app.settings.claude_bin,
        repo_dir=app.settings.repo_dir,
        output_dir=app.settings.output_dir,
        session_id=session_row["claude_session_id"],
        prompt=prompt,
        resume=resume,
    )
    if not result.ok:
        error_text = result.stderr.strip() or result.stdout.strip() or "Claude call failed."
        return f"Claude error:\n{trim_for_discord(error_text)}"

    app.repository.add_message(session_row["id"], "claude", result.stdout)
    discovered = discover_run_dir(app.settings.output_dir)
    if discovered is not None:
        run_name, run_dir = discovered
        app.repository.update_session_run(
            session_row["id"],
            run_name=run_name,
            run_dir=str(run_dir),
        )
        app.repository.replace_artifacts(session_row["id"], scan_artifacts(run_dir))
    return trim_for_discord(extract_response_text(result.stdout) or result.stdout)


def create_discord_bot(app: Any):
    if discord is None or app_commands is None:
        raise RuntimeError(
            "discord.py is not installed. Install remote_control/requirements.txt first."
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

    async def handle_start(
        channel: Any,
        guild_id: str | None,
        prompt: str,
        attachment: Any | None = None,
    ) -> str:
        channel_id, thread_id = get_channel_context(channel)
        existing = app.repository.get_active_session(channel_id, thread_id)
        if existing is not None:
            app.repository.stop_session(existing["id"])

        claude_session_id = str(uuid4())
        session_id = app.repository.create_session(
            discord_guild_id=guild_id,
            discord_channel_id=channel_id,
            discord_thread_id=thread_id,
            claude_session_id=claude_session_id,
            status="active",
        )
        app.repository.add_message(session_id, "discord", prompt)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            return "Failed to create a session."
        attachment_paths: list[Path] = []
        if attachment is not None:
            upload_dir = app.settings.output_dir / "_discord_uploads" / claude_session_id
            attachment_paths.append(await save_attachment_to_workspace(attachment, upload_dir))
        response = await call_claude(
            app,
            session,
            normalize_run_prompt(
                prompt,
                repo_dir=app.settings.repo_dir,
                output_dir=app.settings.output_dir,
                attachment_paths=attachment_paths,
            ),
            resume=False,
        )
        refreshed = app.repository.get_active_session(channel_id, thread_id)
        if refreshed is None:
            return f"Session started.\n\n{response}"
        return BackgroundJobResult(
            message=f"Session started.\n\n{response}",
            attachment_paths=collect_auto_attachment_paths(app.repository, refreshed),
        )

    async def handle_send(
        channel: Any,
        message: str,
        attachment: Any | None = None,
    ) -> str:
        channel_id, thread_id = get_channel_context(channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            return "No active session for this channel. Start one with /agent-start or !agent-start."
        app.repository.add_message(session["id"], "discord", message)
        attachment_paths: list[Path] = []
        if attachment is not None:
            if session["run_dir"]:
                upload_dir = Path(session["run_dir"]) / "user_uploads"
            else:
                upload_dir = app.settings.output_dir / "_discord_uploads" / session["claude_session_id"]
            attachment_paths.append(await save_attachment_to_workspace(attachment, upload_dir))
        response = await call_claude(
            app,
            session,
            normalize_run_prompt(
                message,
                repo_dir=app.settings.repo_dir,
                output_dir=app.settings.output_dir,
                attachment_paths=attachment_paths,
            ),
            resume=True,
        )
        refreshed = app.repository.get_active_session(channel_id, thread_id)
        if refreshed is None:
            return response
        return BackgroundJobResult(
            message=response,
            attachment_paths=collect_auto_attachment_paths(app.repository, refreshed),
        )

    def handle_status(channel: Any) -> str:
        channel_id, thread_id = get_channel_context(channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            return "No active session."
        lines = [
            f"Session ID: {session['claude_session_id']}",
            f"Status: {session['status']}",
        ]
        if session["run_name"]:
            lines.append(f"Run: {session['run_name']}")
        if session["run_dir"]:
            lines.append(f"Run dir: {session['run_dir']}")
        artifacts = app.repository.list_artifacts(session["id"])
        if artifacts:
            lines.append("Artifacts:")
            lines.extend(f"- {item['relative_path']}" for item in artifacts[:10])
        return "\n".join(lines)

    def handle_files(channel: Any) -> str:
        channel_id, thread_id = get_channel_context(channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            return "No active session."
        artifacts = app.repository.list_artifacts(session["id"])
        if not artifacts:
            return "No indexed files yet."
        return "\n".join(item["relative_path"] for item in artifacts)

    async def handle_get(channel: Any, relative_path: str):
        channel_id, thread_id = get_channel_context(channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None or not session["run_dir"]:
            return None, "No active run directory."
        file_path = Path(session["run_dir"]) / relative_path
        if not file_path.exists() or not file_path.is_file():
            return None, "File not found."
        return discord.File(file_path), f"Uploading `{relative_path}`"

    def handle_stop(channel: Any) -> str:
        channel_id, thread_id = get_channel_context(channel)
        session = app.repository.get_active_session(channel_id, thread_id)
        if session is None:
            return "No active session."
        app.repository.stop_session(session["id"])
        return "Session stopped."

    @bot.event
    async def on_ready():
        await bot.tree.sync()
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
                    / session["claude_session_id"]
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

        async def job():
            response = await call_claude(app, session, prompt, resume=True)
            refreshed = app.repository.get_active_session(channel_id, thread_id)
            if refreshed is None:
                return response
            return BackgroundJobResult(
                message=response,
                attachment_paths=collect_auto_attachment_paths(
                    app.repository, refreshed
                ),
            )

        asyncio.create_task(
            execute_background_job(
                message.channel, message.author.mention, job
            )
        )

    @bot.tree.command(name="agent-start", description="Start a new Claude session in this channel")
    @app_commands.describe(prompt="The prompt to send to Claude")
    @app_commands.describe(attachment="Optional image or file for Claude to use from this request")
    async def agent_start_slash(
        interaction: discord.Interaction,
        prompt: str,
        attachment: discord.Attachment | None = None,
    ):
        await interaction.response.send_message(
            "Session queued. I will post the result in this channel.",
            ephemeral=True,
        )

        async def job():
            return await handle_start(
                interaction.channel,
                str(interaction.guild_id) if interaction.guild_id else None,
                prompt,
                attachment,
            )

        asyncio.create_task(
            execute_background_job(interaction.channel, interaction.user.mention, job)
        )

    @bot.tree.command(
        name="agent-funnel",
        description="Start a new FunnelAgent orchestration session in this channel",
    )
    @app_commands.describe(prompt="Product or funnel brief to give FunnelAgent")
    @app_commands.describe(attachment="Optional image or file for FunnelAgent to use from this request")
    async def agent_funnel_slash(
        interaction: discord.Interaction,
        prompt: str,
        attachment: discord.Attachment | None = None,
    ):
        await interaction.response.send_message(
            "Funnel job queued. I will post the result in this channel.",
            ephemeral=True,
        )

        async def job():
            return await handle_start(
                interaction.channel,
                str(interaction.guild_id) if interaction.guild_id else None,
                build_funnel_prompt(prompt),
                attachment,
            )

        asyncio.create_task(
            execute_background_job(interaction.channel, interaction.user.mention, job)
        )

    @bot.tree.command(name="agent-send", description="Send a follow-up message to the active Claude session")
    @app_commands.describe(message="The message to send to Claude")
    @app_commands.describe(attachment="Optional image or file for Claude to use from this message")
    async def agent_send_slash(
        interaction: discord.Interaction,
        message: str,
        attachment: discord.Attachment | None = None,
    ):
        await interaction.response.send_message(
            "Message queued. I will post the result in this channel.",
            ephemeral=True,
        )

        async def job():
            return await handle_send(interaction.channel, message, attachment)

        asyncio.create_task(
            execute_background_job(interaction.channel, interaction.user.mention, job)
        )

    @bot.tree.command(name="agent-status", description="Show the current Claude session status")
    async def agent_status_slash(interaction: discord.Interaction):
        await interaction.response.send_message(handle_status(interaction.channel), ephemeral=True)

    @bot.tree.command(name="agent-files", description="List generated files for the active run")
    async def agent_files_slash(interaction: discord.Interaction):
        await interaction.response.send_message(
            trim_for_discord(handle_files(interaction.channel)),
            ephemeral=True,
        )

    @bot.tree.command(name="agent-stop", description="Stop the current Claude session")
    async def agent_stop_slash(interaction: discord.Interaction):
        await interaction.response.send_message(handle_stop(interaction.channel), ephemeral=True)

    @bot.tree.command(name="agent-get", description="Upload a file from the active run")
    @app_commands.describe(path="The relative file path inside the run directory")
    async def agent_get_slash(interaction: discord.Interaction, path: str):
        file_obj, message = await handle_get(interaction.channel, path)
        if file_obj is None:
            await interaction.response.send_message(message, ephemeral=True)
            return
        await interaction.response.send_message(message, file=file_obj, ephemeral=True)

    return bot
