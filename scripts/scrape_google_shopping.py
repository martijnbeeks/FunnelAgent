from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from scripts.google_shopping_config import GoogleShoppingConfig
from scripts.google_shopping_parser import parse_product_panel, parse_panel_reviews

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

try:
    from playwright_stealth import stealth_sync
except ImportError:  # pragma: no cover
    stealth_sync = None


CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
]

BLOCK_MARKERS = [
    "unusual traffic from your computer",
    "our systems have detected unusual traffic",
    "sorry, we just need to make sure you're not a robot",
]

CONSENT_MARKERS = [
    "before you continue to google",
    "consent.google.com",
]


def save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "google-product"


def find_chrome_executable() -> Path | None:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def is_blocked_page(html: str) -> bool:
    lowered = html.lower()
    return any(marker in lowered for marker in BLOCK_MARKERS)


def is_consent_page(html: str) -> bool:
    lowered = html.lower()
    return any(marker in lowered for marker in CONSENT_MARKERS)


def save_debug_artifacts(debug_dir: Path, html: str, screenshot_bytes: bytes, label: str = "error") -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"{label}.html").write_text(html, encoding="utf-8")
    (debug_dir / f"{label}.png").write_bytes(screenshot_bytes)


def random_delay(page, base_ms: int) -> None:
    jitter = random.randint(0, base_ms)
    page.wait_for_timeout(base_ms + jitter)


def human_scroll(page) -> None:
    viewport_height = page.viewport_size.get("height", 800) if page.viewport_size else 800
    scroll_amount = random.randint(int(viewport_height * 0.3), int(viewport_height * 0.7))
    page.mouse.wheel(0, scroll_amount)
    page.wait_for_timeout(random.randint(300, 800))


def handle_consent(page) -> bool:
    html = page.content()
    if not is_consent_page(html):
        return False
    print("  Handling Google cookie consent...")
    accept_selectors = [
        'button:has-text("Accept all")',
        'button:has-text("Reject all")',
        'button:has-text("Alles accepteren")',
        'button:has-text("Alles afwijzen")',
        'button:has-text("Alle akzeptieren")',
        'button:has-text("Tout accepter")',
        '#L2AGLb',
        'button[aria-label="Accept all"]',
        'form[action*="consent"] button',
    ]
    for selector in accept_selectors:
        try:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                btn.click()
                page.wait_for_timeout(2000)
                print("  Consent accepted.")
                return True
        except Exception:
            continue
    return False


def click_expand_buttons(page) -> None:
    """Click all 'More' buttons in the review panel to expand truncated text."""
    # The overlay panel shows "More" links to expand each review
    expand_selectors = [
        'div.mLFOe a:has-text("More")',
        'div.zzkrfd a:has-text("More")',
        'a:has-text("More")',
    ]
    for selector in expand_selectors:
        buttons = page.query_selector_all(selector)
        for button in buttons:
            try:
                text = button.inner_text().strip()
                # Only click "More" buttons, not "More reviews"
                if text == "More":
                    button.click()
                    page.wait_for_timeout(random.randint(200, 400))
            except Exception:
                pass


def review_dedup_key(review: dict) -> str:
    parts = [
        review.get("reviewer") or "",
        review.get("date") or "",
        review.get("text") or "",
    ]
    raw = "|".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()


def resolve_output_dir(project_root: Path, output_arg: str | None, product: dict, query: str | None) -> Path:
    if output_arg:
        return Path(output_arg)
    name = product.get("title") or query or "google-product"
    return project_root / "output" / slugify(name) / "google-shopping"


def warmup_session(page, config: GoogleShoppingConfig) -> None:
    print("Warming up session on google.com ...")
    page.goto(
        f"https://www.google.com/?hl={config.locale}&gl={config.country}",
        wait_until="domcontentloaded",
        timeout=config.timeout_ms,
    )
    random_delay(page, 2000)
    handle_consent(page)
    random_delay(page, 1000)


