from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

from scripts.amazon_config import AmazonScraperConfig, ReviewFilterConfig
from scripts.amazon_parser import parse_product_page, parse_reviews_page, build_filtered_reviews_url
from scripts.amazon_session import (
    apply_stealth,
    marketplace_home_url,
    simulate_human_behavior,
)

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})")
CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
]


def save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "amazon-product"


def extract_asin(value: str) -> str | None:
    if re.fullmatch(r"[A-Z0-9]{10}", value):
        return value
    match = ASIN_RE.search(value)
    return match.group(1) if match else None


def build_product_url(asin: str, marketplace: str) -> str:
    return f"{marketplace_home_url(marketplace)}/dp/{asin}"


def find_chrome_executable() -> Path | None:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def should_use_persistent_profile(profile_dir: Path) -> bool:
    if not profile_dir.exists():
        return False
    return any(profile_dir.iterdir())


def write_scrape_output(output_dir: Path, product: dict, reviews: list[dict], meta: dict, raw_pages: dict[str, str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    save_json(output_dir / "product.json", product)
    save_json(output_dir / "reviews.json", reviews)
    save_json(output_dir / "meta.json", meta)
    for name, html in raw_pages.items():
        (raw_dir / name).write_text(html, encoding="utf-8")


def save_failure_artifacts(debug_dir: Path, html: str, screenshot_bytes: bytes) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "last_error.html").write_text(html, encoding="utf-8")
    (debug_dir / "last_error.png").write_bytes(screenshot_bytes)


def is_blocked_page(html: str) -> bool:
    lowered = html.lower()
    blocked_markers = [
        "enter the characters you see below",
        "sorry, we just need to make sure you're not a robot",
        "type the characters you see in this image",
        "to discuss automated access to amazon data",
    ]
    return any(marker in lowered for marker in blocked_markers)


def is_sign_in_page(html: str) -> bool:
    """Detect if this is an actual Amazon sign-in page (not just a normal page with sign-in links).

    Normal Amazon pages contain 'ap/signin' in the nav tooltip and 'sign in'/'password'
    in various scripts/tooltips. The real sign-in page has specific form elements.
    """
    lowered = html.lower()
    # The actual sign-in page has the authportal form wrapper
    sign_in_form_markers = [
        'id="authportal',
        'name="signIn"',          # the sign-in form name attribute
        'id="ap_email"',           # email input field on sign-in page
        "action=\"/ap/signin",     # form action pointing to sign-in endpoint
    ]
    return any(marker in lowered for marker in sign_in_form_markers)


def _build_page_url(base_url: str, page_number: int) -> str:
    """Build a reviews URL for a specific page number by setting/replacing the pageNumber param."""
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params["pageNumber"] = [str(page_number)]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def resolve_output_dir(project_root: Path, output_arg: str | None, product: dict, asin: str) -> Path:
    if output_arg:
        return Path(output_arg)
    name = product.get("title") or asin
    return project_root / "output" / slugify(name) / "amazon"


def _load_progress(progress_path: Path) -> dict:
    """Load incremental scrape progress from disk."""
    if progress_path.exists():
        try:
            return json.loads(progress_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_completed_page": 0, "reviews": [], "seen_ids": []}


def _save_progress(progress_path: Path, page_num: int, reviews: list[dict], seen_ids: set[str]) -> None:
    """Save incremental progress after each successful page."""
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress = {
        "last_completed_page": page_num,
        "reviews": reviews,
        "seen_ids": list(seen_ids),
    }
    progress_path.write_text(json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8")


def _navigate_with_retry(page, url: str, config: AmazonScraperConfig, context_factory=None) -> str:
    """Navigate to a URL with retry logic on CAPTCHA/blocks.

    Returns the page HTML on success.
    Raises SystemExit after exhausting all retries.
    """
    delays = config.delays

    for attempt in range(delays.max_retries):
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(int(delays.initial_load_delay * 1000))

        html = page.content()

        if not is_blocked_page(html) and not is_sign_in_page(html):
            return html

        if attempt < delays.max_retries - 1:
            wait = delays.backoff_delay(attempt)
            logger.warning(
                "Blocked on attempt %d/%d — waiting %.1fs before retry",
                attempt + 1, delays.max_retries, wait,
            )
            page.wait_for_timeout(int(wait * 1000))

    # All retries exhausted
    return html


def scrape_product(
    url: str | None,
    asin: str | None,
    max_review_pages: int,
    save_html: bool,
    headed: bool,
    output_arg: str | None,
    star_rating: str | None = None,
    verified_only: bool = False,
    sort_by: str = "recent",
    resume: bool = True,
) -> Path:
    if sync_playwright is None:  # pragma: no cover
        raise SystemExit(
            "Playwright is not installed. Run `pip install -r scripts/requirements.txt` and `playwright install chromium`."
        )

    project_root = Path(__file__).resolve().parent.parent
    if load_dotenv is not None:
        load_dotenv(project_root / ".env")
    config = AmazonScraperConfig.from_project_root(project_root)
    config = AmazonScraperConfig(
        profile_dir=config.profile_dir,
        storage_state_path=config.storage_state_path,
        marketplace=config.marketplace,
        headless=config.headless if not headed else False,
        proxy=config.proxy,
        delays=config.delays,
        filters=ReviewFilterConfig(
            star_rating=star_rating,
            verified_only=verified_only,
            sort_by=sort_by,
        ),
    )

    target_asin = extract_asin(asin or "") or extract_asin(url or "")
    if not target_asin:
        raise SystemExit("Provide --asin or a product --url containing an ASIN.")
    product_url = url or build_product_url(target_asin, config.marketplace)

    with sync_playwright() as playwright:
        # Build launch kwargs with anti-detection features
        viewport = config.random_viewport()
        user_agent = config.random_user_agent()

        launch_kwargs: dict = {"headless": config.headless if not headed else False}
        chrome_executable = find_chrome_executable()
        if chrome_executable is not None:
            launch_kwargs["executable_path"] = str(chrome_executable)

        # Add proxy if configured
        proxy_dict = config.proxy.to_playwright_proxy()
        if proxy_dict:
            launch_kwargs["proxy"] = proxy_dict
            logger.info("Using proxy: %s", config.proxy.server)

        browser = None
        if should_use_persistent_profile(config.profile_dir):
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(config.profile_dir),
                viewport=viewport,
                user_agent=user_agent,
                **launch_kwargs,
            )
            session_mode = "persistent_profile"
        else:
            browser = playwright.chromium.launch(**launch_kwargs)
            context_kwargs: dict = {
                "viewport": viewport,
                "user_agent": user_agent,
            }
            if config.storage_state_path.exists():
                context_kwargs["storage_state"] = str(config.storage_state_path)
                session_mode = "storage_state"
            else:
                session_mode = "anonymous"
            context = browser.new_context(**context_kwargs)

        page = context.new_page()

        # Apply stealth to mask automation fingerprints
        apply_stealth(page)

        raw_pages: dict[str, str] = {}
        warnings: list[str] = []

        # --- Product page ---
        product_html = _navigate_with_retry(page, product_url, config)
        if is_blocked_page(product_html) or is_sign_in_page(product_html):
            debug_dir = resolve_output_dir(project_root, output_arg, {"title": target_asin}, target_asin) / "debug"
            save_failure_artifacts(debug_dir, product_html, page.screenshot(full_page=True))
            context.close()
            if browser:
                browser.close()
            raise SystemExit(
                f"Amazon returned a sign-in or CAPTCHA page on the product URL after {config.delays.max_retries} attempts. "
                f"Debug artifacts saved to {debug_dir}"
            )

        # Simulate human behavior before parsing
        simulate_human_behavior(page)

        if save_html:
            raw_pages["product.html"] = product_html

        product = parse_product_page(product_html, page.url)
        asin_from_page = product.get("asin") or target_asin

        # Build filtered reviews URL (base URL used for explicit pageNumber construction)
        marketplace_url = marketplace_home_url(config.marketplace)
        reviews_base_url = build_filtered_reviews_url(
            marketplace_url,
            asin_from_page,
            star_rating=config.filters.star_rating,
            verified_only=config.filters.verified_only,
            sort_by=config.filters.sort_by,
        )
        reviews_url = reviews_base_url

        # --- Review pages with incremental save and resume ---
        output_dir = resolve_output_dir(project_root, output_arg, product, asin_from_page)
        progress_path = output_dir / ".scrape_progress.json"

        # Resume from previous progress if available
        all_reviews: list[dict] = []
        seen_ids: set[str] = set()
        start_page = 1

        if resume:
            progress = _load_progress(progress_path)
            if progress["last_completed_page"] > 0:
                all_reviews = progress["reviews"]
                seen_ids = set(progress["seen_ids"])
                start_page = progress["last_completed_page"] + 1
                logger.info(
                    "Resuming from page %d with %d reviews already collected",
                    start_page, len(all_reviews),
                )

        review_page = start_page
        consecutive_empty = 0
        was_blocked = False

        while review_page <= max_review_pages and reviews_url:
            # Smart delay between pages (skip for first page)
            if review_page > start_page:
                delay = config.delays.page_delay()
                logger.debug("Waiting %.1fs before page %d", delay, review_page)
                page.wait_for_timeout(int(delay * 1000))

            html = _navigate_with_retry(page, reviews_url, config)

            if is_blocked_page(html) or is_sign_in_page(html):
                debug_dir = output_dir / "debug"
                save_failure_artifacts(debug_dir, html, page.screenshot(full_page=True))
                # Save progress so we can resume later
                _save_progress(progress_path, review_page - 1, all_reviews, seen_ids)
                warnings.append(f"Blocked on review page {review_page} — progress saved for resume")
                logger.warning(
                    "Blocked on review page %d after retries. Progress saved (%d reviews). "
                    "Re-run to resume from page %d.",
                    review_page, len(all_reviews), review_page,
                )
                was_blocked = True
                break

            # Simulate human behavior on review pages too
            simulate_human_behavior(page)

            if save_html:
                raw_pages[f"reviews_page_{review_page:03d}.html"] = html

            parsed = parse_reviews_page(html)
            warnings.extend(parsed["warnings"])

            if not parsed["reviews"]:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    break
                # Retry once with a longer delay for empty pages
                page.wait_for_timeout(int(config.delays.backoff_delay(0) * 1000))
                continue

            consecutive_empty = 0

            new_on_page = 0
            for review in parsed["reviews"]:
                review_id = review.get("review_id")
                if not review_id or review_id in seen_ids:
                    continue
                seen_ids.add(review_id)
                all_reviews.append(review)
                new_on_page += 1

            # Save progress incrementally after each successful page
            _save_progress(progress_path, review_page, all_reviews, seen_ids)

            # Stop if this page yielded zero new reviews (all duplicates = we've looped)
            if new_on_page == 0:
                logger.info("Page %d had no new reviews (all duplicates) — stopping", review_page)
                break

            # Check if there's a next page link at all
            if not parsed["next_page_url"]:
                break

            # Build next page URL explicitly by incrementing pageNumber
            # (Amazon's parsed next_page_url can be stale/incorrect)
            review_page += 1
            reviews_url = _build_page_url(reviews_base_url, review_page)

        # --- Write final output ---
        meta = {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "input_url": product_url,
            "asin": asin_from_page,
            "marketplace": config.marketplace,
            "total_review_pages_fetched": review_page - 1 if review_page > start_page else start_page - 1,
            "total_reviews": len(all_reviews),
            "filters": {
                "star_rating": config.filters.star_rating,
                "verified_only": config.filters.verified_only,
                "sort_by": config.filters.sort_by,
            },
            "parser_warnings": warnings,
            "session_mode": session_mode,
            "proxy_used": config.proxy.enabled,
        }
        write_scrape_output(output_dir, product, all_reviews, meta, raw_pages)

        # Clean up progress file on successful completion (keep it if we were blocked mid-scrape)
        if progress_path.exists() and not was_blocked:
            progress_path.unlink(missing_ok=True)

        context.close()
        if browser is not None:
            browser.close()
        return output_dir


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Scrape an Amazon product page and its reviews")
    parser.add_argument("--url", type=str, default=None, help="Amazon product URL")
    parser.add_argument("--asin", type=str, default=None, help="Amazon ASIN")
    parser.add_argument("--max-review-pages", type=int, default=500, help="Maximum review pages to fetch")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    parser.add_argument("--save-html", action="store_true", help="Save raw HTML pages alongside JSON output")
    parser.add_argument("--output-dir", type=str, default=None, help="Explicit output directory")
    parser.add_argument(
        "--star-rating",
        type=str,
        default=None,
        choices=["1", "2", "3", "4", "5"],
        help="Filter reviews by star rating",
    )
    parser.add_argument("--verified-only", action="store_true", help="Only scrape verified purchase reviews")
    parser.add_argument(
        "--sort-by",
        type=str,
        default="recent",
        choices=["recent", "helpful", "top"],
        help="Sort order for reviews",
    )
    parser.add_argument("--no-resume", action="store_true", help="Start fresh instead of resuming from previous progress")
    args = parser.parse_args()

    output_dir = scrape_product(
        url=args.url,
        asin=args.asin,
        max_review_pages=args.max_review_pages,
        save_html=args.save_html,
        headed=args.headed,
        output_arg=args.output_dir,
        star_rating=args.star_rating,
        verified_only=args.verified_only,
        sort_by=args.sort_by,
        resume=not args.no_resume,
    )
    print(f"Saved scrape output to {output_dir}")


if __name__ == "__main__":
    main()
