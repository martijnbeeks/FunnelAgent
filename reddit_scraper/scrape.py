"""Reddit scraper CLI — subreddit browsing and product search.

Usage:
    python -m reddit_scraper.scrape subreddit --name supplements --sort top --time-filter month --limit 25
    python -m reddit_scraper.scrape search --query "AG1 greens supplement" --limit 50 --comments
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import praw

from .config import RedditScraperConfig
from .parser import build_comment_tree, flatten_comment_tree, parse_submission

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

SUBREDDIT_SORT_CHOICES = ("hot", "new", "top", "rising", "controversial")
SEARCH_SORT_CHOICES = ("relevance", "hot", "top", "new", "comments")
TIME_FILTER_CHOICES = ("all", "day", "hour", "month", "week", "year")
COMMENT_SORT_CHOICES = ("best", "top", "new", "controversial", "old", "q&a")


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:60]


def _build_reddit(config: RedditScraperConfig) -> praw.Reddit:
    return praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        user_agent=config.user_agent,
    )


def _fetch_comments(submission, depth: int, sort: str) -> dict:
    submission.comment_sort = sort
    submission.comments.replace_more(limit=0)
    tree, warnings = build_comment_tree(submission.comments, max_depth=depth)
    flat = flatten_comment_tree(tree)
    return {"comments": tree, "comments_flat": flat, "comment_warnings": warnings}


def _process_submissions(
    submissions,
    *,
    include_comments: bool,
    comment_depth: int,
    comment_sort: str,
) -> list[dict]:
    posts: list[dict] = []
    for submission in submissions:
        post = parse_submission(submission)
        if include_comments:
            post.update(_fetch_comments(submission, comment_depth, comment_sort))
        posts.append(post)
    return posts


def _write_output(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Saved {data['total_posts']} posts to {output_path}")


def cmd_subreddit(args: argparse.Namespace) -> None:
    config = RedditScraperConfig.from_env()
    reddit = _build_reddit(config)
    subreddit = reddit.subreddit(args.name)

    sort_fn = getattr(subreddit, args.sort)
    if args.sort in ("top", "controversial"):
        submissions = sort_fn(time_filter=args.time_filter, limit=args.limit)
    else:
        submissions = sort_fn(limit=args.limit)

    posts = _process_submissions(
        submissions,
        include_comments=args.comments,
        comment_depth=args.comment_depth,
        comment_sort=args.comment_sort,
    )

    now = datetime.now(timezone.utc)
    data = {
        "scrape_type": "subreddit",
        "subreddit": args.name,
        "sort": args.sort,
        "time_filter": args.time_filter,
        "limit": args.limit,
        "scraped_at": now.isoformat(),
        "total_posts": len(posts),
        "posts": posts,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        slug = _slugify(args.name)
        ts = now.strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"{slug}_{ts}.json"

    _write_output(data, output_path)


def cmd_search(args: argparse.Namespace) -> None:
    config = RedditScraperConfig.from_env()
    reddit = _build_reddit(config)

    all_posts: list[dict] = []

    if args.subreddits:
        for sub_name in args.subreddits:
            subreddit = reddit.subreddit(sub_name)
            submissions = subreddit.search(
                args.query,
                sort=args.sort,
                time_filter=args.time_filter,
                limit=args.limit,
            )
            all_posts.extend(
                _process_submissions(
                    submissions,
                    include_comments=args.comments,
                    comment_depth=args.comment_depth,
                    comment_sort=args.comment_sort,
                )
            )
    else:
        submissions = reddit.subreddit("all").search(
            args.query,
            sort=args.sort,
            time_filter=args.time_filter,
            limit=args.limit,
        )
        all_posts = _process_submissions(
            submissions,
            include_comments=args.comments,
            comment_depth=args.comment_depth,
            comment_sort=args.comment_sort,
        )

    now = datetime.now(timezone.utc)
    data = {
        "scrape_type": "search",
        "query": args.query,
        "subreddits": args.subreddits or ["all"],
        "sort": args.sort,
        "time_filter": args.time_filter,
        "limit": args.limit,
        "scraped_at": now.isoformat(),
        "total_posts": len(all_posts),
        "posts": all_posts,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        slug = _slugify(args.query)
        ts = now.strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"search_{slug}_{ts}.json"

    _write_output(data, output_path)


def _extract_post_id(url_or_id: str) -> str:
    """Extract a Reddit post ID from a URL or bare ID."""
    match = re.search(r"/comments/([a-z0-9]+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id.strip()


def cmd_post(args: argparse.Namespace) -> None:
    config = RedditScraperConfig.from_env()
    reddit = _build_reddit(config)

    post_id = _extract_post_id(args.url)
    submission = reddit.submission(id=post_id)
    post = parse_submission(submission)
    post.update(_fetch_comments(submission, args.comment_depth, args.comment_sort))

    now = datetime.now(timezone.utc)
    data = {
        "scrape_type": "post",
        "post_id": post_id,
        "scraped_at": now.isoformat(),
        "total_posts": 1,
        "posts": [post],
    }

    if args.output:
        output_path = Path(args.output)
    else:
        slug = _slugify(submission.title)
        ts = now.strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"post_{slug}_{ts}.json"

    _write_output(data, output_path)


def _add_comment_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--comments", action="store_true", help="Fetch comment trees for each post"
    )
    parser.add_argument(
        "--comment-depth",
        type=int,
        default=10,
        help="Max comment nesting depth (default: 10)",
    )
    parser.add_argument(
        "--comment-sort",
        choices=COMMENT_SORT_CHOICES,
        default="best",
        help="Comment sort order (default: best)",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="reddit_scraper",
        description="Scrape Reddit posts and comments via PRAW",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- subreddit ---
    sub_parser = subparsers.add_parser("subreddit", help="Scrape a subreddit")
    sub_parser.add_argument("--name", required=True, help="Subreddit name (without r/)")
    sub_parser.add_argument(
        "--sort",
        choices=SUBREDDIT_SORT_CHOICES,
        default="hot",
        help="Sort order (default: hot)",
    )
    sub_parser.add_argument(
        "--time-filter",
        choices=TIME_FILTER_CHOICES,
        default="all",
        help="Time filter for top/controversial (default: all)",
    )
    sub_parser.add_argument(
        "--limit", type=int, default=25, help="Max posts to fetch (default: 25)"
    )
    sub_parser.add_argument("--output", help="Output file path (default: auto)")
    _add_comment_args(sub_parser)
    sub_parser.set_defaults(func=cmd_subreddit)

    # --- post ---
    post_parser = subparsers.add_parser("post", help="Fetch a single post by URL or ID")
    post_parser.add_argument("--url", required=True, help="Reddit post URL or ID")
    post_parser.add_argument(
        "--comment-depth",
        type=int,
        default=10,
        help="Max comment nesting depth (default: 10)",
    )
    post_parser.add_argument(
        "--comment-sort",
        choices=COMMENT_SORT_CHOICES,
        default="best",
        help="Comment sort order (default: best)",
    )
    post_parser.add_argument("--output", help="Output file path (default: auto)")
    post_parser.set_defaults(func=cmd_post)

    # --- search ---
    search_parser = subparsers.add_parser("search", help="Search Reddit for posts")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument(
        "--subreddits",
        nargs="+",
        help="Limit search to specific subreddits (space-separated)",
    )
    search_parser.add_argument(
        "--sort",
        choices=SEARCH_SORT_CHOICES,
        default="relevance",
        help="Sort order (default: relevance)",
    )
    search_parser.add_argument(
        "--time-filter",
        choices=TIME_FILTER_CHOICES,
        default="all",
        help="Time filter (default: all)",
    )
    search_parser.add_argument(
        "--limit", type=int, default=25, help="Max posts to fetch (default: 25)"
    )
    search_parser.add_argument("--output", help="Output file path (default: auto)")
    _add_comment_args(search_parser)
    search_parser.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
