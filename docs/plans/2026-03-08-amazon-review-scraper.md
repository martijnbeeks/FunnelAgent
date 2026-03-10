# Amazon Review Scraper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a first-party Amazon product scraper that reuses a logged-in browser session and exports complete product metadata plus all reachable review pages for a single product into structured files under `output/`.

**Architecture:** Use Playwright with a persistent browser profile so login and MFA are handled manually once and then reused. Keep navigation in one CLI script, keep HTML-to-JSON parsing in a small pure parser module, and save both normalized data and raw debug artifacts so DOM changes are easy to diagnose. Leave the existing Apify-based scraper intact as the low-effort fallback; this plan adds an owned scraping path rather than replacing the current integration.

**Tech Stack:** Python 3.11+, `playwright`, `beautifulsoup4`, `pytest`, `python-dotenv`, existing repo `output/` layout, existing `scripts/requirements.txt`.

## Recommended Approach

Use the simplest durable shape:

- One manual login bootstrap command
- One scraper CLI for one ASIN or product URL
- One pure parser module for product and review HTML
- One output folder per product under `output/<slug>/amazon/`
- One small set of fixture-based parser tests

Do not add in v1:

- automatic username/password submission
- CAPTCHA-solving services
- stealth browser plugins
- distributed crawling
- a database
- concurrency across products

Manual login is the right tradeoff for v1. It avoids storing Amazon credentials in code or `.env`, handles MFA naturally, and keeps the scraper maintainable.

## Scope Assumptions

Assume "retrieve everything" means:

- product title
- brand
- ASIN
- canonical URL
- price if present
- average rating
- ratings count
- ratings histogram
- key bullets / description text visible on page
- image URLs visible on the product page
- all reachable review pages
- per-review fields: id, title, rating, date, author name, verified flag, helpful count, variant/format text, body, media thumbnails

Non-goals for v1:

- seller offers / buy box monitoring
- question-and-answer scraping
- review replies from brands
- geo-specific delivery or stock simulation
- anti-bot bypass beyond normal headed browsing and slow page transitions

## Output Contract

Write results to:

- `output/<product-slug>/amazon/product.json`
- `output/<product-slug>/amazon/reviews.json`
- `output/<product-slug>/amazon/meta.json`
- `output/<product-slug>/amazon/raw/product.html`
- `output/<product-slug>/amazon/raw/reviews_page_001.html`
- `output/<product-slug>/amazon/raw/reviews_page_002.html`
- `output/<product-slug>/amazon/debug/last_error.html`
- `output/<product-slug>/amazon/debug/last_error.png`

`meta.json` should include:

- scrape timestamp
- input URL / ASIN
- marketplace
- total review pages fetched
- total reviews parsed
- parser warnings
- session mode used (`persistent_profile` or `storage_state`)

## Files To Create

### Task 1: Add dependencies and scraper configuration

**Files:**
- Modify: `scripts/requirements.txt`
- Modify: `.env.example`
- Create: `scripts/amazon_config.py`
- Create: `tests/test_amazon_config.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from scripts.amazon_config import AmazonScraperConfig


def test_config_uses_repo_relative_defaults(tmp_path, monkeypatch):
    monkeypatch.delenv("AMAZON_PROFILE_DIR", raising=False)
    monkeypatch.delenv("AMAZON_STORAGE_STATE_PATH", raising=False)

    config = AmazonScraperConfig.from_project_root(tmp_path)

    assert config.profile_dir == tmp_path / ".amazon-profile"
    assert config.storage_state_path == tmp_path / ".amazon-storage-state.json"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_amazon_config.py -v`
Expected: FAIL because `AmazonScraperConfig` does not exist.

**Step 3: Write minimal implementation**

- Add `playwright>=1.54.0`
- Add `beautifulsoup4>=4.13.0`
- Keep everything else unchanged
- Add `AmazonScraperConfig.from_project_root()` that resolves:
  - `AMAZON_PROFILE_DIR`
  - `AMAZON_STORAGE_STATE_PATH`
  - `AMAZON_MARKETPLACE`
  - `AMAZON_HEADLESS`

```python
@dataclass
class AmazonScraperConfig:
    profile_dir: Path
    storage_state_path: Path
    marketplace: str
    headless: bool
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_amazon_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/requirements.txt .env.example scripts/amazon_config.py tests/test_amazon_config.py
git commit -m "feat: add amazon scraper config"
```

### Task 2: Add manual login bootstrap with persistent session reuse

**Files:**
- Create: `scripts/amazon_login.py`
- Create: `scripts/amazon_session.py`
- Create: `tests/test_amazon_session.py`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
from pathlib import Path

from scripts.amazon_session import ensure_session_paths


