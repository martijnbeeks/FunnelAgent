---
name: scrape-amazon-reviews
description: Scrapes Amazon product reviews using the Playwright-based scraper with anti-detection, filtering, retry logic, and resume support.
---

# Scrape Amazon Reviews Skill

You scrape Amazon product pages and their reviews using the project's Playwright-based scraper. This skill is flexible — it accepts an ASIN, Amazon URL, or product name to search for, and supports filtering by star rating, verified purchases, and sort order.

## PREREQUISITES

- Python 3.8+ with packages from `scripts/requirements.txt` installed
- Playwright browsers installed: `playwright install chromium`
- (Optional) An Amazon login session for accessing more reviews — run `python -m scripts.amazon_login` first
- (Optional) Proxy configured in `.env` for lower block risk

## INPUT

You need **one of**:
- **ASIN** — a 10-character Amazon product identifier (e.g. `B006IB5T4W`)
- **Amazon URL** — any Amazon product URL containing `/dp/ASIN`
- **Product name** — you'll search Amazon to find the ASIN yourself

Plus optional parameters:
- **star_rating** — filter to only 1-star, 2-star, 3-star, 4-star, or 5-star reviews
- **verified_only** — only scrape verified purchase reviews (`true`/`false`, default `false`)
- **sort_by** — `recent`, `helpful`, or `top` (default `recent`)
- **max_review_pages** — how many pages to scrape (default `500`, ~5000 reviews)
- **output_dir** — where to save output (default: `{RUN_DIR}/amazon/` or `output/{product-slug}/amazon/`)
- **marketplace** — Amazon domain (default: `www.amazon.com`, also supports `.co.uk`, `.de`, `.nl`, etc.)

## STEP 1: RESOLVE THE ASIN

Determine the ASIN from the user's input:

### If given an ASIN directly:
Use it as-is. Verify it's exactly 10 alphanumeric characters.

### If given an Amazon URL:
Extract the ASIN from the `/dp/XXXXXXXXXX` pattern in the URL.

### If given a product name:
Use WebFetch to search Amazon and find the product:
```
WebFetch:
  url: https://www.amazon.com/s?k={url-encoded product name}
  prompt: "Find the main product listing that matches '{product name}'. Return the ASIN (10-character code from the /dp/ URL) and the product title. If there are multiple matches, return the top 3 with their ASINs so the user can pick."
```

If multiple matches, present options to the user and ask which one to scrape.

## STEP 2: CONFIGURE THE SCRAPE

Build the command based on user requirements. The base command is:

```bash
python -m scripts.scrape_amazon_product --asin {ASIN}
```

Add flags based on the parameters:

| Parameter | Flag | Example |
|-----------|------|---------|
| Star rating filter | `--star-rating {1-5}` | `--star-rating 1` for negative reviews only |
| Verified only | `--verified-only` | Filters to verified purchases |
| Sort order | `--sort-by {recent\|helpful\|top}` | `--sort-by helpful` |
| Max pages | `--max-review-pages {N}` | `--max-review-pages 50` for quick scrape |
| Output directory | `--output-dir {path}` | `--output-dir output/my-product/amazon` |
| Save raw HTML | `--save-html` | Useful for debugging selector issues |
| Headed mode | `--headed` | Watch the browser (debugging) |
| Fresh start | `--no-resume` | Ignore previous partial scrape |

### Quick scrape presets:

**Full scrape** (all reviews, all stars):
```bash
python -m scripts.scrape_amazon_product --asin {ASIN} --max-review-pages 500
```

**Negative reviews only** (for pain point mining):
```bash
python -m scripts.scrape_amazon_product --asin {ASIN} --star-rating 1 --sort-by recent
```

**Positive reviews only** (for testimonial mining):
```bash
python -m scripts.scrape_amazon_product --asin {ASIN} --star-rating 5 --verified-only
```

**Quick sample** (first 5 pages, ~50 reviews):
```bash
python -m scripts.scrape_amazon_product --asin {ASIN} --max-review-pages 5
```

**FunnelAgent research mode** (all reviews, output to run dir):
```bash
python -m scripts.scrape_amazon_product --asin {ASIN} --output-dir {RUN_DIR}/amazon
```

## STEP 3: RUN THE SCRAPER

Execute the command from Step 2 using the Bash tool. The scraper will:

