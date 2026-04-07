"""
HousingLens – Detail Page Enricher (Phase 2)
=============================================
Visits each listing's detail page to extract land size and floor area,
which are only available in the description text.

Input:  data/raw_listings.csv
Output: data/enriched_listings.csv  (resume-safe)

New columns added:
  - land_size_perches  (float)
  - floor_area_sqft    (float)
  - description        (raw text, first 500 chars)
"""

import csv
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper.ikman_scraper import (
    BASE_URL, DATA_DIR, HEADERS, _get
)

log = logging.getLogger(__name__)

IN_FILE  = DATA_DIR / "raw_listings.csv"
OUT_FILE = DATA_DIR / "enriched_listings_v2.csv"

EXTRA_COLUMNS = ["land_size_perches", "floor_area_sqft", "description", "enriched_at"]


# ── Field Parsers ─────────────────────────────────────────────────────────────

def _extract_land_size(text: str) -> float | None:
    """
    Extract land size in perches from free text.
    Handles: '6.5 perch', '10 perches', '15.5 P', '87.8 Perches'
    """
    patterns = [
        r"(\d+\.?\d*)\s*(?:perch(?:es)?|P)\b",
        r"(\d+\.?\d*)\s*perch",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None


def _extract_floor_area(text: str) -> float | None:
    """
    Extract floor area in sqft from free text.
    Handles: '1200 sqft', '1,500 sq.ft', '2000 square feet', '180 sq m'
    Converts sq m → sqft if needed.
    """
    # sqft variants
    m = re.search(r"(\d[\d,]*\.?\d*)\s*(?:sq\.?\s*ft|sqft|square\s*feet)", text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    # sq m → sqft (1 sq m = 10.764 sqft)
    m = re.search(r"(\d[\d,]*\.?\d*)\s*(?:sq\.?\s*m|square\s*met)", text, re.IGNORECASE)
    if m:
        try:
            return round(float(m.group(1).replace(",", "")) * 10.764, 1)
        except ValueError:
            pass
    return None


def _parse_detail_page(soup: BeautifulSoup | None) -> dict:
    """Extract land size, floor area, and description from a detail page."""
    if not soup:
        return {
            "land_size_perches": None,
            "floor_area_sqft":   None,
            "description":       "",
            "enriched_at":       datetime.now().isoformat(timespec="seconds"),
        }

    # Description could be in various containers
    desc_el = (
        soup.select_one('[class*="description"]') or
        soup.select_one('[class*="details"]') or
        soup.find("meta", {"name": "description"})
    )

    if desc_el:
        if desc_el.name == "meta":
            text = desc_el.get("content", "")
        else:
            text = desc_el.get_text(separator=" ", strip=True)
    else:
        # Fall back to full body text
        text = soup.get_text(separator=" ", strip=True)[:2000]

    land  = _extract_land_size(text)
    floor = _extract_floor_area(text)
    desc  = text[:500]

    return {
        "land_size_perches": land,
        "floor_area_sqft":   floor,
        "description":       desc,
        "enriched_at":       datetime.now().isoformat(timespec="seconds"),
    }


# ── Main runner ───────────────────────────────────────────────────────────────

def run(
    max_rows: int = 999_999,
    delay_min: float = 1.5,
    delay_max: float = 3.0,
) -> int:
    """
    Enrich raw_listings.csv with detail-page fields.

    Parameters
    ----------
    max_rows   : maximum number of rows to enrich in this run
    delay_min/max : polite rate-limiting delay

    Returns
    -------
    Number of rows successfully enriched.
    """
    if not IN_FILE.exists():
        log.error("raw_listings.csv not found. Run Phase 1 first.")
        return 0

    # Load already-enriched URLs
    enriched_urls: set[str] = set()
    existing_rows: list[dict] = []
    in_columns: list[str] = []

    if OUT_FILE.exists():
        with open(OUT_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            in_columns = reader.fieldnames or []
            for row in reader:
                existing_rows.append(row)
                enriched_urls.add(row.get("url", ""))
        log.info("Loaded %d already-enriched rows.", len(existing_rows))

    # Read raw listings
    with open(IN_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_columns = reader.fieldnames or []
        raw_rows = list(reader)

    all_columns = raw_columns + [c for c in EXTRA_COLUMNS if c not in raw_columns]
    to_enrich   = [r for r in raw_rows if r["url"] not in enriched_urls]
    to_enrich   = to_enrich[:max_rows]
    log.info("%d rows to enrich.", len(to_enrich))

    session   = requests.Session()
    enriched  = 0
    
    # Write header if needed
    write_header = not OUT_FILE.exists() or OUT_FILE.stat().st_size == 0
    
    out_f = open(OUT_FILE, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_f, fieldnames=all_columns, extrasaction="ignore")
    write_lock = threading.Lock()
    
    if write_header:
        writer.writeheader()
        for row in existing_rows:
            writer.writerow(row)

    def process_row(row):
        url = row.get("url", "")
        if not url:
            return None
        
        # Add random delay per thread to prevent all hitting the server at the exact same ms
        time.sleep(random.uniform(delay_min, delay_max))
        
        # Use a fresh session per thread to avoid connection pool exhaustion
        with requests.Session() as s:
            _, soup = _get(url, s)
            
        extras = _parse_detail_page(soup) if soup else {
            "land_size_perches": None,
            "floor_area_sqft":   None,
            "description":       "",
            "enriched_at":       datetime.now().isoformat(timespec="seconds"),
        }
        return {**row, **extras}

    log.info("Starting enrichment pool with 10 workers...")
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_row, row): row for row in to_enrich}
            
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result()
                    if result:
                        with write_lock:
                            writer.writerow(result)
                            enriched += 1
                        
                        if i % 100 == 0:
                            with write_lock:
                                out_f.flush()
                            log.info("  Enriched %d / %d…", i, len(to_enrich))
                except Exception as exc:
                    log.error("Worker error: %s", exc)
    finally:
        out_f.close()

    log.info("Phase 2 complete. Enriched %d rows → %s", enriched, OUT_FILE)
    return enriched
