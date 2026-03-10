import sqlite3

from remote_control.app.db import init_db


def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "control.db"

    init_db(db_path)

    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "select name from sqlite_master where type = 'table'"
            )
        }
    finally:
        conn.close()

    assert {"sessions", "messages", "artifacts"}.issubset(tables)
