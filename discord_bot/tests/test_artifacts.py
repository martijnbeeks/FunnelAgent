from pathlib import Path

from discord_bot.app.artifacts import (
    ArtifactRecord,
    classify_artifact,
    scan_artifacts,
    diff_artifacts,
)


def test_classify_html():
    assert classify_artifact(Path("advertorial.html")) == "html"


def test_classify_image_png():
    assert classify_artifact(Path("logo.png")) == "image"


def test_classify_image_jpg():
    assert classify_artifact(Path("hero.jpg")) == "image"


def test_classify_image_webp():
    assert classify_artifact(Path("photo.webp")) == "image"


def test_classify_document_md():
    assert classify_artifact(Path("research.md")) == "document"


def test_classify_document_js():
    assert classify_artifact(Path("config.js")) == "document"


def test_classify_document_json():
    assert classify_artifact(Path("data.json")) == "document"


def test_classify_other():
    assert classify_artifact(Path("archive.zip")) == "other"


def test_scan_artifacts_empty_dir(tmp_path):
    result = scan_artifacts(tmp_path)
    assert result == []


def test_scan_artifacts_nonexistent(tmp_path):
    result = scan_artifacts(tmp_path / "nonexistent")
    assert result == []


def test_scan_artifacts_with_files(tmp_path):
    (tmp_path / "file.md").write_text("hello")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")

    result = scan_artifacts(tmp_path)
    assert len(result) == 2

    paths = {a.relative_path for a in result}
    assert "file.md" in paths
    assert "image.png" in paths

    for a in result:
        assert a.size_bytes > 0
        assert a.modified_at.isdigit()


def test_scan_artifacts_nested(tmp_path):
    subdir = tmp_path / "images"
    subdir.mkdir()
    (subdir / "hero.png").write_bytes(b"\x89PNG")

    result = scan_artifacts(tmp_path)
    assert len(result) == 1
    assert result[0].relative_path == "images/hero.png"


def test_diff_artifacts_new():
    prev = []
    curr = [ArtifactRecord("new.md", 100, "1700000001", "document")]

    diff = diff_artifacts(prev, curr)
    assert len(diff) == 1
    assert diff[0].relative_path == "new.md"


def test_diff_artifacts_modified():
    prev = [ArtifactRecord("file.md", 100, "1700000000", "document")]
    curr = [ArtifactRecord("file.md", 200, "1700000001", "document")]

    diff = diff_artifacts(prev, curr)
    assert len(diff) == 1


def test_diff_artifacts_unchanged():
    artifact = ArtifactRecord("file.md", 100, "1700000000", "document")
    prev = [artifact]
    curr = [artifact]

    diff = diff_artifacts(prev, curr)
    assert len(diff) == 0


def test_diff_artifacts_mixed():
    prev = [
        ArtifactRecord("unchanged.md", 100, "1700000000", "document"),
        ArtifactRecord("modified.md", 100, "1700000000", "document"),
    ]
    curr = [
        ArtifactRecord("unchanged.md", 100, "1700000000", "document"),
        ArtifactRecord("modified.md", 200, "1700000001", "document"),
        ArtifactRecord("new.png", 500, "1700000002", "image"),
    ]

    diff = diff_artifacts(prev, curr)
    assert len(diff) == 2
    paths = {a.relative_path for a in diff}
    assert "modified.md" in paths
    assert "new.png" in paths
