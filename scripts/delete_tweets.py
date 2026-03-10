#!/usr/bin/env python3
"""Delete all tweets from your Twitter/X account using your Twitter archive.

The Free tier API can delete tweets but can't list them, so we load tweet IDs
from your downloaded Twitter archive instead.

Download your archive:
  1. Go to x.com → Settings → Your Account → Download an archive of your data
  2. Unzip the downloaded file
  3. Pass the path to the unzipped folder as --archive

Usage:
    export TWITTER_API_KEY="your-consumer-key"
    export TWITTER_API_SECRET="your-consumer-secret"
    export TWITTER_ACCESS_TOKEN="your-access-token"
    export TWITTER_ACCESS_SECRET="your-access-token-secret"

    python scripts/delete_tweets.py --archive /path/to/twitter-archive --dry-run
    python scripts/delete_tweets.py --archive /path/to/twitter-archive
"""

import json
import os
import re
import sys
import time
import argparse
from pathlib import Path

try:
    import tweepy
except ImportError:
    print("Install tweepy first: pip install tweepy")
    sys.exit(1)


def get_client():
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

    missing = []
    if not api_key:
        missing.append("TWITTER_API_KEY")
    if not api_secret:
        missing.append("TWITTER_API_SECRET")
    if not access_token:
        missing.append("TWITTER_ACCESS_TOKEN")
    if not access_secret:
        missing.append("TWITTER_ACCESS_SECRET")

    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        print("See script header for setup instructions.")
        sys.exit(1)

    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )


def load_tweet_ids_from_archive(archive_path):
    """Extract tweet IDs from a Twitter archive directory."""
    archive = Path(archive_path)

    # Twitter archive stores tweets in data/tweets.js
    tweets_file = archive / "data" / "tweets.js"
    if not tweets_file.exists():
        # Also check for older format
        tweets_file = archive / "data" / "tweet.js"
    if not tweets_file.exists():
        print(f"Could not find tweets.js or tweet.js in {archive / 'data'}")
        print("Make sure you pass the path to the unzipped archive folder.")
        sys.exit(1)

    content = tweets_file.read_text(encoding="utf-8")
    # The file starts with a JS variable assignment like "window.YTD.tweets.part0 = "
    # Strip that to get valid JSON
    json_str = re.sub(r"^.*?=\s*", "", content, count=1)
    tweets = json.loads(json_str)

    tweet_ids = []
    for entry in tweets:
        tweet = entry.get("tweet", entry)
        tweet_id = tweet.get("id") or tweet.get("id_str")
        if tweet_id:
            tweet_ids.append(str(tweet_id))

    return tweet_ids


def main():
    parser = argparse.ArgumentParser(description="Delete all tweets from your account")
    parser.add_argument(
        "--archive",
        required=True,
        help="Path to your unzipped Twitter archive folder",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count tweets without deleting them",
    )
    args = parser.parse_args()

    # Load tweet IDs from archive
    print(f"Loading tweets from archive: {args.archive}")
    tweet_ids = load_tweet_ids_from_archive(args.archive)
    print(f"Found {len(tweet_ids)} tweets in archive.")

    if not tweet_ids:
        print("No tweets found. Nothing to do.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would delete {len(tweet_ids)} tweets.")
        print(f"First 10 tweet IDs: {tweet_ids[:10]}")
        print("\nRun without --dry-run to delete them.")
        return

    # Authenticate
    client = get_client()
    me = client.get_me()
    if not me or not me.data:
        print("Failed to authenticate. Check your credentials.")
        sys.exit(1)
    print(f"Authenticated as @{me.data.username}")

    confirm = input(
        f"\nThis will PERMANENTLY delete {len(tweet_ids)} tweets from @{me.data.username}.\n"
        f"Type 'DELETE' to confirm: "
    )
    if confirm != "DELETE":
        print("Aborted.")
        sys.exit(0)

    deleted = 0
    errors = 0
    skipped = 0

    for i, tweet_id in enumerate(tweet_ids):
        try:
            client.delete_tweet(tweet_id)
            deleted += 1
            print(f"  Deleted ({deleted}/{len(tweet_ids)}): {tweet_id}")
            # Rate limit: 50 deletions per 15 min window
            time.sleep(18.5)
        except tweepy.TooManyRequests:
            print("  Rate limited. Waiting 15 minutes...")
            time.sleep(900)
            try:
                client.delete_tweet(tweet_id)
                deleted += 1
                print(f"  Deleted ({deleted}/{len(tweet_ids)}): {tweet_id}")
            except Exception as e:
                errors += 1
                print(f"  Error: {e}")
        except tweepy.NotFound:
            skipped += 1
            print(f"  Already deleted: {tweet_id}")
        except Exception as e:
            errors += 1
            print(f"  Error deleting {tweet_id}: {e}")

    print(f"\nDone. Deleted: {deleted}, Already gone: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()
