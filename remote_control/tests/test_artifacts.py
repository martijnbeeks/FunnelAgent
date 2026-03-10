from remote_control.app.artifacts import scan_artifacts


def test_scan_artifacts_finds_html_and_images(tmp_path):
    run_dir = tmp_path / "demo"
    run_dir.mkdir()
    (run_dir / "advertorial.html").write_text("<html></html>")
    (run_dir / "logo.png").write_bytes(b"png")

    artifacts = scan_artifacts(run_dir)

    assert {item.kind for item in artifacts} == {"html", "image"}

