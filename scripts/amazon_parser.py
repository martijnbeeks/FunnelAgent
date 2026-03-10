from __future__ import annotations

import json
import re
from datetime import datetime
from urllib.parse import urlparse, urlencode

from bs4 import BeautifulSoup


ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})")

# Amazon review sort/filter URL parameter mappings
SORT_MAP = {
    "recent": "recent",
    "helpful": "helpful",
    "top": "",  # default Amazon sort
}


def _extract_asin(url: str, soup: BeautifulSoup) -> str | None:
    candidates = [url]
    canonical = soup.select_one('link[rel="canonical"]')
    if canonical and canonical.get("href"):
        candidates.append(canonical["href"])

    for candidate in candidates:
        match = ASIN_RE.search(candidate)
        if match:
            return match.group(1)
    return None


def _extract_rating_number(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def _extract_int(text: str | None) -> int | None:
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def _extract_histogram(soup: BeautifulSoup) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for row in soup.select("#histogramTable tr"):
        key_text = row.select_one("td.aok-nowrap a")
        value_text = row.select_one("td:not(.aok-nowrap) a")
        if not key_text or not value_text:
            continue
        key = key_text.get_text(" ", strip=True).replace(" ", "_")
        value = _extract_int(value_text.get_text(" ", strip=True))
        if value is not None:
            histogram[key] = value
    return histogram


def _extract_image_urls(soup: BeautifulSoup) -> list[str]:
    urls: list[str] = []
    for script in soup.select('script[type="application/json"]'):
        raw = script.get_text(strip=True)
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        images = payload.get("colorImages", {}).get("initial", [])
        for image in images:
            url = image.get("hiRes") or image.get("large")
            if url and url not in urls:
                urls.append(url)
    return urls


def _parse_review_date(text: str | None) -> str | None:
    """Try to extract an ISO date string from Amazon's review date text.

    Amazon formats like 'Reviewed in the United States on January 5, 2024'.
    Returns ISO date string or the original text if parsing fails.
    """
    if not text:
        return None
    match = re.search(r"on\s+(.+)$", text)
    if not match:
        return text
    date_str = match.group(1).strip()
    for fmt in ("%B %d, %Y", "%d %B %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


def parse_product_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("#productTitle")
    rating = soup.select_one("#acrPopover")
    ratings_count = soup.select_one("#acrCustomerReviewText")
    bullet_nodes = soup.select("#feature-bullets .a-list-item")

    return {
        "asin": _extract_asin(url, soup),
        "canonical_url": urlparse(url)._replace(query="", fragment="").geturl(),
        "title": title.get_text(" ", strip=True) if title else None,
        "average_rating": _extract_rating_number(rating.get("title") if rating else None),
        "ratings_count": _extract_int(ratings_count.get_text(" ", strip=True) if ratings_count else None),
        "bullets": [node.get_text(" ", strip=True) for node in bullet_nodes if node.get_text(" ", strip=True)],
        "histogram": _extract_histogram(soup),
        "image_urls": _extract_image_urls(soup),
    }


def _text_or_none(node) -> str | None:
    if node is None:
        return None
    text = node.get_text(" ", strip=True)
    return text or None


def _extract_review_rating(review_node) -> float | None:
    rating_node = review_node.select_one(
        '[data-hook="review-star-rating"], [data-hook="cmps-review-star-rating"]'
    )
    return _extract_rating_number(_text_or_none(rating_node))


def _extract_review_media(review_node) -> list[str]:
    media: list[str] = []
    for image in review_node.select('[data-hook="review-image-tile"]'):
        src = image.get("src")
        if src and src not in media:
            media.append(src)
    return media


def parse_reviews_page(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    reviews = []
    warnings: list[str] = []

    for review_node in soup.select('[data-hook="review"]'):
        review_id = review_node.get("id")
        if not review_id:
            warnings.append("review without id skipped")
            continue

        helpful_text = _text_or_none(review_node.select_one('[data-hook="helpful-vote-statement"]'))
        raw_date = _text_or_none(review_node.select_one('[data-hook="review-date"]'))
        reviews.append(
            {
                "review_id": review_id,
                "author": _text_or_none(review_node.select_one(".a-profile-name")),
                "rating": _extract_review_rating(review_node),
                "title": _text_or_none(review_node.select_one('[data-hook="review-title"]')),
                "date": _parse_review_date(raw_date),
                "date_raw": raw_date,
                "verified": review_node.select_one('[data-hook="avp-badge"]') is not None,
                "helpful_count": _extract_int(helpful_text),
                "format": _text_or_none(review_node.select_one('[data-hook="format-strip"]')),
                "body": _text_or_none(review_node.select_one('[data-hook="review-body"]')),
                "media": _extract_review_media(review_node),
            }
        )

    next_link = soup.select_one(".a-pagination .a-last a")
    return {
        "reviews": reviews,
        "next_page_url": next_link.get("href") if next_link else None,
        "warnings": warnings,
    }


def build_filtered_reviews_url(
    marketplace_url: str,
    asin: str,
    star_rating: str | None = None,
    verified_only: bool = False,
    sort_by: str = "recent",
) -> str:
    """Build a reviews URL with optional filters applied via URL parameters.

    Args:
        marketplace_url: Base marketplace URL (e.g. https://www.amazon.com)
        asin: Product ASIN
        star_rating: Filter by star count ("1"-"5"), or None for all
        verified_only: Only show verified purchase reviews
        sort_by: Sort order — "recent", "helpful", or "top"
    """
    base = f"{marketplace_url}/product-reviews/{asin}/"

    params: dict[str, str] = {}

    # Sort
    sort_value = SORT_MAP.get(sort_by, "recent")
    if sort_value:
        params["sortBy"] = sort_value

    # Star filter: Amazon uses filterByStar=one_star through five_star
    star_map = {"1": "one_star", "2": "two_star", "3": "three_star", "4": "four_star", "5": "five_star"}
    if star_rating and star_rating in star_map:
        params["filterByStar"] = star_map[star_rating]

    # Verified only
    if verified_only:
        params["reviewerType"] = "avp_only_reviews"

    if params:
        return f"{base}?{urlencode(params)}"
    return base
