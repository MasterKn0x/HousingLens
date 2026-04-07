import csv
import random
import time
from datetime import datetime
from pathlib import Path
import sys
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.ikman_scraper import _get
from scraper.detail_enricher import _parse_detail_page, IN_FILE, EXTRA_COLUMNS

OUT_SYNC = Path(__file__).parent.parent / "data" / "enriched_sync.csv"

def run_sync(max_rows=300):
    print(f"Starting synchronous enrichment of {max_rows} rows...")
    with open(IN_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_columns = reader.fieldnames or []
        rows = list(reader)
        
    all_columns = raw_columns + [c for c in EXTRA_COLUMNS if c not in raw_columns]
    
    with open(OUT_SYNC, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_columns, extrasaction="ignore")
        writer.writeheader()
        
        with requests.Session() as s:
            for i, row in enumerate(rows[:max_rows], 1):
                url = row.get("url")
                if not url: continue
                
                _, soup = _get(url, s)
                extras = _parse_detail_page(soup) if soup else {
                    "land_size_perches": None,
                    "floor_area_sqft": None,
                    "description": "",
                    "enriched_at": datetime.now().isoformat(timespec="seconds"),
                }
                writer.writerow({**row, **extras})
                
                if i % 10 == 0:
                    f.flush()
                    print(f"Enriched {i} / {max_rows}")
                    
                time.sleep(random.uniform(0.1, 0.3))
                
    print(f"Done! Wrote {max_rows} rows to {OUT_SYNC.name}")

if __name__ == "__main__":
    import sys
    max_rows = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_sync(max_rows)
