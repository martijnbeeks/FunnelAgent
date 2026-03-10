import sqlite3
from pathlib import Path


SCHEMA = """
create table if not exists sessions (
    id integer primary key,
    discord_guild_id text,
    discord_channel_id text,
    discord_thread_id text,
    claude_session_id text not null,
    run_name text,
    run_dir text,
    status text not null,
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


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
    finally:
        conn.close()
