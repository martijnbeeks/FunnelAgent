"""Convert Claude Agent SDK messages into Discord-friendly text."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger("discord_bot.message_processor")

# Patterns that indicate Claude is asking the user a question
QUESTION_PATTERNS = [
    re.compile(r"\?\s*$", re.MULTILINE),
    re.compile(r"\b(which|would you like|please choose|select|do you want|shall i)\b", re.IGNORECASE),
]


def format_tool_use(name: str, tool_input: dict) -> str | None:
    """Return a short progress line for a tool-use block, or None to skip."""
    if name == "Bash":
        cmd = tool_input.get("command", "")
        if len(cmd) > 120:
            cmd = cmd[:117] + "..."
        return f"Running: `{cmd}`"

    if name in ("Task", "Agent"):
        desc = tool_input.get("description", "")
        prompt = tool_input.get("prompt", "")
        label = desc or prompt[:80]
        if label:
            return f"Spawning sub-agent: {label}"
        return "Spawning sub-agent..."

    if name == "Read":
        path = tool_input.get("file_path", "")
        return f"Reading: `{path}`"

    if name == "Write":
        path = tool_input.get("file_path", "")
        return f"Writing: `{path}`"

    if name == "Edit":
        path = tool_input.get("file_path", "")
        return f"Editing: `{path}`"

    if name == "Glob":
        pattern = tool_input.get("pattern", "")
        return f"Searching files: `{pattern}`"

    if name == "Grep":
        pattern = tool_input.get("pattern", "")
        return f"Searching content: `{pattern}`"

    if name == "WebFetch":
        url = tool_input.get("url", "")
        return f"Fetching: `{url}`"

    if name == "Skill":
        skill = tool_input.get("skill", "")
        return f"Running skill: `{skill}`"

    return None


def looks_like_question(text: str) -> bool:
    """Heuristic check if text ends with a question for the user."""
    for pattern in QUESTION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def extract_text_content(content_blocks: list) -> str:
    """Extract all text from a list of content blocks."""
    try:
        from claude_agent_sdk import TextBlock
    except ModuleNotFoundError:  # pragma: no cover
        return ""

    parts: list[str] = []
    for block in content_blocks:
        if isinstance(block, TextBlock):
            parts.append(block.text)
    return "\n".join(parts)


def extract_tool_progress(content_blocks: list) -> list[str]:
    """Extract progress lines from tool-use blocks."""
    try:
        from claude_agent_sdk import ToolUseBlock
    except ModuleNotFoundError:  # pragma: no cover
        return []

    lines: list[str] = []
    for block in content_blocks:
        if isinstance(block, ToolUseBlock):
            line = format_tool_use(block.name, block.input)
            if line:
                lines.append(line)
    return lines
