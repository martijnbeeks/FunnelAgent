import asyncio

import pytest

from discord_bot.app.stream_buffer import StreamBuffer


@pytest.mark.asyncio
async def test_basic_flush():
    messages = []

    async def send(text):
        messages.append(text)

    buffer = StreamBuffer(send, chunk_size=100, min_interval=0.0)
    await buffer.append("Hello, world!")
    await buffer.flush()

    assert len(messages) == 1
    assert messages[0] == "Hello, world!"


@pytest.mark.asyncio
async def test_empty_flush():
    messages = []

    async def send(text):
        messages.append(text)

    buffer = StreamBuffer(send, chunk_size=100, min_interval=0.0)
    await buffer.flush()

    assert len(messages) == 0


@pytest.mark.asyncio
async def test_chunking_at_newline():
    messages = []

    async def send(text):
        messages.append(text)

    buffer = StreamBuffer(send, chunk_size=20, min_interval=0.0)
    await buffer.append("Short line\nAnother line here that is long")
    await buffer.flush()

    # First chunk should break at newline
    assert messages[0] == "Short line\n"
    # Remaining text gets chunked further
    combined = "".join(messages[1:])
    assert "Another line here that is long" == combined


@pytest.mark.asyncio
async def test_append_line():
    messages = []

    async def send(text):
        messages.append(text)

    buffer = StreamBuffer(send, chunk_size=1000, min_interval=0.0)
    await buffer.append_line("Line 1")
    await buffer.append_line("Line 2")
    await buffer.flush()

    assert len(messages) == 1
    assert "Line 1\nLine 2\n" == messages[0]


@pytest.mark.asyncio
async def test_auto_flush_on_large_buffer():
    messages = []

    async def send(text):
        messages.append(text)

    buffer = StreamBuffer(send, chunk_size=10, min_interval=0.0)
    await buffer.append("This is a very long text that exceeds the chunk size")
    # Should have been flushed automatically
    await buffer.flush()

    assert len(messages) >= 1
    combined = "".join(messages)
    assert "This is a very long text" in combined