def test_ensure_session_paths_creates_parent_dirs(tmp_path):
    profile_dir = tmp_path / ".amazon-profile"
    storage_state = tmp_path / ".state" / "amazon.json"

    ensure_session_paths(profile_dir, storage_state)

    assert profile_dir.exists()
    assert storage_state.parent.exists()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_amazon_session.py -v`
Expected: FAIL because session helpers do not exist.

**Step 3: Write minimal implementation**

- `amazon_login.py` launches Chromium in headed mode
- Open the Amazon marketplace home page
- Print instructions telling the user to log in manually and complete MFA
- Wait for the user to press Enter in the terminal
- Save Playwright storage state to the configured path
- Reuse the persistent profile directory for future runs

```python
def ensure_session_paths(profile_dir: Path, storage_state_path: Path) -> None:
    profile_dir.mkdir(parents=True, exist_ok=True)
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)
```

Important:

- Do not read `AMAZON_EMAIL` or `AMAZON_PASSWORD`
- Do not script MFA
- Fail with a clear message if login does not complete

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_amazon_session.py -v`
Expected: PASS

**Step 5: Smoke test the login bootstrap**

Run: `python scripts/amazon_login.py`
Expected: A visible browser opens, you log in manually, and storage state is saved locally.

**Step 6: Commit**

```bash
git add scripts/amazon_login.py scripts/amazon_session.py tests/test_amazon_session.py README.md
git commit -m "feat: add amazon login bootstrap"
```

### Task 3: Add pure product-page parsing

**Files:**
- Create: `scripts/amazon_parser.py`
- Create: `tests/fixtures/amazon/product_page_minimal.html`
- Create: `tests/test_amazon_product_parser.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from scripts.amazon_parser import parse_product_page


def test_parse_product_page_extracts_core_fields():
    html = Path("tests/fixtures/amazon/product_page_minimal.html").read_text(encoding="utf-8")

    data = parse_product_page(html, "https://www.amazon.com/dp/B000TEST01")

    assert data["asin"] == "B000TEST01"
    assert data["title"] == "Test Product"
    assert data["average_rating"] == 4.4
    assert data["ratings_count"] == 1234
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_amazon_product_parser.py -v`
Expected: FAIL because `parse_product_page` does not exist.

**Step 3: Write minimal implementation**

- Parse with `BeautifulSoup`
- Support selector fallbacks for:
  - `#productTitle`
  - `#acrPopover`
  - `#acrCustomerReviewText`
  - `#feature-bullets`
  - ratings histogram table
  - image data in product gallery markup
- Extract ASIN from canonical URL first, then fall back to detail tables

```python
def parse_product_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("#productTitle")
    return {
        "asin": extract_asin(url, soup),
        "title": title.get_text(" ", strip=True) if title else None,
    }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_amazon_product_parser.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/amazon_parser.py tests/fixtures/amazon/product_page_minimal.html tests/test_amazon_product_parser.py
git commit -m "feat: parse amazon product pages"
```

### Task 4: Add review-page parsing and pagination extraction

**Files:**
- Modify: `scripts/amazon_parser.py`
- Create: `tests/fixtures/amazon/reviews_page_minimal.html`
- Create: `tests/test_amazon_review_parser.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from scripts.amazon_parser import parse_reviews_page


def test_parse_reviews_page_extracts_reviews_and_next_link():
    html = Path("tests/fixtures/amazon/reviews_page_minimal.html").read_text(encoding="utf-8")

    data = parse_reviews_page(html)

    assert len(data["reviews"]) == 2
    assert data["reviews"][0]["review_id"] == "RTEST123"
    assert data["reviews"][0]["verified"] is True
    assert data["next_page_url"].endswith("pageNumber=2")
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_amazon_review_parser.py -v`
Expected: FAIL because `parse_reviews_page` does not exist.

**Step 3: Write minimal implementation**

- Parse review containers using `[data-hook="review"]`
- Extract:
  - `review_id`
  - `author`
  - `rating`
  - `title`
  - `date`
  - `verified`
  - `helpful_count`
  - `body`
  - `format`
  - `media`
- Extract next-page URL from the pagination controls
- Return parser warnings instead of raising for single missing fields

```python
def parse_reviews_page(html: str) -> dict:
    return {
        "reviews": [],
        "next_page_url": None,
        "warnings": [],
    }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_amazon_review_parser.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/amazon_parser.py tests/fixtures/amazon/reviews_page_minimal.html tests/test_amazon_review_parser.py
git commit -m "feat: parse amazon review pages"
```

### Task 5: Add the authenticated scraper CLI

**Files:**
- Create: `scripts/scrape_amazon_product.py`
- Modify: `scripts/amazon_session.py`
- Modify: `scripts/amazon_parser.py`
- Create: `tests/test_amazon_output_writer.py`

**Step 1: Write the failing test**

