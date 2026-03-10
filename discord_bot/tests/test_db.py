import sqlite3
from pathlib import Path

from discord_bot.app.db import init_db


def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "subdir" / "test.db"
    init_db(db_path)

    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "select name from sqlite_master where type='table' order by name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "sessions" in tables
    assert "messages" in tables
    assert "artifacts" in tables


def test_init_db_idempotent(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    init_db(db_path)  # should not raise


def test_sessions_schema_has_is_funnel(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("pragma table_info(sessions)")
    columns = {row[1] for row in cursor.fetchall()}
    conn.close()

    assert "is_funnel" in columns
    assert "current_step" in columns
