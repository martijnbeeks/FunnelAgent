#!/usr/bin/env python3
"""
Amazon Reviews Scraper via Apify (delicious_zebu/amazon-reviews-scraper-with-advanced-filters).

Usage:
    python scripts/scrape_amazon_reviews.py --asins B0CZ9DGVLG B0BFC42HQR
    python scripts/scrape_amazon_reviews.py --asins B0CZ9DGVLG --output output/reviews.json

Environment:
    APIFY_API_KEY - Your Apify API token (or set in .env file)
"""

import argparse
import json
import os
import sys
from datetime import datetime
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


def scrape_reviews(asins: list[str]) -> list[dict]:
    """Run the Apify actor and return reviews."""
    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        print("Error: APIFY_API_KEY not set in environment or .env file.", file=sys.stderr)
        sys.exit(1)

    client = ApifyClient(api_key)

    run_input = {
        "ASIN_or_URL": asins,
        "sort_reviews_by": ["helpful", "recent"],
        "recent_days": 0,
        "max_reviews": 10000,
        "filter_by_ratings": ["all_stars", "five_star", "four_star", "three_star", "two_star", "one_star", "positive", "critical"],
        "filter_by_verified_purchase_only": ["all_reviews", "avp_only_reviews"],
        "filter_by_mediaType": ["all_contents", "media_reviews_only"],
        "unique_only": True,
    }

    print(f"Starting Apify actor for {len(asins)} product(s)...")
    print(f"ASINs: {', '.join(asins)}")

    run = client.actor(ACTOR_ID).call(run_input=run_input)

    items = client.dataset(run["defaultDatasetId"]).list_items().items

    print(f"Fetched {len(items)} reviews.")
    return items


def main():
    parser = argparse.ArgumentParser(description="Scrape Amazon reviews via Apify")
    parser.add_argument("--asins", nargs="+", required=True, help="One or more Amazon ASINs or product URLs")
    parser.add_argument("--output", type=str, default=None, help="Output JSON file path")
    args = parser.parse_args()

    results = scrape_reviews(args.asins)

    output_json = json.dumps(results, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).resolve().parent.parent / "output" / f"amazon_reviews_{timestamp}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_json, encoding="utf-8")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
