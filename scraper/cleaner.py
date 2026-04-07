"""
HousingLens – Data Cleaning Pipeline (Phase 3)
===============================================
Reads enriched_listings.csv (or raw_listings.csv if enriched not available),
applies cleaning rules, and saves a ready-to-train dataset.

Cleaning steps:
  1. Normalise price → numeric LKR (drop "per perch" land entries for ML)
  2. Normalise district → canonical Sri Lankan district name
  3. Filter: keep only House and Apartment subcategories for ML model
  4. Drop rows with missing price, district, or bedrooms
  5. Remove obvious price outliers (< 500k or > 500M LKR)
  6. Deduplicate by URL
  7. Save → data/cleaned_listings.csv

Output columns:
    title, url, district, subcategory, price_lkr,
    bedrooms, bathrooms, land_size_perches, floor_area_sqft, scraped_at
"""

import logging
import re
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

DATA_DIR    = Path(__file__).parent.parent / "data"
IN_FILE     = DATA_DIR / "enriched_sync.csv"
FALLBACK    = DATA_DIR / "raw_listings.csv"
OUT_FILE    = DATA_DIR / "cleaned_listings.csv"

# Canonical district name mapping (handles slug → display name)
DISTRICT_MAP = {
    "colombo":        "Colombo",
    "gampaha":        "Gampaha",
    "kalutara":       "Kalutara",
    "kandy":          "Kandy",
    "matale":         "Matale",
    "nuwara-eliya":   "Nuwara Eliya",
    "nuwaraeliya":    "Nuwara Eliya",
    "nuwara eliya":   "Nuwara Eliya",
    "galle":          "Galle",
    "matara":         "Matara",
    "hambantota":     "Hambantota",
    "jaffna":         "Jaffna",
    "kilinochchi":    "Kilinochchi",
    "mannar":         "Mannar",
    "vavuniya":       "Vavuniya",
    "mullaitivu":     "Mullaitivu",
    "batticaloa":     "Batticaloa",
    "ampara":         "Ampara",
    "trincomalee":    "Trincomalee",
    "kurunegala":     "Kurunegala",
    "puttalam":       "Puttalam",
    "anuradhapura":   "Anuradhapura",
    "polonnaruwa":    "Polonnaruwa",
    "badulla":        "Badulla",
    "monaragala":     "Monaragala",
    "ratnapura":      "Ratnapura",
    "kegalle":        "Kegalle",
}


def _normalise_district(s: str | None) -> str | None:
    if not s:
        return None
    key = s.strip().lower()
    return DISTRICT_MAP.get(key, s.title())


def _clean_price(val) -> float | None:
    """Ensure price is a positive float; try parsing strings."""
    if pd.isna(val):
        return None
    try:
        f = float(str(val).replace(",", "").strip())
        return f if f > 0 else None
    except (ValueError, TypeError):
        return None


