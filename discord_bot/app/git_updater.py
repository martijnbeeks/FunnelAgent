"""Auto-update skills by pulling from the master branch."""

from __future__ import annotations

import asyncio
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("discord_bot.git_updater")


def git_pull(repo_dir: Path) -> str:
    """Run git pull origin master in the repo directory. Returns stdout."""
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "master"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            logger.warning(
                "git pull failed (rc=%d): %s", result.returncode, result.stderr
            )
            return f"git pull failed: {result.stderr.strip()}"
        logger.info("git pull: %s", output)
        return output
    except subprocess.TimeoutExpired:
        logger.warning("git pull timed out")
        return "git pull timed out"
    except FileNotFoundError:
        logger.warning("git not found on PATH")
        return "git not found"


async def pull_on_startup(repo_dir: Path) -> str:
    """Run git pull in a thread to avoid blocking the event loop."""
    return await asyncio.to_thread(git_pull, repo_dir)


async def periodic_pull(repo_dir: Path, interval: int) -> None:
    """Background task: pull every `interval` seconds."""
    while True:
        await asyncio.sleep(interval)
        try:
            result = await asyncio.to_thread(git_pull, repo_dir)
            if "Already up to date" not in result:
                logger.info("Periodic git pull result: %s", result)
        except Exception:
            logger.exception("Periodic git pull failed")