def navigate_to_shopping_search(page, query: str, config: GoogleShoppingConfig) -> bool:
    """Navigate to Google Shopping search results. Returns False if blocked."""
    search_url = (
        f"https://www.google.com/search?tbm=shop"
        f"&q={quote_plus(query)}"
        f"&hl={config.locale}"
        f"&gl={config.country}"
    )
    page.goto(search_url, wait_until="domcontentloaded", timeout=config.timeout_ms)
    random_delay(page, config.delay_ms)
    handle_consent(page)
    human_scroll(page)
    page.wait_for_timeout(2000)
    return not is_blocked_page(page.content())


def find_product_cards(page) -> list:
    """Find clickable product cards on the Google Shopping search results page."""
    card_selectors = [
        "div.UC8ZCe",           # clickable card with jsaction
        "g-inner-card.ExWXFf",  # outer card wrapper with jscontroller
        "div.PhALMc",           # inner card container
        "div.rRCm8",            # card row container
    ]
    for selector in card_selectors:
        cards = page.query_selector_all(selector)
        if len(cards) > 1:
            return cards

    # Fallback: g-inner-card elements that contain a price
    all_inner_cards = page.query_selector_all("g-inner-card")
    return [c for c in all_inner_cards if c.query_selector("span.lmQWe")]


def click_product_card(page, card, config: GoogleShoppingConfig) -> bool:
    """Click a product card and wait for the overlay panel to load.

    Returns True if the panel appeared successfully.
    """
    try:
        card.click()
        # Wait for the product detail panel to load
        page.wait_for_timeout(3000)

        # Verify the panel loaded by checking for the panel container
        panel = page.query_selector("div.mLFOe, [jsname='kefP3d'], div.zzkrfd")
        if panel:
            # Scroll within the panel to trigger lazy-loading of reviews
            page.wait_for_timeout(1000)
            return True

        return False
    except Exception:
        return False


def load_more_reviews(page, config: GoogleShoppingConfig) -> int:
    """Click 'More reviews' button to load additional reviews. Returns number of clicks."""
    clicks = 0
    for _ in range(config.max_review_pages):
        more_btn = page.query_selector(
            'div.mLFOe a:has-text("More reviews"), '
            'div.zzkrfd a:has-text("More reviews"), '
            '[jsname="UtT7xe"] a:has-text("More reviews")'
        )
        if not more_btn:
            break
        try:
            more_btn.click()
            random_delay(page, config.delay_ms)
            clicks += 1
        except Exception:
            break
    return clicks


