"""File discovery, classification, and diff detection for pipeline outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactRecord:
    relative_path: str
    size_bytes: int
    modified_at: str  # Unix timestamp as string
    kind: str


def classify_artifact(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "html"
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"
    if suffix in {".md", ".js", ".json", ".txt"}:
        return "document"
    return "other"


def scan_artifacts(run_dir: Path) -> list[ArtifactRecord]:
    """Recursively find all files in run_dir and return ArtifactRecords."""
    if not run_dir.exists():
        return []

    artifacts = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        stat = path.stat()
        artifacts.append(
            ArtifactRecord(
                relative_path=str(path.relative_to(run_dir)),
                size_bytes=stat.st_size,
                modified_at=str(int(stat.st_mtime)),
                kind=classify_artifact(path),
            )
        )
    return artifacts


def diff_artifacts(
    previous: list[ArtifactRecord],
    current: list[ArtifactRecord],
) -> list[ArtifactRecord]:
    """Return artifacts that are new or modified since the previous scan."""
    prev_map: dict[str, ArtifactRecord] = {
        a.relative_path: a for a in previous
    }
    new_or_modified: list[ArtifactRecord] = []
    for artifact in current:
        prev = prev_map.get(artifact.relative_path)
        if prev is None:
            new_or_modified.append(artifact)
        elif (
            artifact.modified_at != prev.modified_at
            or artifact.size_bytes != prev.size_bytes
        ):
            new_or_modified.append(artifact)
    return new_or_modified
