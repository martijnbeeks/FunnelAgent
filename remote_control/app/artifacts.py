from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactRecord:
    relative_path: str
    size_bytes: int
    modified_at: str
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