def scrape_from_query(
    query: str,
    headed: bool,
    save_html: bool,
    output_arg: str | None,
    max_results: int,
) -> Path:
    if sync_playwright is None:
        raise SystemExit(
            "Playwright is not installed. Run `pip install -r scripts/requirements.txt` and `playwright install chromium`."
        )

    project_root = Path(__file__).resolve().parent.parent
    if load_dotenv is not None:
        load_dotenv(project_root / ".env")

    config = GoogleShoppingConfig.from_env(project_root)
    effective_headless = config.headless if not headed else False

    with sync_playwright() as playwright:
        profile_dir = Path(config.profile_dir)
        profile_dir.mkdir(parents=True, exist_ok=True)

        launch_kwargs: dict = {
            "headless": effective_headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                f"--lang={config.locale}",
            ],
        }
        chrome_executable = find_chrome_executable()
        if chrome_executable is not None:
            launch_kwargs["executable_path"] = str(chrome_executable)
            print(f"Using system Chrome: {chrome_executable}")
        else:
            launch_kwargs["channel"] = "chromium"
            print("Using Playwright Chromium (system Chrome not found)")

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            viewport={"width": random.randint(1280, 1440), "height": random.randint(800, 900)},
            locale=config.locale,
            **launch_kwargs,
        )
        page = context.new_page()

        if config.stealth and stealth_sync is not None:
            stealth_sync(page)

        warmup_session(page, config)

        # Navigate to Google Shopping search
        print(f"Searching Google Shopping for: {query}")
        if not navigate_to_shopping_search(page, query, config):
            debug_dir = project_root / "output" / slugify(query) / "google-shopping" / "debug"
            save_debug_artifacts(debug_dir, page.content(), page.screenshot(full_page=True), "search_blocked")
            context.close()
            raise SystemExit("Google blocked the search request. Try --headed or wait and retry.")

        cards = find_product_cards(page)
        print(f"Found {len(cards)} product cards")

        if not cards:
            debug_dir = project_root / "output" / slugify(query) / "google-shopping" / "debug"
            save_debug_artifacts(debug_dir, page.content(), page.screenshot(full_page=True), "no_cards")
            context.close()
            raise SystemExit("No product cards found on search page. Check debug/ for screenshots.")

        last_output_dir = None

        for i in range(min(max_results, len(cards))):
            print(f"\n[{i + 1}/{min(max_results, len(cards))}] Clicking product card #{i + 1} ...")

            # Re-navigate to search page for each product (panel replaces previous)
            if i > 0:
                if not navigate_to_shopping_search(page, query, config):
                    print("  BLOCKED on re-search. Stopping.")
                    break
                cards = find_product_cards(page)
                if i >= len(cards):
                    print(f"  Only {len(cards)} cards found, stopping.")
                    break

            if not click_product_card(page, cards[i], config):
                print("  Panel did not load after clicking card. Skipping.")
                continue

            # Expand truncated review text
            click_expand_buttons(page)

            # Load more reviews if available
            more_clicks = load_more_reviews(page, config)
            if more_clicks:
                # Expand newly loaded reviews too
                click_expand_buttons(page)

            # Parse the overlay panel
            panel_html = page.content()
            raw_pages: dict[str, str] = {}
            if save_html:
                raw_pages["panel.html"] = panel_html

            product = parse_product_panel(panel_html)
            product["url"] = page.url
            product["query"] = query

            print(f"  Product: {product.get('title', 'Unknown')}")
            print(f"  Rating: {product.get('average_rating', 'N/A')} ({product.get('total_reviews', 'N/A')} reviews)")
            print(f"  Price range: {product.get('price_range', 'N/A')}")
            print(f"  Merchants: {len(product.get('merchants', []))}")

            # Parse reviews from the panel
            review_data = parse_panel_reviews(panel_html)
            all_reviews = review_data["reviews"]
            warnings = review_data["warnings"]

            # Deduplicate reviews
            seen_keys: set[str] = set()
            deduped_reviews: list[dict] = []
            for review in all_reviews:
                key = review_dedup_key(review)
                if key not in seen_keys:
                    seen_keys.add(key)
                    deduped_reviews.append(review)

            print(f"  Scraped {len(deduped_reviews)} reviews")
            if more_clicks:
                print(f"  Loaded {more_clicks} additional review pages")
            if warnings:
                print(f"  Warnings: {warnings}")

            # Save output
            output_dir = resolve_output_dir(project_root, output_arg, product, query)
            output_dir.mkdir(parents=True, exist_ok=True)

            save_json(output_dir / "product.json", product)
            save_json(output_dir / "reviews.json", deduped_reviews)
            save_json(output_dir / "meta.json", {
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "query": query,
                "locale": config.locale,
                "country": config.country,
                "total_reviews_scraped": len(deduped_reviews),
                "review_pages_loaded": 1 + more_clicks,
                "warnings": warnings,
                "stealth_enabled": config.stealth and stealth_sync is not None,
            })

            if save_html:
                raw_dir = output_dir / "raw"
                raw_dir.mkdir(parents=True, exist_ok=True)
                for name, html_content in raw_pages.items():
                    (raw_dir / name).write_text(html_content, encoding="utf-8")

            last_output_dir = output_dir

            if i < min(max_results, len(cards)) - 1:
                random_delay(page, config.delay_ms * 2)

        context.close()

    if last_output_dir is None:
        raise SystemExit("No products were successfully scraped.")

    return last_output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Google Shopping product reviews")
    parser.add_argument("--query", type=str, required=True, help="Search query to find products")
    parser.add_argument("--max-results", type=int, default=1, help="Max products to scrape from search (default: 1)")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed (visible) mode")
    parser.add_argument("--save-html", action="store_true", help="Save raw HTML alongside JSON output")
    parser.add_argument("--output-dir", type=str, default=None, help="Explicit output directory")
    args = parser.parse_args()

    output_dir = scrape_from_query(
        query=args.query,
        headed=args.headed,
        save_html=args.save_html,
        output_arg=args.output_dir,
        max_results=args.max_results,
    )
    print(f"\nSaved scrape output to {output_dir}")


if __name__ == "__main__":
    main()
