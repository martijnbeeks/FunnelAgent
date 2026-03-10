"""Rate-limited text accumulator for Discord message streaming."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Callable, Awaitable

logger = logging.getLogger("discord_bot.stream_buffer")

DISCORD_MSG_LIMIT = 2000
SAFE_CHUNK_SIZE = 1900
MIN_FLUSH_INTERVAL = 2.0  # seconds between Discord messages
BATCH_DELAY = 0.5  # seconds to wait for more text before flushing


class StreamBuffer:
    """Accumulates text and flushes to Discord respecting rate limits.

    Usage:
        buffer = StreamBuffer(send_fn)
        await buffer.append("partial text...")
        await buffer.append("more text...")
        await buffer.flush()  # flush any remaining text
    """

    def __init__(
        self,
        send_fn: Callable[[str], Awaitable[Any]],
        chunk_size: int = SAFE_CHUNK_SIZE,
        min_interval: float = MIN_FLUSH_INTERVAL,
    ):
        self.send_fn = send_fn
        self.chunk_size = chunk_size
        self.min_interval = min_interval
        self._buffer: str = ""
        self._last_flush: float = 0.0
        self._pending_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def append(self, text: str) -> None:
        """Add text to the buffer. May trigger a flush if buffer is large."""
        async with self._lock:
            self._buffer += text

            # If buffer exceeds chunk size, flush immediately
            if len(self._buffer) >= self.chunk_size:
                await self._do_flush()
                return

            # Schedule a delayed flush if not already pending
            if self._pending_task is None or self._pending_task.done():
                self._pending_task = asyncio.create_task(
                    self._delayed_flush()
                )

    async def append_line(self, line: str) -> None:
        """Add a line of text (with trailing newline)."""
        await self.append(line + "\n")

    async def flush(self) -> None:
        """Force flush any remaining buffered text."""
        async with self._lock:
            if self._pending_task and not self._pending_task.done():
                self._pending_task.cancel()
                self._pending_task = None
            await self._do_flush()

    async def _delayed_flush(self) -> None:
        """Wait briefly then flush, allowing batching of rapid updates."""
        await asyncio.sleep(BATCH_DELAY)
        async with self._lock:
            await self._do_flush()

    async def _do_flush(self) -> None:
        """Send buffered text to Discord in chunks."""
        if not self._buffer:
            return

        # Respect rate limit
        now = time.monotonic()
        wait = self._last_flush + self.min_interval - now
        if wait > 0:
            await asyncio.sleep(wait)

        while self._buffer:
            chunk = self._take_chunk()
            if not chunk.strip():
                continue
            try:
                await self.send_fn(chunk)
            except Exception:
                logger.exception("Failed to send Discord message chunk")
            self._last_flush = time.monotonic()

            # Rate-limit between chunks
            if self._buffer:
                await asyncio.sleep(self.min_interval)

    def _take_chunk(self) -> str:
        """Extract up to chunk_size chars from the buffer, preferring line breaks."""
        if len(self._buffer) <= self.chunk_size:
            chunk = self._buffer
            self._buffer = ""
            return chunk

        # Try to break at a newline within the chunk
        candidate = self._buffer[: self.chunk_size]
        last_newline = candidate.rfind("\n")
        if last_newline > 0:
            chunk = self._buffer[: last_newline + 1]
            self._buffer = self._buffer[last_newline + 1 :]
        else:
            chunk = candidate
            self._buffer = self._buffer[self.chunk_size :]
        return chunk
