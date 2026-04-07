"""
HousingLens – ikman.lk Listing Scraper (Phase 1)
=================================================
Parses the `window.initialData` JSON embedded in every ikman.lk listing page.
This gives 100% reliable field extraction (title, slug/URL, bedrooms, bathrooms,
price, district, subcategory, land size from title, timestamp) without dependent
on fragile HTML/CSS class names.

Output: data/raw_listings.csv  (append-mode — safe to resume)

Usage (via run_scraper.py):
    python run_scraper.py --phase 1 --district colombo --max-pages 3
"""

import csv
import json
import logging
import os
import random
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_URL  = "https://ikman.lk"
DATA_DIR  = Path(__file__).parent.parent / "data"
OUT_FILE  = DATA_DIR / "raw_listings.csv"

# All 25 Sri Lankan districts (ikman.lk URL slugs)
DISTRICTS = [
    "colombo", "gampaha", "kalutara",
    "kandy", "matale", "nuwara-eliya",
    "galle", "matara", "hambantota",
    "jaffna", "kilinochchi", "mannar", "vavuniya", "mullaitivu",
    "batticaloa", "ampara", "trincomalee",
    "kurunegala", "puttalam",
    "anuradhapura", "polonnaruwa",
    "badulla", "monaragala",
    "ratnapura", "kegalle",
]

# (url_slug, display_label) pairs
SUBCATEGORIES = [
    ("houses-for-sale",     "House"),
    ("apartments-for-sale", "Apartment"),
    ("land-for-sale",       "Land"),
]

CSV_COLUMNS = [
    "title", "url", "district", "subcategory",
    "price_lkr", "price_raw",
    "bedrooms", "bathrooms",
    "land_size_perches",   # extracted from title when available
    "posted_date", "scraped_at",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://ikman.lk/",
}


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(url: str, session: requests.Session, retries: int = 4):
    """GET with retry + exponential backoff. Returns (html_text, soup) or (None, None)."""
    delay = 2.0
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                return resp.text, soup
            if resp.status_code in (429, 503):
                wait = delay * (2 ** attempt) + random.uniform(1, 3)
                log.warning("Rate limited (%s). Waiting %.0fs…", resp.status_code, wait)
                time.sleep(wait)
            else:
                log.warning("HTTP %s → %s", resp.status_code, url)
                return None, None
        except requests.RequestException as exc:
            log.warning("Request error (attempt %d/%d): %s", attempt, retries, exc)
            time.sleep(delay * attempt)
    log.error("All retries failed for %s", url)
    return None, None


# ── JSON extraction ───────────────────────────────────────────────────────────

