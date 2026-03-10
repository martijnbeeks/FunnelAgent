#!/usr/bin/env python3
"""
Batch Amazon Reviews Scraper — scrapes reviews for a predefined list of products.

Uses the same Apify actor as scrape_amazon_reviews.py but processes products
in batches to avoid timeouts, and saves one JSON file per ASIN.

Usage:
    python scripts/scrape_batch_reviews.py
    python scripts/scrape_batch_reviews.py --batch-size 5 --output-dir output/reviews

Environment:
    APIFY_API_KEY - Your Apify API token (or set in .env file)
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    from apify_client import ApifyClient
except ImportError:
    print("Error: apify-client package not installed. Run: pip install apify-client", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    pass

ACTOR_ID = "delicious_zebu/amazon-reviews-scraper-with-advanced-filters"

AMAZON_URLS = [
    "https://www.amazon.com/dp/B006IB5T4W",
    "https://www.amazon.com/dp/B00TTD9BRC",
    "https://www.amazon.com/dp/B0BTXLHWCC",
    "https://www.amazon.com/dp/B00AINMFAC",
    "https://www.amazon.com/dp/B0CDM74PPH",
    "https://www.amazon.com/dp/B005UEB96K",
    "https://www.amazon.com/dp/B000GCJ2HC",
    "https://www.amazon.com/dp/B007TBUOQQ",
    "https://www.amazon.com/dp/B07NSMKL2S",
    "https://www.amazon.com/dp/B001BYMFKM",
    "https://www.amazon.com/dp/B007TB4YBQ",
    "https://www.amazon.com/dp/B000087805",
    "https://www.amazon.com/dp/B0BPN4NL4R",
    "https://www.amazon.com/dp/B000052YMB",
    "https://www.amazon.com/dp/B00AXVJF52",
    "https://www.amazon.com/dp/B005L8YVRO",
    "https://www.amazon.com/dp/B0001TU1MK",
    "https://www.amazon.com/dp/B00H2DXQIS",
    "https://www.amazon.com/dp/B005MI648C",
    "https://www.amazon.com/dp/B00DWYIIJ0",
    "https://www.amazon.com/dp/B00HTJFNBM",
    "https://www.amazon.com/dp/B0071GVNHA",
    "https://www.amazon.com/dp/B07FNBDPKS",
    "https://www.amazon.com/dp/B00LP3MU6M",
    "https://www.amazon.com/dp/B001ET79H8",
    "https://www.amazon.com/dp/B07CZWYY4H",
    "https://www.amazon.com/dp/B0010ED5FC",
    "https://www.amazon.com/dp/B00008MNZO",
    "https://www.amazon.com/dp/B00IYWFCPM",
    "https://www.amazon.com/dp/B01LB2OE0I",
    "https://www.amazon.com/dp/B000GCNJ6U",
    "https://www.amazon.com/dp/B00FFS8RMG",
    "https://www.amazon.com/dp/B00P8HGNVA",
    "https://www.amazon.com/dp/B005FJ3LGI",
    "https://www.amazon.com/dp/B003IHXMQ8",
    "https://www.amazon.com/dp/B001AK46GQ",
    "https://www.amazon.com/dp/B0BKL96VCL",
    "https://www.amazon.com/dp/B07NSPJR25",
    "https://www.amazon.com/dp/B0009RF9DG",
    "https://www.amazon.com/dp/B003DKU5BW",
    "https://www.amazon.com/dp/B0019LVF7S",
    "https://www.amazon.com/dp/B00CD85KNW",
    "https://www.amazon.com/dp/B07TGNWFNX",
    "https://www.amazon.com/dp/B000GCE81Y",
    "https://www.amazon.com/dp/B07D9DG9V1",
    "https://www.amazon.com/dp/B002PQ8BQM",
    "https://www.amazon.com/dp/B00NPYMZPS",
    "https://www.amazon.com/dp/B01G8GZBSQ",
    "https://www.amazon.com/dp/B001E96LKQ",
    "https://www.amazon.com/dp/B000PC4SQC",
    "https://www.amazon.com/dp/B000HZGTUS",
    "https://www.amazon.com/dp/B002EHSMKE",
    "https://www.amazon.com/dp/B07BHCFF9V",
    "https://www.amazon.com/dp/B000YQGHKQ",
    "https://www.amazon.com/dp/B086C3ZVT2",
    "https://www.amazon.com/dp/B01CW4ZO9I",
    "https://www.amazon.com/dp/B00A8OAK1A",
    "https://www.amazon.com/dp/B000RLLVKK",
    "https://www.amazon.com/dp/B09DKBKL6W",
    "https://www.amazon.com/dp/B000KL0TZU",
    "https://www.amazon.com/dp/B00DPCQX84",
    "https://www.amazon.com/dp/B000050FJQ",
    "https://www.amazon.com/dp/B008YTWVF6",
    "https://www.amazon.com/dp/B0044NO5PS",
    "https://www.amazon.com/dp/B001GAQIUC",
    "https://www.amazon.com/dp/B003EKKDS0",
    "https://www.amazon.com/dp/B07DG7QLCM",
    "https://www.amazon.com/dp/B01A2GBXWI",
    "https://www.amazon.com/dp/B001GAQIUG",
    "https://www.amazon.com/dp/B0039UTHEM",
    "https://www.amazon.com/dp/B00027DDLS",
    "https://www.amazon.com/dp/B0CWV4C1S7",
    "https://www.amazon.com/dp/B0753JT7YC",
    "https://www.amazon.com/dp/B07MQ1FW91",
    "https://www.amazon.com/dp/B07L33K6BW",
    "https://www.amazon.com/dp/B00D8YYLRO",
    "https://www.amazon.com/dp/B00165UYDW",
]


def extract_asin(url: str) -> str | None:
    """Extract ASIN from an Amazon URL."""
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    return match.group(1) if match else None


def scrape_batch(client: ApifyClient, urls: list[str]) -> list[dict]:
    """Scrape reviews for a batch of URLs via the Apify actor."""
    run_input = {
        "ASIN_or_URL": urls,
        "sort_reviews_by": ["helpful", "recent"],
        "recent_days": 365,
        "max_reviews": 10000,
        "filter_by_ratings": ["all_stars", "five_star", "four_star", "three_star", "two_star", "one_star", "positive", "critical"],
        "filter_by_verified_purchase_only": ["all_reviews", "avp_only_reviews"],
        "filter_by_mediaType": ["all_contents", "media_reviews_only"],
        "unique_only": True,
    }

    run = client.actor(ACTOR_ID).call(run_input=run_input)
    items = client.dataset(run["defaultDatasetId"]).list_items().items
    return items


def main():
    parser = argparse.ArgumentParser(description="Batch scrape Amazon reviews via Apify")
    parser.add_argument("--batch-size", type=int, default=10, help="Products per Apify run (default: 10)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory (default: output/reviews)")
    args = parser.parse_args()

    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        print("Error: APIFY_API_KEY not set in environment or .env file.", file=sys.stderr)
        sys.exit(1)

    client = ApifyClient(api_key)

    output_dir = Path(args.output_dir) if args.output_dir else Path(__file__).resolve().parent.parent / "output" / "reviews"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build batches
    urls = AMAZON_URLS
    batches = [urls[i:i + args.batch_size] for i in range(0, len(urls), args.batch_size)]

    print(f"Total products: {len(urls)}")
    print(f"Batch size: {args.batch_size}")
    print(f"Total batches: {len(batches)}")
    print(f"Output directory: {output_dir}")
    print()

    all_reviews = []
    for batch_idx, batch in enumerate(batches, 1):
        asins_in_batch = [extract_asin(u) or u for u in batch]
        print(f"--- Batch {batch_idx}/{len(batches)} ({len(batch)} products: {', '.join(asins_in_batch)}) ---")

        try:
            items = scrape_batch(client, batch)
            print(f"    Fetched {len(items)} reviews")
            all_reviews.extend(items)

            # Save per-ASIN files
            reviews_by_asin: dict[str, list[dict]] = {}
            for item in items:
                asin = item.get("ASIN", "unknown")
                reviews_by_asin.setdefault(asin, []).append(item)

            for asin, reviews in reviews_by_asin.items():
                asin_file = output_dir / f"{asin}.json"
                # Merge with existing file if present
                if asin_file.exists():
                    existing = json.loads(asin_file.read_text(encoding="utf-8"))
                    existing_ids = {r.get("reviewId") for r in existing}
                    new = [r for r in reviews if r.get("reviewId") not in existing_ids]
                    reviews = existing + new
                asin_file.write_text(json.dumps(reviews, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"    Saved {len(reviews)} reviews to {asin_file.name}")

        except Exception as e:
            print(f"    ERROR in batch {batch_idx}: {e}", file=sys.stderr)

        # Brief pause between batches to be kind to Apify
        if batch_idx < len(batches):
            print("    Waiting 5s before next batch...")
            time.sleep(5)

    # Save combined file
    combined_file = output_dir / "_all_reviews.json"
    combined_file.write_text(json.dumps(all_reviews, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone! {len(all_reviews)} total reviews saved.")
    print(f"Combined file: {combined_file}")
    print(f"Per-ASIN files: {output_dir}/")


if __name__ == "__main__":
    main()
