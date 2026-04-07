"""
HousingLens – Shared Data Loader
=================================
Centralised loader for the scraped listings CSV and trained model metadata.
Used by all Streamlit pages.  Results are cached so reads happen only once
per session.
"""

import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

log = logging.getLogger(__name__)

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
PKL_PATH = ROOT / "model" / "ml_model.pkl"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _best_csv() -> Path | None:
    """Return the best available listings CSV, in priority order."""
    candidates = [
        DATA_DIR / "cleaned_listings.csv",
        DATA_DIR / "enriched_sync.csv",
        DATA_DIR / "raw_listings.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


# ── Cached loaders ────────────────────────────────────────────────────────────



@st.cache_data(ttl=300, show_spinner=False)   # hot reload trigger
def load_listings() -> pd.DataFrame:
    """
    Load the best available listings CSV.
    Returns an empty DataFrame if no file exists yet.
    """
    path = _best_csv()
    if path is None:
        return pd.DataFrame()

    df = pd.read_csv(path, low_memory=False)

    # Normalise types
    df["price_lkr"]         = pd.to_numeric(df.get("price_lkr"),         errors="coerce")
    df["bedrooms"]          = pd.to_numeric(df.get("bedrooms"),           errors="coerce")
    df["bathrooms"]         = pd.to_numeric(df.get("bathrooms"),          errors="coerce")
    df["land_size_perches"] = pd.to_numeric(df.get("land_size_perches"),  errors="coerce")

    # Capitalise district
    if "district" in df.columns:
        df["district"] = df["district"].str.strip().str.title()

    log.info("Loaded %d rows from %s", len(df), path.name)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_model_metadata() -> dict:
    """
    Load metrics and feature importances from the trained model pickle.
    Returns empty dict if no model exists.
    """
    if not PKL_PATH.exists():
        return {}
    try:
        with open(PKL_PATH, "rb") as f:
            payload = pickle.load(f)
        return {
            "metrics":  payload.get("metrics", {}),
            "feat_imp": payload.get("feat_imp", {}),
        }
    except Exception as exc:
        log.warning("Could not load model metadata: %s", exc)
        return {}


# ── Derived analytics helpers ──────────────────────────────────────────────────

def district_price_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return per-district median, mean, count for House + Apartment listings.
    Sorted by median descending.
    """
    houses = df[df.get("subcategory", pd.Series(dtype=str)).isin(["House", "Apartment"])].copy()
    houses = houses.dropna(subset=["price_lkr", "district"])
    houses = houses[(houses["price_lkr"] >= 1_000_000) & (houses["price_lkr"] <= 600_000_000)]

    summary = (
        houses.groupby("district")["price_lkr"]
        .agg(count="count", median="median", mean="mean")
        .reset_index()
        .sort_values("median", ascending=False)
    )
    summary["median_M"] = summary["median"] / 1_000_000
    summary["mean_M"]   = summary["mean"]   / 1_000_000
    return summary


def price_distribution(df: pd.DataFrame, subcats: list[str] | None = None) -> pd.Series:
    """Return a filtered price series (in LKR millions) for histogram plotting."""
    d = df.copy()
    if subcats:
        d = d[d.get("subcategory", pd.Series(dtype=str)).isin(subcats)]
    d = d.dropna(subset=["price_lkr"])
    d = d[(d["price_lkr"] >= 500_000) & (d["price_lkr"] <= 600_000_000)]
    return d["price_lkr"] / 1_000_000


def dataset_stats(df: pd.DataFrame) -> dict:
    """Compute headline stats dict for the dashboard."""
    if df.empty:
        return {
            "total": 0, "districts": 0, "median_price": 0,
            "houses": 0, "apartments": 0, "land": 0,
            "min_price": 0, "max_price": 0,
        }
    houses = df[df.get("subcategory", pd.Series(dtype=str)).isin(["House", "Apartment"])]
    prices = houses["price_lkr"].dropna()
    prices = prices[(prices >= 1_000_000) & (prices <= 600_000_000)]
    sc = df.get("subcategory", pd.Series(dtype=str)).value_counts().to_dict()
    return {
        "total":       len(df),
        "districts":   df["district"].nunique() if "district" in df else 0,
        "median_price": float(prices.median()) if len(prices) else 0,
        "houses":      sc.get("House", 0),
        "apartments":  sc.get("Apartment", 0),
        "land":        sc.get("Land", 0),
        "min_price":   float(prices.min()) if len(prices) else 0,
        "max_price":   float(prices.max()) if len(prices) else 0,
    }
