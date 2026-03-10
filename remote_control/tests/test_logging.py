from remote_control.app.logging_utils import setup_logging


def test_setup_logging_creates_log_files(tmp_path):
    setup_logging(tmp_path)

    assert (tmp_path / "bot.log").exists()
    assert (tmp_path / "claude.log").exists()