```python
import json
from pathlib import Path

from scripts.scrape_amazon_product import write_scrape_output


def test_write_scrape_output_creates_expected_files(tmp_path):
    write_scrape_output(
        output_dir=tmp_path,
        product={"asin": "B000TEST01"},
        reviews=[{"review_id": "R1"}],
        meta={"total_reviews": 1},
        raw_pages={"product.html": "<html></html>"},
    )

    assert json.loads((tmp_path / "product.json").read_text())["asin"] == "B000TEST01"
    assert json.loads((tmp_path / "reviews.json").read_text())[0]["review_id"] == "R1"
    assert json.loads((tmp_path / "meta.json").read_text())["total_reviews"] == 1
    assert (tmp_path / "raw" / "product.html").exists()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_amazon_output_writer.py -v`
Expected: FAIL because `write_scrape_output` does not exist.

**Step 3: Write minimal implementation**

- CLI flags:
  - `--url`
  - `--asin`
  - `--marketplace`
  - `--max-review-pages`
  - `--headed`
  - `--save-html`
  - `--output-dir`
- Flow:
  1. open product page with saved session
  2. detect sign-in redirect or CAPTCHA
  3. collect product HTML
  4. open the "see all reviews" page
  5. paginate until no next page or `--max-review-pages`
  6. parse after each page
  7. de-duplicate reviews by `review_id`
  8. write normalized JSON plus raw HTML

```python
def write_scrape_output(output_dir, product, reviews, meta, raw_pages):
    output_dir.mkdir(parents=True, exist_ok=True)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_amazon_output_writer.py -v`
Expected: PASS

**Step 5: Run a real scrape smoke test**

Run: `python scripts/scrape_amazon_product.py --url https://www.amazon.com/dp/B006IB5T4W --max-review-pages 2 --save-html --headed`
Expected:

- Browser opens using the saved session
- Product metadata is saved
- Two review pages are fetched
- Files appear under `output/<product-slug>/amazon/`

**Step 6: Commit**

```bash
git add scripts/scrape_amazon_product.py scripts/amazon_session.py scripts/amazon_parser.py tests/test_amazon_output_writer.py
git commit -m "feat: add authenticated amazon product scraper"
```

### Task 6: Add failure diagnostics and recovery rules

**Files:**
- Modify: `scripts/scrape_amazon_product.py`
- Create: `tests/test_amazon_failure_modes.py`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
from pathlib import Path

from scripts.scrape_amazon_product import save_failure_artifacts


def test_save_failure_artifacts_writes_html_and_png(tmp_path):
    save_failure_artifacts(tmp_path, "<html>captcha</html>", b"png-bytes")
    assert (tmp_path / "last_error.html").exists()
    assert (tmp_path / "last_error.png").exists()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_amazon_failure_modes.py -v`
Expected: FAIL because failure artifact helpers do not exist.

**Step 3: Write minimal implementation**

- On sign-in redirect, CAPTCHA, empty review page, or parse failure:
  - save HTML
  - save screenshot
  - stop with a readable error
- Add README usage notes:
  - run `python scripts/amazon_login.py` first
  - use headed mode for troubleshooting
  - re-run login if session expires

```python
def save_failure_artifacts(debug_dir: Path, html: str, screenshot_bytes: bytes) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_amazon_failure_modes.py -v`
Expected: PASS

**Step 5: Run targeted regression tests**

Run: `python -m pytest tests/test_amazon_config.py tests/test_amazon_session.py tests/test_amazon_product_parser.py tests/test_amazon_review_parser.py tests/test_amazon_output_writer.py tests/test_amazon_failure_modes.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add scripts/scrape_amazon_product.py tests/test_amazon_failure_modes.py README.md
git commit -m "feat: add amazon scraper diagnostics"
```

## Implementation Notes

- Keep the existing `scripts/scrape_amazon_reviews.py` unchanged so the repo still supports the Apify path.
- Prefer `python -m pytest ...` over broad test runs while building this feature.
- Use small handcrafted fixtures instead of full live Amazon HTML dumps to keep tests stable and reviewable.
- Normalize review dates to raw strings in v1; do not spend time on locale-aware parsing until needed.
- Store session files outside git and add them to `.gitignore` if they are not already ignored.

## Verification Checklist

- `python scripts/amazon_login.py` successfully saves session state
- `python -m pytest tests/test_amazon_config.py -v`
- `python -m pytest tests/test_amazon_session.py -v`
- `python -m pytest tests/test_amazon_product_parser.py -v`
- `python -m pytest tests/test_amazon_review_parser.py -v`
- `python -m pytest tests/test_amazon_output_writer.py -v`
- `python -m pytest tests/test_amazon_failure_modes.py -v`
- `python scripts/scrape_amazon_product.py --url <amazon-product-url> --max-review-pages 2 --save-html --headed`

## Risks To Watch

- Amazon DOM drift will break selectors; keep parser warnings and raw HTML snapshots.
- Session expiry is normal; re-run login bootstrap instead of trying to refresh cookies manually.
- CAPTCHA pages should be treated as a stop condition, not something to bypass automatically.
- "All reviews" may still be limited by Amazon’s own pagination and availability rules.

Plan complete and saved to `docs/plans/2026-03-08-amazon-review-scraper.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