def run() -> int:
    """Run the cleaning pipeline. Returns number of clean rows saved."""
    # Load both sources and combine them to maximize training data
    dfs = []
    
    if FALLBACK.exists():
        log.info("Loading %s…", FALLBACK.name)
        dfs.append(pd.read_csv(FALLBACK, low_memory=False))
        
    if IN_FILE.exists():
        log.info("Loading %s…", IN_FILE.name)
        dfs.append(pd.read_csv(IN_FILE, low_memory=False))
        
    if not dfs:
        log.error("No input data found matching %s or %s. Run Phase 1 first.", IN_FILE, FALLBACK)
        return 0

    df = pd.concat(dfs, ignore_index=True)
    
    # Deduplicate early by URL, keeping the enriched data (which is appended later)
    df = df.drop_duplicates(subset=["url"], keep="last")
    log.info("Combined raw rows: %d", len(df))

    # ── 1. Price ─────────────────────────────────────────────────────────────
    df["price_lkr"] = df["price_lkr"].apply(_clean_price)

    # ── 2. District normalise ────────────────────────────────────────────────
    df["district"] = df["district"].apply(_normalise_district)

    # ── 3. Subcategory filter (keep House + Apartment only) ──────────────────
    df = df[df["subcategory"].isin(["House", "Apartment"])].copy()
    log.info("After subcategory filter: %d rows", len(df))

    # ── 3.5 Extract City from Title ──────────────────────────────────────────
    SRI_LANKA_CITIES = [
        # Colombo - Numbered zones
        "Colombo 1", "Colombo 2", "Colombo 3", "Colombo 4", "Colombo 5",
        "Colombo 6", "Colombo 7", "Colombo 8", "Colombo 9", "Colombo 10",
        "Colombo 11", "Colombo 12", "Colombo 13", "Colombo 14", "Colombo 15",
        # Colombo - Southern suburbs
        "Dehiwala", "Mount Lavinia", "Moratuwa", "Rathmalana", "Ratmalana",
        "Kohuwala", "Nugegoda", "Maharagama", "Pannipitiya", "Kottawa",
        "Homagama", "Piliyandala", "Kesbewa", "Boralesgamuwa",
        # Colombo - Eastern suburbs
        "Pelawatte", "Battaramulla", "Battharamulla", "Thalawathugoda", "Talawatugoda",
        "Malabe", "Athurugiriya", "Kaduwela", "Rajagiriya", "Nawala", "Kotte",
        "Pitakotte", "Ethul Kotte", "Wellampitiya", "Kolonnawa", "Angoda",
        "Mulleriyawa", "Gothatuwa", "Koswatta", "Hokandara",
        # Colombo - Northern/Central suburbs
        "Padukka", "Hanwella", "Avissawella", "Madiwela", "Meegoda", "Godagama",
        "Mattegoda", "Polgasowita", "Papiliyana", "Depanama", "Makumbura",
        "Diyagama", "Attidiya", "Bokundara", "Kahathuduwa",
        # Gampaha
        "Gampaha", "Negombo", "Wattala", "Ja-Ela", "Kelaniya", "Peliyagoda",
        "Kadawatha", "Kiribathgoda", "Ragama", "Ganemulla", "Kandana",
        "Katunayake", "Minuwangoda", "Mirigama", "Veyangoda", "Nittambuwa",
        "Divulapitiya", "Dankotuwa", "Attanagalla", "Biyagama", "Dompe",
        "Hendala", "Ekala", "Mahara", "Kotugoda", "Seeduwa", "Liyanagemulla",
        "Pamunugama", "Udugampola", "Yakkala", "Delgoda", "Pugoda", "Mabole",
        "Thalahena",
        # Kalutara
        "Kalutara", "Panadura", "Beruwala", "Horana", "Bandaragama",
        "Aluthgama", "Matugama", "Agalawatta", "Dodangoda", "Ingiriya",
        "Palindanuwara", "Bulathsinhala", "Millaniya", "Walallavita",
        "Madurawala", "Bombuwala", "Neboda", "Payagala", "Wadduwa",
        "Baduraliya", "Katukurunda", "Dharga Town", "Maggona",
        # Kandy
        "Kandy", "Peradeniya", "Katugastota", "Digana", "Kundasale",
        "Lewella", "Ampitiya", "Gampola", "Nawalapitiya", "Hatton",
        "Teldeniya", "Akurana", "Pallekele", "Wattegama", "Daulagala",
        "Kadugannawa", "Pilimathalawa", "Gelioya", "Poojapitiya",
        # Matale
        "Matale", "Dambulla", "Sigiriya", "Rattota", "Ukuwela",
        "Pallepola", "Galewela", "Nalanda", "Laggala", "Wilgamuwa",
        "Palapathwela", "Elkaduwa", "Naula",
        # Nuwara Eliya
        "Nuwara Eliya", "Talawakele", "Maskeliya", "Ragala", "Walapane",
        "Kotmale", "Hanguranketha", "Udapussellawa", "Lindula",
        "Bogawanthalawa", "Dickoya", "Kotagala", "Ginigathena", "Norwood",
        # Galle
        "Galle", "Hikkaduwa", "Ambalangoda", "Elpitiya", "Bentota",
        "Balapitiya", "Karandeniya", "Habaraduwa", "Akmeemana", "Baddegama",
        "Imaduwa", "Niyagama", "Wanduramba", "Rathgama", "Koggala",
        "Unawatuna",
        # Matara
        "Matara", "Weligama", "Dikwella", "Akuressa", "Hakmana",
        "Kamburupitiya", "Mulatiyana", "Malimbada", "Pasgoda", "Pitabeddara",
        "Thihagoda", "Welipitiya", "Athuraliya", "Devinuwara", "Mirissa",
        "Polhena",
        # Hambantota
        "Hambantota", "Tangalle", "Tissamaharama", "Beliatta", "Weeraketiya",
        "Ambalantota", "Katuwana", "Okewela", "Hungama", "Angunakolapelessa",
        "Walasmulla", "Suriyawewa",
        # Jaffna
        "Jaffna", "Nallur", "Chavakachcheri", "Point Pedro", "Manipay",
        "Kopay", "Nelliady", "Karainagar", "Velanai", "Kayts", "Sandilipay",
        "Uduvil", "Vaddukoddai", "Chankanai",
        # Kilinochchi
        "Kilinochchi", "Palai", "Poonakary", "Karachchi", "Pachchilaipalli",
        "Kandavalai",
        # Mannar
        "Mannar", "Nanatan", "Musali", "Madhu", "Manthai West", "Pesalai",
        # Vavuniya
        "Vavuniya", "Cheddikulam", "Vengalacheddikulam",
        # Mullaitivu
        "Mullaitivu", "Oddusuddan", "Puthukkudiyiruppu", "Thunukkai", "Welioya",
        # Batticaloa
        "Batticaloa", "Kattankudy", "Eravur", "Valaichchenai", "Chenkaladi",
        "Vavunathivu",
        # Ampara
        "Ampara", "Kalmunai", "Sainthamaruthu", "Pottuvil", "Akkaraipattu",
        "Ninthavur", "Addalaichenai", "Sammanthurai", "Mahaoya", "Uhana",
        "Damana", "Dehiattakandiya", "Padiyathalawa", "Navithanveli", "Thirukkovil",
        # Trincomalee
        "Trincomalee", "Kinniya", "Kantale", "Muttur", "Seruvila", "Morawewa",
        "Gomarankadawala", "Kuchchaveli", "China Bay",
        # Kurunegala
        "Kurunegala", "Kuliyapitiya", "Nikaweratiya", "Mawathagama",
        "Narammala", "Pannala", "Alawwa", "Hettipola", "Wariyapola",
        "Galgamuwa", "Ibbagamuwa", "Kotavehera", "Polpithigama", "Ridigama",
        "Mahawa", "Yapahuwa", "Polgahawela", "Bingiriya", "Dodangaslanda",
        "Ganewatta", "Rasnayakapura",
        # Puttalam
        "Puttalam", "Chilaw", "Wennappuwa", "Marawila", "Nattandiya",
        "Anamaduwa", "Nawagattegama", "Mundel", "Arachchikattuwa", "Kalpitiya",
        "Pallama",
        # Anuradhapura
        "Anuradhapura", "Kekirawa", "Medawachchiya", "Eppawala",
        "Tambuttegama", "Nochchiyagama", "Horowpothana",
        "Padaviya", "Rajanganaya", "Thirappane", "Kahatagasdigiliya",
        "Mahavilachchiya", "Thalawa", "Mihintale",
        # Polonnaruwa
        "Polonnaruwa", "Kaduruwela", "Hingurakgoda", "Medirigiriya",
        "Habarana", "Welikanda", "Elahera",
        # Badulla
        "Badulla", "Bandarawela", "Haputale", "Welimada", "Mahiyanganaya",
        "Passara", "Hali-Ela", "Ella", "Diyatalawa", "Meegahakiula",
        "Lunugala", "Kandaketiya", "Ridimaliyadda",
        # Monaragala
        "Monaragala", "Bibile", "Wellawaya", "Buttala", "Medagama",
        "Kataragama", "Thanamalwila", "Badalkumbura", "Sewanagala", "Siyambalanduwa",
        # Ratnapura
        "Ratnapura", "Embilipitiya", "Balangoda", "Pelmadulla",
        "Eheliyagoda", "Kuruwita", "Godakawela", "Imbulpe", "Kahawatta",
        "Kolonne", "Kiriella", "Ayagama", "Nivitigala", "Weligepola",
        # Kegalle
        "Kegalle", "Mawanella", "Warakapola", "Aranayaka", "Rambukkana",
        "Ruwanwella", "Dehiowita", "Yatiyanthota", "Galigamuwa",
        "Deraniyagala", "Bulathkohupitiya", "Kitulgala",
    ]
    city_patterns = {c.lower(): c for c in SRI_LANKA_CITIES}
    
    def _extract_city(title):
        if not isinstance(title, str):
            return "Unknown"
        title_lower = title.lower()
        for k, v in city_patterns.items():
            if re.search(r'\b' + re.escape(k) + r'\b', title_lower):
                return v
        return "Unknown"

    df["city"] = df["title"].apply(_extract_city)

    # ── 4. Drop missing essentials ───────────────────────────────────────────
    df = df.dropna(subset=["price_lkr", "district"])
    df = df[df["bedrooms"].notna() | df["subcategory"].eq("Apartment")]
    log.info("After dropping nulls: %d rows", len(df))

    # ── 5. Price outlier removal ─────────────────────────────────────────────
    df = df[(df["price_lkr"] >= 500_000) & (df["price_lkr"] <= 500_000_000)]
    log.info("After outlier removal: %d rows", len(df))

    # ── 6. Deduplicate by URL ────────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset=["url"])
    log.info("Removed %d duplicates. Final: %d rows", before - len(df), len(df))

    # ── 7. Cast types ────────────────────────────────────────────────────────
    for col in ["bedrooms", "bathrooms"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in ["land_size_perches", "floor_area_sqft"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 8. Final column set ──────────────────────────────────────────────────
    keep = [c for c in [
        "title", "url", "district", "city", "subcategory",
        "price_lkr", "bedrooms", "bathrooms",
        "land_size_perches", "floor_area_sqft", "scraped_at",
    ] if c in df.columns]
    df = df[keep]

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    log.info("Saved %d clean rows → %s", len(df), OUT_FILE)

    # Summary stats
    log.info("── District distribution ──")
    for dist, cnt in df["district"].value_counts().head(10).items():
        log.info("  %-20s %d", dist, cnt)
    log.info("── Price range ──")
    log.info("  Min: Rs %.0f  |  Median: Rs %.0f  |  Max: Rs %.0f",
             df["price_lkr"].min(), df["price_lkr"].median(), df["price_lkr"].max())

    return len(df)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    run()
