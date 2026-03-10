#!/usr/bin/env python3
"""
Scrape multiple Reddit posts using YARS with rate limiting to avoid IP bans.

Usage:
    python scripts/scrape_reddit_posts.py --urls-file <file> --output-dir <dir> [--delay-min 8] [--delay-max 15]
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

# Add YARS to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'YARS', 'src'))

from yars.yars import YARS


def url_to_permalink(url: str) -> str:
    """Extract permalink from full Reddit URL."""
    url = url.strip().rstrip('/')
    # Remove query params
    if '?' in url:
        url = url[:url.index('?')]
    # Extract path after reddit.com
    if 'reddit.com' in url:
        return url.split('reddit.com')[1] + '/'
    return url


def url_to_filename(url: str) -> str:
    """Generate a safe filename from a Reddit URL."""
    permalink = url_to_permalink(url)
    # /r/subreddit/comments/id/title/ -> subreddit_id_title
    parts = [p for p in permalink.split('/') if p and p not in ('r', 'comments')]
    name = '_'.join(parts)
    # Truncate long filenames
    if len(name) > 120:
        name = name[:120]
    return f"reddit_{name}.json"


def scrape_with_retry(miner: YARS, permalink: str, max_retries: int = 3) -> dict | None:
    """Scrape a post with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            result = miner.scrape_post_details(permalink)
            if result:
                return result
            print(f"  Empty result on attempt {attempt}/{max_retries}")
        except Exception as e:
            print(f"  Error on attempt {attempt}/{max_retries}: {e}")
        if attempt < max_retries:
            wait = 30 * attempt  # 30s, 60s backoff
            print(f"  Retrying in {wait}s...")
            time.sleep(wait)
    return None


def main():
    parser = argparse.ArgumentParser(description='Scrape Reddit posts with rate limiting')
    parser.add_argument('--urls-file', required=True, help='File with one Reddit URL per line')
    parser.add_argument('--output-dir', required=True, help='Directory to save JSON files')
    parser.add_argument('--delay-min', type=int, default=8, help='Min delay between requests (seconds)')
    parser.add_argument('--delay-max', type=int, default=15, help='Max delay between requests (seconds)')
    args = parser.parse_args()

    # Read URLs
    urls_path = Path(args.urls_file)
    urls = [line.strip() for line in urls_path.read_text().splitlines() if line.strip() and not line.startswith('#')]
    print(f"Loaded {len(urls)} URLs from {urls_path}")

    # Create output dir
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check which are already scraped
    pending = []
    for url in urls:
        filename = url_to_filename(url)
        filepath = out_dir / filename
        if filepath.exists() and filepath.stat().st_size > 50:
            print(f"  SKIP (exists): {filename}")
        else:
            pending.append(url)

    print(f"\n{len(urls) - len(pending)} already scraped, {len(pending)} remaining\n")
    if not pending:
        print("Nothing to do.")
        return

    # Estimate time
    avg_delay = (args.delay_min + args.delay_max) / 2
    est_minutes = (len(pending) * avg_delay) / 60
    print(f"Estimated time: ~{est_minutes:.0f} minutes ({args.delay_min}-{args.delay_max}s between requests)\n")

    miner = YARS()
    success = 0
    failed = []

    for i, url in enumerate(pending, 1):
        filename = url_to_filename(url)
        permalink = url_to_permalink(url)
        print(f"[{i}/{len(pending)}] {permalink}")

        result = scrape_with_retry(miner, permalink)

        if result:
            filepath = out_dir / filename
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            comment_count = len(result.get('comments', []))
            print(f"  OK — {comment_count} top-level comments -> {filename}")
            success += 1
        else:
            print(f"  FAILED — skipping")
            failed.append(url)

        # Rate limiting (skip delay after last request)
        if i < len(pending):
            delay = random.uniform(args.delay_min, args.delay_max)
            print(f"  Waiting {delay:.1f}s...")
            time.sleep(delay)

    # Summary
    print(f"\n{'='*60}")
    print(f"Done. {success}/{len(pending)} scraped successfully.")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for url in failed:
            print(f"  {url}")
        # Save failed URLs for retry
        failed_path = out_dir / '_failed_urls.txt'
        failed_path.write_text('\n'.join(failed) + '\n')
        print(f"\nFailed URLs saved to {failed_path}")


if __name__ == '__main__':
    main()