1. Launch a Chromium browser with stealth anti-detection
2. Navigate to the product page and extract product metadata
3. Navigate to the reviews section with any filters applied
4. Paginate through all review pages with smart random delays (3-8s)
5. Retry automatically on CAPTCHA/blocks with exponential backoff
6. Save progress incrementally after each page (resumes on re-run)

**Expected runtime:** ~10 seconds per page. A 50-page scrape takes ~8-10 minutes.

Monitor the output for:
- `WARNING: Blocked on attempt...` — the scraper is retrying, this is normal
- `Blocked on review page X after retries. Progress saved.` — scraper hit a hard block, re-run later to resume
- `Saved scrape output to {path}` — success

## STEP 4: VERIFY OUTPUT

After the scraper completes, check the output directory:

```
{output_dir}/
├── product.json    — Product metadata (title, rating, bullet points, images)
├── reviews.json    — All scraped reviews (array of review objects)
├── meta.json       — Scrape metadata (timestamp, filters used, page count, warnings)
└── raw/            — (only with --save-html) Raw HTML pages for debugging
```

Read `meta.json` to verify:
- `total_reviews` — how many reviews were collected
- `parser_warnings` — any issues during parsing
- `filters` — confirms the correct filters were applied

### Review object format:
```json
{
  "review_id": "R1ABC2DEF3GH",
  "author": "John D.",
  "rating": 5.0,
  "title": "Great product!",
  "date": "2024-01-15",
  "date_raw": "Reviewed in the United States on January 15, 2024",
  "verified": true,
  "helpful_count": 42,
  "format": "Size: 60 Count",
  "body": "The full review text...",
  "media": ["https://images-na.ssl-images-amazon.com/..."]
}
```

## STEP 5: PRESENT RESULTS

Summarize the scrape results to the user:

> **Scrape complete for {product title} ({ASIN})**
> - Reviews collected: {total_reviews}
> - Pages scraped: {total_review_pages_fetched}
> - Filters: {star_rating or "all stars"}, {sort_by}, {"verified only" if verified_only else "all reviewers"}
> - Output: `{output_dir}/`

If the scrape was interrupted (blocked mid-way), tell the user:

> **Partial scrape — {total_reviews} reviews collected before being blocked on page {page}.**
> Re-run the same command to resume from where it stopped.

## MULTI-PRODUCT SCRAPING

To scrape reviews for multiple products (e.g. competitor analysis), run the scraper in a loop:

```bash
for ASIN in B006IB5T4W B00TTD9BRC B0BTXLHWCC; do
  python -m scripts.scrape_amazon_product --asin $ASIN --output-dir output/reviews/$ASIN
done
```

Or run multiple Bash commands in parallel for independent ASINs.

## TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| `Playwright is not installed` | Run `pip install -r scripts/requirements.txt && playwright install chromium` |
| CAPTCHA on first page | Run `python -m scripts.amazon_login` to establish a session, then retry |
| Blocked after N pages | Wait 10-30 minutes and re-run (auto-resumes). Consider adding a proxy in `.env` |
| Empty reviews | Product may have few reviews, or try `--sort-by helpful` instead |
| Wrong marketplace | Set `AMAZON_MARKETPLACE=www.amazon.de` in `.env` or pass via env |
| `playwright-stealth not installed` | Run `pip install playwright-stealth` — scraper still works without it but is easier to detect |

## INTEGRATION WITH FUNNEL PIPELINE

When used as part of the FunnelAgent pipeline, this skill feeds review data into the Deep Research step. The orchestrator can spawn this skill to collect real customer language before or alongside Step 1.

```
Use the Task tool with:
  subagent_type: "general-purpose"
  mode: "bypassPermissions"
  prompt: "You are executing Amazon Review Scraping for the FunnelAgent pipeline.

    FIRST: Read skills/scrape-amazon-reviews/SKILL.md for your complete instructions.

    RUN_DIR: {RUN_DIR}
    ASIN: {asin}

    Scrape all reviews (all stars, sorted by recent). Save output to {RUN_DIR}/amazon/.
    After scraping, read reviews.json and produce a brief summary:
    - Total review count and average rating
    - Top 5 most common complaints (from 1-2 star reviews)
    - Top 5 most praised features (from 4-5 star reviews)
    - 10 verbatim customer quotes that capture strong emotion
    Save the summary to {RUN_DIR}/00_amazon_review_summary.md"
```

## OUTPUT

- `{output_dir}/product.json` — Product metadata
- `{output_dir}/reviews.json` — All reviews as JSON array
- `{output_dir}/meta.json` — Scrape metadata and diagnostics
