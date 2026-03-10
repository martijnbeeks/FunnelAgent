from __future__ import annotations

from datetime import datetime, timezone


def parse_submission(submission) -> dict:
    """Convert a PRAW Submission to a plain dict."""
    created = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
    return {
        "id": submission.id,
        "title": submission.title,
        "author": str(submission.author) if submission.author else "[deleted]",
        "score": submission.score,
        "upvote_ratio": submission.upvote_ratio,
        "num_comments": submission.num_comments,
        "selftext": submission.selftext or "",
        "url": submission.url,
        "permalink": f"https://www.reddit.com{submission.permalink}",
        "subreddit": str(submission.subreddit),
        "created_utc": created.isoformat(),
        "is_self": submission.is_self,
        "link_flair_text": submission.link_flair_text,
    }


def parse_comment(comment, depth: int = 0) -> dict | None:
    """Convert a single PRAW Comment to a plain dict. Returns None for MoreComments."""
    from praw.models import MoreComments

    if isinstance(comment, MoreComments):
        return None

    created = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
    return {
        "id": comment.id,
        "author": str(comment.author) if comment.author else "[deleted]",
        "body": comment.body,
        "score": comment.score,
        "created_utc": created.isoformat(),
        "depth": depth,
        "replies": [],
    }


def build_comment_tree(
    comment_forest, max_depth: int = 10
) -> tuple[list[dict], list[str]]:
    """Recursively build a nested comment tree from a PRAW CommentForest.

    Returns (tree, warnings) where warnings lists skipped MoreComments instances.
    """
    from praw.models import MoreComments

    warnings: list[str] = []

    def _recurse(comments, depth: int) -> list[dict]:
        result: list[dict] = []
        for comment in comments:
            if isinstance(comment, MoreComments):
                warnings.append(
                    f"MoreComments skipped at depth {depth} ({comment.count} hidden)"
                )
                continue
            parsed = parse_comment(comment, depth)
            if parsed is None:
                continue
            if depth < max_depth and hasattr(comment, "replies"):
                parsed["replies"] = _recurse(comment.replies, depth + 1)
            result.append(parsed)
        return result

    tree = _recurse(comment_forest, 0)
    return tree, warnings


def flatten_comment_tree(tree: list[dict]) -> list[dict]:
    """Flatten a nested comment tree into a depth-first list (without replies key)."""
    flat: list[dict] = []
    for node in tree:
        entry = {k: v for k, v in node.items() if k != "replies"}
        flat.append(entry)
        if node.get("replies"):
            flat.extend(flatten_comment_tree(node["replies"]))
    return flat