def _extract_initial_data(html: str) -> dict | None:
    """
    ikman.lk embeds all listing data as:
        window.initialData = { ... };
    on a single long line in the page HTML.
    We use brace-counting to robustly extract the JSON object.
    """
    marker = "window.initialData = "
    start_idx = html.find(marker)
    if start_idx == -1:
        return None

    json_start = html.find("{", start_idx)
    if json_start == -1:
        return None

    # Brace-counting to find the matching closing brace
    depth = 0
    in_string = False
    escape_next = False
    i = json_start
    while i < len(html):
        ch = html[i]
        if escape_next:
            escape_next = False
        elif ch == "\\" and in_string:
            escape_next = True
        elif ch == '"' and not escape_next:
            in_string = not in_string
        elif not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    json_str = html[json_start: i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError as e:
                        log.debug("JSON parse error at pos %d: %s", i, e)
                        return None
        i += 1
    return None


def _get_ads_from_data(data: dict) -> list[dict]:
    """Navigate the initialData structure to get the ads list."""
    try:
        serp = data.get("serp", {})
        ads_obj = serp.get("ads", {})
        if ads_obj.get("type") != "Success":
            return []
        ads = ads_obj.get("data", {}).get("ads", [])
        top_ads = ads_obj.get("data", {}).get("topAds", [])
        return top_ads + ads  # include featured/top ads too
    except (AttributeError, KeyError, TypeError):
        return []


def _has_next_page_json(data: dict, current_page: int) -> bool:
    """Check pagination data from initialData."""
    try:
        pagination = (
            data.get("serp", {})
                .get("ads", {})
                .get("data", {})
                .get("paginationData", {})
        )
        total = pagination.get("total", 0)
        page_size = pagination.get("pageSize", 25)
        max_page = (total + page_size - 1) // page_size
        return current_page < max_page
    except (AttributeError, KeyError, TypeError):
        return False


# ── Field parsers ─────────────────────────────────────────────────────────────

def _parse_price(price_text: str) -> tuple[float | None, str]:
    """Parse 'Rs 37,500,000' → (37500000.0, 'Rs 37,500,000')."""
    raw = price_text.strip()
    cleaned = re.sub(r"[Rrs,\s]", "", raw)
    cleaned = re.sub(r"(perperch|totalprice|/month.*)", "", cleaned, flags=re.I)
    try:
        return float(cleaned), raw
    except ValueError:
        return None, raw


def _parse_beds_baths(details_text: str) -> tuple[int | None, int | None]:
    """Parse 'Bedrooms: 4, Bathrooms: 3' → (4, 3)."""
    beds = baths = None
    m = re.search(r"[Bb]edrooms?\s*:?\s*(\d+)", details_text)
    if m:
        beds = int(m.group(1))
    m = re.search(r"[Bb]athrooms?\s*:?\s*(\d+)", details_text)
    if m:
        baths = int(m.group(1))
    return beds, baths


def _extract_land_from_title(title: str) -> float | None:
    """Try to extract perch count from listing title, e.g. '12.7 Perches'."""
    m = re.search(r"(\d+\.?\d*)\s*(?:perch(?:es)?|P)\b", title, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _ad_to_row(ad: dict, district: str, subcategory: str) -> dict | None:
    """Convert a single ad object from initialData to a CSV row dict."""
    try:
        slug = ad.get("slug", "")
        if not slug:
            return None
        url = f"{BASE_URL}/en/ad/{slug}"

        title = ad.get("title", "")
        price_text = ad.get("price", "")
        price_lkr, price_raw = _parse_price(price_text) if price_text else (None, "")

        details = ad.get("details", "")          # "Bedrooms: 4, Bathrooms: 3"
        beds, baths = _parse_beds_baths(details)

        land_size = _extract_land_from_title(title)

        timestamp = ad.get("lastBumpUpDate") or ad.get("timeStamp", "")

        return {
            "title":             title,
            "url":               url,
            "district":          district,
            "subcategory":       subcategory,
            "price_lkr":         price_lkr,
            "price_raw":         price_raw,
            "bedrooms":          beds,
            "bathrooms":         baths,
            "land_size_perches": land_size,
            "posted_date":       timestamp,
            "scraped_at":        datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as exc:
        log.debug("Ad parse error: %s", exc)
        return None


# ── CSV helpers ───────────────────────────────────────────────────────────────

def _load_seen_urls(path: Path) -> set[str]:
    seen = set()
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("url"):
                    seen.add(row["url"])
    log.info("Loaded %d already-scraped URLs from %s", len(seen), path.name)
    return seen


def _append_rows(rows: list[dict], path: Path) -> None:
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


# ── Main runner ───────────────────────────────────────────────────────────────

def run(
    districts: list[str] | None = None,
    subcategories: list[tuple] | None = None,
    max_pages: int = 999,
    delay_min: float = 1.5,
    delay_max: float = 3.0,
) -> int:
    """
    Run Phase 1: scrape all listing cards via window.initialData JSON.

    Returns
    -------
    Total number of new rows written.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    districts     = districts or DISTRICTS
    subcategories = subcategories or SUBCATEGORIES
    seen_urls     = _load_seen_urls(OUT_FILE)
    session       = requests.Session()
    total_new     = 0

    for district in districts:
        for url_slug, label in subcategories:
            log.info("▶ %s / %s", district.capitalize(), label)
            page = 1

            while page <= max_pages:
                url = (
                    f"{BASE_URL}/en/ads/{district}/{url_slug}"
                    f"?sort=date&order=desc&page={page}"
                )
                log.info("  Page %d → %s", page, url)

                html, soup = _get(url, session)
                if html is None:
                    log.warning("  Fetch failed — skipping page %d", page)
                    break

                data = _extract_initial_data(html)
                if data is None:
                    log.warning("  No initialData found on page %d — skipping", page)
                    break

                ads = _get_ads_from_data(data)
                if not ads:
                    log.info("  No ads on page %d — done with %s / %s", page, district, label)
                    break

                rows = [_ad_to_row(ad, district.capitalize(), label) for ad in ads]
                rows = [r for r in rows if r is not None]

                new_rows = [r for r in rows if r["url"] not in seen_urls]
                for r in new_rows:
                    seen_urls.add(r["url"])

                if new_rows:
                    _append_rows(new_rows, OUT_FILE)
                    total_new += len(new_rows)
                    log.info("  ✓ %d new rows (page %d, %d total ads found)", len(new_rows), page, len(ads))
                else:
                    log.info("  No new rows on page %d — stopping.", page)
                    break

                if not _has_next_page_json(data, page):
                    log.info("  No next page — done with %s / %s", district, label)
                    break

                page += 1
                time.sleep(random.uniform(delay_min, delay_max))

    log.info("Phase 1 complete. Total new rows: %d → %s", total_new, OUT_FILE)
    return total_new
