from discord_bot.app.artifacts import ArtifactRecord


def test_create_and_get_session(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
        is_funnel=True,
    )
    assert session_id > 0

    session = repository.get_active_session("c1", None)
    assert session is not None
    assert session["status"] == "active"
    assert session["is_funnel"] == 1


def test_get_active_session_none(repository):
    result = repository.get_active_session("nonexistent", None)
    assert result is None


def test_stop_session(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )
    repository.stop_session(session_id)

    session = repository.get_active_session("c1", None)
    assert session is None


def test_update_session_status(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )
    repository.update_session_status(session_id, "waiting_input")

    session = repository.get_active_session("c1", None)
    assert session is not None
    assert session["status"] == "waiting_input"


def test_update_session_run(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )
    repository.update_session_run(session_id, "my-product", "/output/my-product")

    session = repository.get_active_session("c1", None)
    assert session["run_name"] == "my-product"
    assert session["run_dir"] == "/output/my-product"


def test_add_message(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )
    repository.add_message(session_id, "discord", "Hello!")
    repository.add_message(session_id, "claude", "Hi there!")

    # Messages are stored — no list method but we can verify no error


def test_replace_and_list_artifacts(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )

    artifacts = [
        ArtifactRecord("00_product_info.md", 1234, "1700000000", "document"),
        ArtifactRecord("logo.png", 5678, "1700000001", "image"),
    ]
    repository.replace_artifacts(session_id, artifacts)

    result = repository.list_artifacts(session_id)
    assert len(result) == 2
    assert result[0]["relative_path"] == "00_product_info.md"
    assert result[1]["relative_path"] == "logo.png"


def test_replace_artifacts_replaces(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )

    artifacts_v1 = [
        ArtifactRecord("old.txt", 100, "1700000000", "document"),
    ]
    repository.replace_artifacts(session_id, artifacts_v1)

    artifacts_v2 = [
        ArtifactRecord("new.txt", 200, "1700000001", "document"),
    ]
    repository.replace_artifacts(session_id, artifacts_v2)

    result = repository.list_artifacts(session_id)
    assert len(result) == 1
    assert result[0]["relative_path"] == "new.txt"


def test_update_session_step(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )
    repository.update_session_step(session_id, "Step 2.1: Synthesis")

    session = repository.get_active_session("c1", None)
    assert session["current_step"] == "Step 2.1: Synthesis"


def test_update_session_claude_id(repository):
    session_id = repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id=None,
        status="active",
    )
    repository.update_session_claude_id(session_id, "claude-uuid-123")

    session = repository.get_active_session("c1", None)
    assert session["claude_session_id"] == "claude-uuid-123"


def test_thread_session_isolation(repository):
    repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id="t1",
        status="active",
    )
    repository.create_session(
        discord_guild_id="g1",
        discord_channel_id="c1",
        discord_thread_id="t2",
        status="active",
    )

    s1 = repository.get_active_session("c1", "t1")
    s2 = repository.get_active_session("c1", "t2")
    assert s1 is not None
    assert s2 is not None
    assert s1["id"] != s2["id"]
