"""
HousingLens – Scraper CLI Runner
=================================
Orchestrates the three scraping phases.

Usage examples:
    # Full run (all districts, all phases): 
    python run_scraper.py

    # Phase 1 only (listing cards):
    python run_scraper.py --phase 1

    # Smoke test — one district, 3 pages:
    python run_scraper.py --phase 1 --district colombo --max-pages 3

    # Single district across all pages:
    python run_scraper.py --phase 1 --district kandy

    # Phase 2 — enrich detail pages (run after Phase 1):
    python run_scraper.py --phase 2

    # Phase 3 — clean data (run after Phase 1 or 2):
    python run_scraper.py --phase 3

    # All phases end-to-end:
    python run_scraper.py --phase all
"""

import argparse
import logging
import sys
from pathlib import Path

# ── Ensure data dir exists before log file is created ────────────────────────
Path("data").mkdir(exist_ok=True)

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/scraper.log", mode="a", encoding="utf-8"),
    ],
)

log = logging.getLogger(__name__)



def main():
    parser = argparse.ArgumentParser(
        description="HousingLens ikman.lk data scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--phase",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which phase to run (default: all)",
    )
    parser.add_argument(
        "--district",
        default=None,
        help="Scrape a single district only (e.g. colombo). Default: all 25.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=999,
        help="Max pages per district/subcategory (default: 999 = unlimited).",
    )
    parser.add_argument(
        "--delay-min",
        type=float,
        default=1.5,
        help="Min delay between requests in seconds (default: 1.5).",
    )
    parser.add_argument(
        "--delay-max",
        type=float,
        default=3.0,
        help="Max delay between requests in seconds (default: 3.0).",
    )
    args = parser.parse_args()

    districts = [args.district] if args.district else None

    log.info("=" * 60)
    log.info("HousingLens Scraper — Phase: %s", args.phase)
    if args.district:
        log.info("District filter: %s", args.district)
    log.info("Max pages: %s", args.max_pages)
    log.info("=" * 60)

    # ── Phase 1 ───────────────────────────────────────────────────────────────
    if args.phase in ("1", "all"):
        log.info("\n▶▶ PHASE 1: Listing card scraper\n")
        from scraper.ikman_scraper import run as run_phase1
        n = run_phase1(
            districts=districts,
            max_pages=args.max_pages,
            delay_min=args.delay_min,
            delay_max=args.delay_max,
        )
        log.info("Phase 1 done. %d new rows collected.\n", n)

    # ── Phase 2 ───────────────────────────────────────────────────────────────
    if args.phase in ("2", "all"):
        log.info("\n▶▶ PHASE 2: Detail page enricher\n")
        from scraper.detail_enricher import run as run_phase2
        n = run_phase2(
            delay_min=args.delay_min,
            delay_max=args.delay_max,
        )
        log.info("Phase 2 done. %d rows enriched.\n", n)

    # ── Phase 3 ───────────────────────────────────────────────────────────────
    if args.phase in ("3", "all"):
        log.info("\n▶▶ PHASE 3: Data cleaning pipeline\n")
        from scraper.cleaner import run as run_phase3
        n = run_phase3()
        log.info("Phase 3 done. %d clean rows ready for ML.\n", n)

    log.info("All requested phases complete.")


if __name__ == "__main__":
    main()
