import os
import tempfile
from pathlib import Path

import pytest

from discord_bot.app.config import Settings
from discord_bot.app.db import init_db
from discord_bot.app.repository import Repository


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    return path


@pytest.fixture
def repository(db_path):
    return Repository(db_path)


@pytest.fixture
def settings(tmp_path):
    return Settings(
        discord_bot_token="test-token",
        discord_application_id="123456789",
        discord_public_key="test-key",
        anthropic_api_key="test-anthropic-key",
        repo_dir=tmp_path / "repo",
        output_dir=tmp_path / "output",
        db_path=tmp_path / "test.db",
        log_dir=tmp_path / "logs",
        openai_api_key="test-openai-key",
        gemini_api_key="test-gemini-key",
        r2_access_key_id="",
        r2_secret_access_key="",
        r2_endpoint_url="",
        r2_bucket_name="",
        r2_public_url="",
        git_auto_update=True,
        git_update_interval=3600,
    )
