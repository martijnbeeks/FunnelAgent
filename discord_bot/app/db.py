import sqlite3
from pathlib import Path


SCHEMA = """
create table if not exists sessions (
    id integer primary key,
    discord_guild_id text,
    discord_channel_id text,
    discord_thread_id text,
    claude_session_id text,
    run_name text,
    run_dir text,
    status text not null,
    is_funnel integer not null default 0,
    current_step text,
    created_at text not null,
    updated_at text not null
);

create table if not exists messages (
    id integer primary key,
    session_id integer not null,
    source text not null,
    discord_message_id text,
    content text not null,
    created_at text not null,
    foreign key(session_id) references sessions(id)
);

create table if not exists artifacts (
    id integer primary key,
    session_id integer not null,
    relative_path text not null,
    size_bytes integer not null,
    modified_at text not null,
    kind text not null,
    foreign key(session_id) references sessions(id)
);
"""


MIGRATIONS = [
    "ALTER TABLE sessions ADD COLUMN is_funnel integer not null default 0",
    "ALTER TABLE sessions ADD COLUMN current_step text",
]


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        # Apply migrations for existing databases missing new columns
        for sql in MIGRATIONS:
            try:
                conn.execute(sql)
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists — skip
                pass
    finally:
        conn.close()
