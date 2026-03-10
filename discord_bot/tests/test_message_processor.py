from discord_bot.app.message_processor import (
    format_tool_use,
    looks_like_question,
)


def test_format_bash_tool():
    result = format_tool_use("Bash", {"command": "python scripts/deep_research.py --prompt-file p.txt"})
    assert result.startswith("Running: `")
    assert "deep_research" in result


def test_format_bash_long_command():
    long_cmd = "x" * 200
    result = format_tool_use("Bash", {"command": long_cmd})
    assert len(result) < 200
    assert result.endswith("...`")


def test_format_task_tool():
    result = format_tool_use("Task", {"description": "Deep Research"})
    assert "Deep Research" in result


def test_format_agent_tool():
    result = format_tool_use("Agent", {"description": "Synthesis Phase 1"})
    assert "Synthesis Phase 1" in result


def test_format_read_tool():
    result = format_tool_use("Read", {"file_path": "/path/to/file.md"})
    assert "Reading" in result
    assert "file.md" in result


def test_format_write_tool():
    result = format_tool_use("Write", {"file_path": "/path/to/output.html"})
    assert "Writing" in result


def test_format_unknown_tool():
    result = format_tool_use("SomeUnknownTool", {})
    assert result is None


def test_format_skill_tool():
    result = format_tool_use("Skill", {"skill": "funnel-orchestrator"})
    assert "funnel-orchestrator" in result


def test_looks_like_question_with_mark():
    assert looks_like_question("What do you think?") is True


def test_looks_like_question_which():
    assert looks_like_question("Which avatar would you prefer") is True


def test_looks_like_question_negative():
    assert looks_like_question("File saved successfully.") is False


def test_looks_like_question_would_you():
    assert looks_like_question("Would you like to continue") is True
