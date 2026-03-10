from __future__ import annotations

import argparse
from pathlib import Path

from scripts.amazon_config import AmazonScraperConfig
from scripts.scrape_amazon_product import find_chrome_executable
from scripts.amazon_session import (
    ensure_session_paths,
    has_marketplace_cookies,
    marketplace_home_url,
)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional at runtime
    load_dotenv = None

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise SystemExit(
        "Playwright is not installed. Run `pip install -r scripts/requirements.txt` "
        "and `playwright install chromium` first."
    ) from exc


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    if load_dotenv is not None:
        load_dotenv(project_root / ".env")

    parser = argparse.ArgumentParser(description="Open Amazon in a browser and save a logged-in session")
    parser.add_argument("--url", type=str, default=None, help="Optional Amazon URL to open for login/session establishment")
    args = parser.parse_args()

    config = AmazonScraperConfig.from_project_root(project_root)
    ensure_session_paths(config.profile_dir, config.storage_state_path)
    target_url = args.url or marketplace_home_url(config.marketplace)

    with sync_playwright() as playwright:
        launch_kwargs = {
            "user_data_dir": str(config.profile_dir),
            "headless": False,
        }
        chrome_executable = find_chrome_executable()
        if chrome_executable is not None:
            launch_kwargs["executable_path"] = str(chrome_executable)
        context = playwright.chromium.launch_persistent_context(**launch_kwargs)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(target_url, wait_until="domcontentloaded")

        print("Log in to Amazon in the opened browser window and complete any MFA prompt.")
        print(f"Opened URL: {target_url}")
        input("Press Enter here after login finishes...")

        storage_state = context.storage_state()
        if not has_marketplace_cookies(storage_state, config.marketplace):
            context.close()
            raise SystemExit(
                "No Amazon session cookies were detected. Confirm login completed and retry."
            )

        context.storage_state(path=str(config.storage_state_path))
        context.close()

    print(f"Saved Amazon session to {config.storage_state_path}")
    print(f"Persistent browser profile directory: {config.profile_dir}")


if __name__ == "__main__":
    main()
