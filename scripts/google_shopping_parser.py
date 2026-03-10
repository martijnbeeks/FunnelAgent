from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag


def _text_or_none(node) -> str | None:
    if node is None:
        return None
    text = node.get_text(" ", strip=True)
    return text or None


def _extract_rating_number(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def _extract_int(text: str | None) -> int | None:
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def _find_panel(soup: BeautifulSoup) -> Tag | None:
    """Find the product detail overlay panel that Google Shopping opens as an SPA."""
    # Primary: div.mLFOe contains the full product detail panel
    for selector in ["div.mLFOe", '[jsname="kefP3d"]', "div.zzkrfd"]:
        panel = soup.select_one(selector)
        if panel and len(panel.get_text(strip=True)) > 100:
            return panel
    return None


def parse_product_panel(html: str) -> dict:
    """Extract product metadata from the Google Shopping SPA overlay panel.

    Google Shopping (2025+) is an SPA — clicking a product on search results
    opens an overlay panel on the same page rather than navigating to a new URL.
    This function parses that panel's HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    panel = _find_panel(soup)
    if not panel:
        return {
            "title": None,
            "average_rating": None,
            "total_reviews": None,
            "price_range": None,
            "merchants": [],
            "image_urls": [],
            "histogram": {},
        }

    # Title — panel structure: merchant name (line 0), product title (line 1), rating (line 2)
    # The title is the second non-trivial text line in the panel.
    title = None
    panel_text = panel.get_text("\n", strip=True)
    panel_lines = [line.strip() for line in panel_text.split("\n") if line.strip()]
    skip_patterns = ["user review", "size :", "price", "sign in", "learn more", "track price",
                     "(function", "var ", "this||"]
    candidates: list[str] = []
    for line in panel_lines:
        if len(line) < 5 or line.startswith("$") or line.startswith("("):
            continue
        if any(skip in line.lower() for skip in skip_patterns):
            continue
        # Stop at rating number or size section
        if re.match(r"^\d+(\.\d+)?$", line):
            break
        candidates.append(line)
        if len(candidates) >= 2:
            break
    # The product title is the longer of the first two candidates (merchant name is short)
    if len(candidates) >= 2:
        title = max(candidates, key=len)
    elif candidates:
        title = candidates[0]

    # Average rating — panel shows "4.8" followed by "( 39K user reviews )"
    # Also appears as "4.8/5" in merchant listings
    avg_rating = None
    # Method 1: find standalone decimal like "4.8" near the top of the panel
    for line in panel_lines:
        match = re.match(r"^(\d\.\d)$", line)
        if match:
            avg_rating = float(match.group(1))
            break
    # Method 2: find "X.X/5" pattern in merchant listings
    if not avg_rating:
        for text_node in panel.find_all(string=re.compile(r"\d+\.\d+/5")):
            match = re.search(r"(\d+\.\d+)/5", text_node)
            if match:
                avg_rating = float(match.group(1))
                break

    # Total reviews
    total_reviews = None
    # Look for "39,498 reviews" or "39K user reviews"
    for text_node in panel.find_all(string=re.compile(r"[\d,]+K?\s*(?:user\s+)?reviews?", re.IGNORECASE)):
        text = text_node.strip()
        # Handle "39K" format
        k_match = re.search(r"(\d+)K\s*(?:user\s+)?reviews?", text, re.IGNORECASE)
        if k_match:
            total_reviews = int(k_match.group(1)) * 1000
            break
        # Handle "39,498 reviews" format
        num_match = re.search(r"([\d,]+)\s*(?:user\s+)?reviews?", text, re.IGNORECASE)
        if num_match:
            total_reviews = _extract_int(num_match.group(1))
            break

    # Price range — "Typically" on one line, "$18–$26" on the next
    price_range = None
    for idx, line in enumerate(panel_lines):
        if line.strip().lower() == "typically" and idx + 1 < len(panel_lines):
            next_line = panel_lines[idx + 1].strip()
            if next_line.startswith("$"):
                price_range = next_line
                break
    # Fallback: look for "Typically $X–$Y" on same line
    if not price_range:
        for text_node in panel.find_all(string=re.compile(r"Typically")):
            match = re.search(r"Typically\s*(\$[\d,.]+\s*[–-]\s*\$[\d,.]+)", text_node)
            if match:
                price_range = match.group(1)
                break

    # Merchants — extract from the stores listing
    merchants: list[dict] = []
    seen_stores: set[str] = set()
    # Merchant entries typically have: store name, price, product subtitle, delivery info
    # They're in links with external hrefs (walmart.com, target.com, etc.)
    # Skip non-merchant links (YouTube, social media, manufacturer sites, etc.)
    skip_domains = {"youtube.com", "youtu.be", "facebook.com", "instagram.com", "twitter.com", "tiktok.com"}
    for link in panel.select("a[href]"):
        href = link.get("href", "")
        # Skip internal Google links
        if "google.com" in href or href.startswith("/") or href.startswith("#"):
            continue
        # Skip non-merchant domains
        if any(domain in href.lower() for domain in skip_domains):
            continue
        link_text = link.get_text(" ", strip=True)
        if not link_text or len(link_text) < 10:
            continue
        # Extract store name and price from the link text
        price_match = re.search(r"\$\d+(?:\.\d{2})?", link_text)
        if price_match:
            store_price = price_match.group(0)
            # Store name is usually the first word(s) before the price
            store_text_before = link_text[:link_text.index(store_price)].strip()
            # Clean up labels like "Most popular", "Best price"
            store_name = re.sub(r"^(?:Most popular|Best price|Nearby)\s+", "", store_text_before).strip()
            if store_name and len(store_name) < 40 and store_name not in seen_stores:
                seen_stores.add(store_name)
                merchants.append({
                    "store": store_name,
                    "price": store_price,
                    "url": href,
                    "details": link_text[link_text.index(store_price):].strip()[:100],
                })

    # Product images
    image_urls: list[str] = []
    for img in panel.select("img"):
        src = img.get("src") or img.get("data-src")
        if (src and src not in image_urls
                and not src.startswith("data:")
                and "encrypted" in src):
            image_urls.append(src)

    # Review histogram
    histogram: dict[str, int] = {}
    hist_node = panel.select_one("div.liSKFd, div.suYfQc")
    if hist_node:
        hist_text = hist_node.get_text(" ", strip=True)
        for star in range(5, 0, -1):
            match = re.search(rf"{star}\s+([\d,]+)\s*reviews?", hist_text)
            if match:
                histogram[f"{star}_star"] = _extract_int(match.group(1)) or 0

    return {
        "title": title,
        "average_rating": avg_rating,
        "total_reviews": total_reviews,
        "price_range": price_range,
        "merchants": merchants,
        "image_urls": image_urls,
        "histogram": histogram,
    }


def parse_panel_reviews(html: str) -> dict:
    """Extract individual reviews from the Google Shopping SPA overlay panel.

    Reviews appear in the panel's review section, loaded via AJAX after the panel opens.
    Each review has: reviewer name, date, title, body text, source site.
    """
    soup = BeautifulSoup(html, "html.parser")
    panel = _find_panel(soup)
    reviews: list[dict] = []
    warnings: list[str] = []

    if not panel:
        return {"reviews": [], "has_more": False, "warnings": ["no panel found"]}

    # Find the reviews section within the panel
    review_section = panel.select_one('[jsname="UtT7xe"], div.zzkrfd')
    if not review_section:
        review_section = panel

    # Extract reviews by finding reviewer names + associated content
    # Reviews follow a pattern: reviewer_name -> date -> title -> body -> source
    panel_text = review_section.get_text("\n", strip=True)
    lines = [line.strip() for line in panel_text.split("\n") if line.strip()]

    # Review structure per the actual DOM (text lines):
    #   [N]   Reviewer name (e.g. "PickyPurrchaser")
    #   [N+1] Star rating as digit (e.g. "4")
    #   [N+2] Date (e.g. "2 months ago")
    #   [N+3] Review title (optional)
    #   [N+4] Review body text
    #   [N+5] "More" (expand button — skip)
    #   [N+6] Full body text (duplicate of N+4 but expanded — skip if same)
    #   [N+7] "Less" (collapse button — skip)
    #   [N+8] "Reviewed on walmart.com"
    #   [N+9] "Provide feedback"

    date_pattern = re.compile(
        r"^(\d+\s+(?:day|week|month|year)s?\s+ago|a\s+(?:day|week|month|year)\s+ago|yesterday|\d{1,2}/\d{1,2}/\d{2,4})",
        re.IGNORECASE,
    )
    skip_labels = {"User reviews", "All reviews", "Most relevant", "Most recent",
                   "Non-incentivized only", "More reviews", "Provide feedback",
                   "More", "Less"}

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip known non-review lines
        if line in skip_labels or line.endswith("star") or re.match(r"^[\d,]+\s*reviews?$", line):
            i += 1
            continue
        if re.match(r"^\d+\+?$", line) or line.startswith("(function"):
            i += 1
            continue

        # Detect review start: name -> star_rating(digit) -> date
        # Or: name -> date (if star rating is rendered via CSS, not text)
        if (re.match(r"^[A-Za-z]", line)
                and not line.startswith("$")
                and not line.startswith("Reviewed")
                and not line.startswith("Sort")
                and len(line) < 50
                and i + 2 < len(lines)):

            rating = None
            date_line_idx = None

            # Check: name -> digit -> date
            if re.match(r"^[1-5]$", lines[i + 1]) and date_pattern.match(lines[i + 2]):
                rating = int(lines[i + 1])
                date_line_idx = i + 2
            # Check: name -> date (no star rating in text)
            elif date_pattern.match(lines[i + 1]):
                date_line_idx = i + 1

            if date_line_idx is not None:
                reviewer = line
                date = lines[date_line_idx]
                j = date_line_idx + 1

                # Collect review text lines until "Reviewed on" or end
                review_parts: list[str] = []
                source = None
                while j < len(lines):
                    if lines[j].startswith("Reviewed on"):
                        source = lines[j].replace("Reviewed on ", "")
                        j += 1
                        break
                    if lines[j] in skip_labels:
                        j += 1
                        continue
                    if re.match(r"^[\d,]+\s*reviews?$", lines[j]) or re.match(r"^\d+\+?$", lines[j]):
                        j += 1
                        continue
                    review_parts.append(lines[j])
                    j += 1

                # Deduplicate consecutive identical lines (expanded/collapsed text)
                deduped: list[str] = []
                for part in review_parts:
                    if not deduped or part != deduped[-1]:
                        deduped.append(part)

                review_title = None
                review_body = None
                if deduped:
                    review_title = deduped[0] if len(deduped) > 1 else None
                    body_parts = deduped[1:] if review_title else deduped
                    review_body = " ".join(body_parts) if body_parts else deduped[0]

                if review_body or review_title:
                    reviews.append({
                        "reviewer": reviewer,
                        "rating": rating,
                        "date": date,
                        "title": review_title,
                        "text": review_body or review_title,
                        "source": source,
                        "verified": False,
                    })

                i = j
                continue

        i += 1

    # Check for "More reviews" button
    has_more = bool(panel.find(string=re.compile(r"More reviews")))

    return {
        "reviews": reviews,
        "has_more": has_more,
        "warnings": warnings,
    }
