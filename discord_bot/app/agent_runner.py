"""AgentBridge: wraps claude-agent-sdk ClaudeSDKClient for multi-turn streaming sessions."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Awaitable

try:
    from claude_agent_sdk import (
        ClaudeSDKClient,
        ClaudeAgentOptions,
        AssistantMessage,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
    )
except ModuleNotFoundError:  # pragma: no cover
    ClaudeSDKClient = None
    ClaudeAgentOptions = None
    AssistantMessage = None
    ResultMessage = None
    TextBlock = None
    ToolUseBlock = None

from discord_bot.app.message_processor import (
    extract_text_content,
    extract_tool_progress,
    looks_like_question,
)

logger = logging.getLogger("discord_bot.agent_runner")
claude_raw_logger = logging.getLogger("discord_bot.claude_raw")


@dataclass
class TurnResult:
    """Result from a single agent turn (one query→response cycle)."""
    text: str = ""
    session_id: str | None = None
    is_question: bool = False
    is_error: bool = False
    cost_usd: float | None = None
    duration_ms: int = 0
    tool_progress: list[str] = field(default_factory=list)


class AgentBridge:
    """Wraps ClaudeSDKClient for multi-turn sessions with streaming.

    Usage:
        bridge = AgentBridge(repo_dir, output_dir, env)
        await bridge.connect()

        # Stream a turn
        result = await bridge.run_turn(
            prompt="Start the pipeline",
            on_text=my_text_callback,
            on_progress=my_progress_callback,
        )

        # Continue the conversation
        result = await bridge.run_turn(
            prompt="User's response",
            on_text=my_text_callback,
        )

        await bridge.disconnect()
    """

    def __init__(
        self,
        repo_dir: Path,
        output_dir: Path,
        env: dict[str, str] | None = None,
    ):
        self.repo_dir = repo_dir
        self.output_dir = output_dir
        self.env = env or {}
        self._client: ClaudeSDKClient | None = None
        self._session_id: str | None = None

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def connected(self) -> bool:
        return self._client is not None

    def _build_options(self) -> ClaudeAgentOptions:
        def _log_stderr(line: str) -> None:
            claude_raw_logger.warning("CLI stderr: %s", line.rstrip())

        # Unset CLAUDECODE to allow launching from within a Claude Code session
        # Set IS_SANDBOX=1 to allow bypassPermissions when running as root (Docker)
        agent_env = dict(self.env)
        agent_env["CLAUDECODE"] = ""
        agent_env["IS_SANDBOX"] = "1"

        return ClaudeAgentOptions(
            allowed_tools=[
                "Read", "Write", "Edit", "Bash", "Glob", "Grep",
                "WebFetch", "WebSearch", "Agent", "Task",
                "Skill", "AskUserQuestion", "NotebookEdit",
            ],
            permission_mode="bypassPermissions",
            cwd=str(self.repo_dir),
            setting_sources=["project"],
            system_prompt={"type": "preset", "preset": "claude_code"},
            env=agent_env,
            stderr=_log_stderr,
        )

    async def connect(self) -> None:
        """Create and connect the SDK client."""
        if self._client is not None:
            return
        options = self._build_options()
        self._client = ClaudeSDKClient(options=options)
        await self._client.connect()
        logger.info("AgentBridge connected (cwd=%s)", self.repo_dir)

    async def disconnect(self) -> None:
        """Disconnect the SDK client."""
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception:
                logger.exception("Error disconnecting agent client")
            self._client = None
            logger.info("AgentBridge disconnected")

    async def run_turn(
        self,
        prompt: str,
        on_text: Callable[[str], Awaitable[None]] | None = None,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> TurnResult:
        """Send a prompt and stream the response.

        Args:
            prompt: The user message to send.
            on_text: Async callback for text content chunks.
            on_progress: Async callback for tool-use progress lines.

        Returns:
            TurnResult with accumulated text and metadata.
        """
        if self._client is None:
            raise RuntimeError("AgentBridge not connected. Call connect() first.")

        result = TurnResult()
        text_parts: list[str] = []

        await self._client.query(prompt)

        async for message in self._client.receive_response():
            claude_raw_logger.info("SDK message: %s", type(message).__name__)

            if isinstance(message, AssistantMessage):
                # Extract text content
                text = extract_text_content(message.content)
                if text:
                    text_parts.append(text)
                    if on_text:
                        try:
                            await on_text(text)
                        except Exception:
                            logger.exception("on_text callback failed")

                # Extract tool progress
                progress_lines = extract_tool_progress(message.content)
                for line in progress_lines:
                    result.tool_progress.append(line)
                    if on_progress:
                        try:
                            await on_progress(line)
                        except Exception:
                            logger.exception("on_progress callback failed")

            elif isinstance(message, ResultMessage):
                result.session_id = message.session_id
                result.is_error = message.is_error
                result.cost_usd = getattr(message, "total_cost_usd", None)
                result.duration_ms = message.duration_ms
                self._session_id = message.session_id
                claude_raw_logger.info(
                    "Turn complete: session=%s, cost=$%.4f, duration=%dms",
                    message.session_id,
                    message.total_cost_usd or 0,
                    message.duration_ms,
                )

        result.text = "\n".join(text_parts) if text_parts else ""
        result.is_question = looks_like_question(result.text)

        return result

    async def interrupt(self) -> None:
        """Interrupt the current agent operation."""
        if self._client is not None:
            try:
                await self._client.interrupt()
                logger.info("Agent interrupted")
            except Exception:
                logger.exception("Error interrupting agent")

    async def __aenter__(self) -> AgentBridge:
        await self.connect()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.disconnect()
