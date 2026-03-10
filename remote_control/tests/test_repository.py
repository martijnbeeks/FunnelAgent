from remote_control.app.db import init_db
from remote_control.app.artifacts import ArtifactRecord
from remote_control.app.repository import Repository


def test_repository_creates_and_reads_active_session(tmp_path):
    db_path = tmp_path / "control.db"
    init_db(db_path)
    repo = Repository(db_path)

    session_id = repo.create_session(
        discord_guild_id="guild-1",
        discord_channel_id="channel-1",
        discord_thread_id="thread-1",
        claude_session_id="11111111-1111-1111-1111-111111111111",
        status="active",
    )

    session = repo.get_active_session("channel-1", "thread-1")

    assert session is not None
    assert session["id"] == session_id
    assert session["claude_session_id"] == "11111111-1111-1111-1111-111111111111"


def test_repository_replaces_lists_and_stops_session(tmp_path):
    db_path = tmp_path / "control.db"
    init_db(db_path)
    repo = Repository(db_path)

    session_id = repo.create_session(
        discord_guild_id=None,
        discord_channel_id="channel-1",
        discord_thread_id=None,
        claude_session_id="11111111-1111-1111-1111-111111111111",
        status="active",
    )

    repo.replace_artifacts(
        session_id,
        [
            ArtifactRecord(
                relative_path="advertorial.html",
                size_bytes=123,
                modified_at="1",
                kind="html",
            )
        ],
    )
    artifacts = repo.list_artifacts(session_id)
    repo.stop_session(session_id)

    assert len(artifacts) == 1
    assert artifacts[0]["relative_path"] == "advertorial.html"
    assert repo.get_active_session("channel-1", None) is None
