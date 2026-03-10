import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_session(
        self,
        discord_guild_id: str | None,
        discord_channel_id: str,
        discord_thread_id: str | None,
        status: str,
        is_funnel: bool = False,
        claude_session_id: str | None = None,
        run_name: str | None = None,
        run_dir: str | None = None,
    ) -> int:
        now = utc_now()
        conn = self._connect()
        try:
            cursor = conn.execute(
                """
                insert into sessions (
                    discord_guild_id,
                    discord_channel_id,
                    discord_thread_id,
                    claude_session_id,
                    run_name,
                    run_dir,
                    status,
                    is_funnel,
                    current_step,
                    created_at,
                    updated_at
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    discord_guild_id,
                    discord_channel_id,
                    discord_thread_id,
                    claude_session_id or "",
                    run_name,
                    run_dir,
                    status,
                    1 if is_funnel else 0,
                    None,
                    now,
                    now,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)
        finally:
            conn.close()

    def get_active_session(
        self, discord_channel_id: str, discord_thread_id: str | None
    ) -> sqlite3.Row | None:
        conn = self._connect()
        try:
            cursor = conn.execute(
                """
                select *
                from sessions
                where discord_channel_id = ?
                  and (discord_thread_id is ? or discord_thread_id = ?)
                  and status in ('active', 'waiting_input')
                order by updated_at desc
                limit 1
                """,
                (discord_channel_id, discord_thread_id, discord_thread_id),
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def update_session_status(self, session_id: int, status: str) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "update sessions set status = ?, updated_at = ? where id = ?",
                (status, utc_now(), session_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_session_claude_id(
        self, session_id: int, claude_session_id: str
    ) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "update sessions set claude_session_id = ?, updated_at = ? where id = ?",
                (claude_session_id, utc_now(), session_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_session_step(self, session_id: int, step: str) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "update sessions set current_step = ?, updated_at = ? where id = ?",
                (step, utc_now(), session_id),
            )
            conn.commit()
        finally:
            conn.close()

    def add_message(
        self,
        session_id: int,
        source: str,
        content: str,
        discord_message_id: str | None = None,
    ) -> None:
        now = utc_now()
        conn = self._connect()
        try:
            conn.execute(
                """
                insert into messages (
                    session_id, source, discord_message_id, content, created_at
                ) values (?, ?, ?, ?, ?)
                """,
                (session_id, source, discord_message_id, content, now),
            )
            conn.execute(
                "update sessions set updated_at = ? where id = ?",
                (now, session_id),
            )
            conn.commit()
        finally:
            conn.close()

    def replace_artifacts(self, session_id: int, artifacts: list[object]) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "delete from artifacts where session_id = ?", (session_id,)
            )
            for artifact in artifacts:
                conn.execute(
                    """
                    insert into artifacts (
                        session_id, relative_path, size_bytes, modified_at, kind
                    ) values (?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        artifact.relative_path,
                        artifact.size_bytes,
                        artifact.modified_at,
                        artifact.kind,
                    ),
                )
            conn.execute(
                "update sessions set updated_at = ? where id = ?",
                (utc_now(), session_id),
            )
            conn.commit()
        finally:
            conn.close()

    def list_artifacts(self, session_id: int) -> list[sqlite3.Row]:
        conn = self._connect()
        try:
            cursor = conn.execute(
                """
                select *
                from artifacts
                where session_id = ?
                order by relative_path asc
                """,
                (session_id,),
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def update_session_run(
        self, session_id: int, run_name: str, run_dir: str
    ) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                update sessions
                set run_name = ?, run_dir = ?, updated_at = ?
                where id = ?
                """,
                (run_name, run_dir, utc_now(), session_id),
            )
            conn.commit()
        finally:
            conn.close()

    def stop_session(self, session_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                update sessions
                set status = 'stopped', updated_at = ?
                where id = ?
                """,
                (utc_now(), session_id),
            )
            conn.commit()
        finally:
            conn.close()
