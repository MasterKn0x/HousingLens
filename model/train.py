"""
HousingLens – ML Model Training Pipeline
=========================================
Trains a price prediction model on cleaned ikman.lk listings.

Steps:
  1. Load data/cleaned_listings.csv (or raw_listings.csv as fallback)
  2. Feature engineering
  3. Train XGBoost + Random Forest ensemble
  4. Cross-validate (5-fold RMSE, MAE, R²)
  5. Save pickled model + scaler to model/ml_model.pkl
  6. Update model/__init__.py to use real model when pickle exists

Features used:
  - district (label-encoded)
  - subcategory (House=0, Apartment=1)
  - bedrooms, bathrooms
  - land_size_perches (imputed with district median)
  - price_per_perch_district_median (target-encoded)

Target: log(price_lkr)  [log-transform for normality]

Usage:
    python model/train.py
    python model/train.py --data data/cleaned_listings.csv
    python model/train.py --cv-only   # just run CV, don't save
"""

import argparse
import logging
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# ── Setup ─────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_PKL  = Path(__file__).parent / "ml_model.pkl"

# ── District ordering (by avg price, for ordinal encoding) ────────────────────
DISTRICT_ORDER = [
    "Mullaitivu", "Monaragala", "Mannar", "Kilinochchi", "Vavuniya",
    "Polonnaruwa", "Ampara", "Batticaloa", "Matale", "Puttalam",
    "Anuradhapura", "Badulla", "Trincomalee", "Ratnapura", "Kegalle",
    "Hambantota", "Jaffna", "Kurunegala", "Matara", "Nuwara Eliya",
    "Galle", "Kalutara", "Kandy", "Gampaha", "Colombo",
]


# ── Feature engineering ───────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame, district_stats: dict | None = None) -> tuple[pd.DataFrame, dict]:
    """
    Build feature matrix from a cleaned listings DataFrame.

    Parameters
    ----------
    df            : cleaned listings with at minimum: district, subcategory,
                    price_lkr, bedrooms, bathrooms, land_size_perches
    district_stats: pre-computed district stats dict (use from training data;
                    pass at inference time so no data leakage)

    Returns
    -------
    X             : feature DataFrame
    district_stats: dict with computed medians (save alongside model)
    """
    df = df.copy()

    # ── District ordinal encoding ─────────────────────────────────────────────
    district_map = {d: i for i, d in enumerate(DISTRICT_ORDER)}
    df["district_ord"] = df["district"].map(district_map).fillna(len(DISTRICT_ORDER) // 2)

    # ── Subcategory binary ────────────────────────────────────────────────────
    df["is_apartment"] = (df["subcategory"] == "Apartment").astype(int)

    # ── Room features ─────────────────────────────────────────────────────────
    df["bedrooms"]  = pd.to_numeric(df.get("bedrooms"),  errors="coerce").fillna(3).clip(1, 10)
    df["bathrooms"] = pd.to_numeric(df.get("bathrooms"), errors="coerce").fillna(2).clip(1, 10)
    df["total_rooms"] = df["bedrooms"] + df["bathrooms"]

    # ── Land size (impute per district median) ────────────────────────────────
    if district_stats is None:
        # Training time: compute from data
        district_stats = {}
        district_stats["land_medians"] = (
            df.groupby("district")["land_size_perches"]
              .median()
              .fillna(8.0)
              .to_dict()
        )
        # District price medians (target encoding — use with caution, computed on full train set)
        district_stats["price_medians"] = (
            df.groupby("district")["price_lkr"]
              .median()
              .to_dict()
        )
        # City price medians
        if "city" not in df.columns:
            df["city"] = "Unknown"
        district_stats["city_price_medians"] = (
            df.groupby("city")["price_lkr"]
              .median()
              .to_dict()
        )

    global_land_median = np.median(list(district_stats["land_medians"].values()))
    df["land_size_perches"] = df.apply(
        lambda r: r["land_size_perches"]
        if pd.notna(r.get("land_size_perches")) and r["land_size_perches"] > 0
        else district_stats["land_medians"].get(r["district"], global_land_median),
        axis=1,
    )
    df["log_land"] = np.log1p(df["land_size_perches"])

    # ── District price median (target encoding) ───────────────────────────────
    global_price_median = np.median(list(district_stats["price_medians"].values()))
    df["district_price_median"] = (
        df["district"]
        .map(district_stats["price_medians"])
        .fillna(global_price_median)
    )
    df["log_district_price_median"] = np.log(df["district_price_median"])

    # ── City price median (target encoding) ───────────────────────────────────
    if "city" not in df.columns:
        df["city"] = "Unknown"
    
    df["city_price_median"] = df.apply(
        lambda r: district_stats.get("city_price_medians", {}).get(r["city"], r["district_price_median"]),
        axis=1
    )
    df["log_city_price_median"] = np.log(df["city_price_median"])

    # ── Interaction features ──────────────────────────────────────────────────
    df["beds_x_land"] = df["bedrooms"] * df["log_land"]
    df["bath_x_land"] = df["bathrooms"] * df["log_land"]

    feature_cols = [
        "district_ord",
        "is_apartment",
        "bedrooms",
        "bathrooms",
        "total_rooms",
        "log_land",
        "log_district_price_median",
        "log_city_price_median",
        "beds_x_land",
        "bath_x_land",
    ]

    X = df[feature_cols].astype(float)
    return X, district_stats


def load_data(data_path: Path | None) -> pd.DataFrame:
    """Load and minimally validate the dataset."""
    candidates = [
        data_path,
        DATA_DIR / "cleaned_listings.csv",
        DATA_DIR / "raw_listings.csv",
    ]
    for path in candidates:
        if path and Path(path).exists():
            log.info("Loading data from %s", path)
            df = pd.read_csv(path, low_memory=False)
            break
    else:
        log.error("No data file found. Run the scraper (run_scraper.py) first.")
        sys.exit(1)

    required = ["district", "price_lkr"]
    for col in required:
        if col not in df.columns:
            log.error("Missing required column: %s", col)
            sys.exit(1)

    # Keep only House + Apartment
    if "subcategory" in df.columns:
        df = df[df["subcategory"].isin(["House", "Apartment"])].copy()

    # Price filter
    df["price_lkr"] = pd.to_numeric(df["price_lkr"], errors="coerce")
    df = df.dropna(subset=["price_lkr"])
    df = df[(df["price_lkr"] >= 1_000_000) & (df["price_lkr"] <= 600_000_000)]

    # Need at least a district
    df = df.dropna(subset=["district"])

    log.info("Dataset: %d rows after filtering", len(df))
    return df


# ── Training ──────────────────────────────────────────────────────────────────

def train(data_path: Path | None = None, cv_only: bool = False) -> dict | None:
    """
    Train the model and (optionally) save to disk.

    Returns
    -------
    metrics dict with cv_rmse, cv_mae, cv_r2
    """
    df = load_data(data_path)

    if len(df) < 10:
        log.error("Not enough data (%d rows). Need at least 10 House/Apartment rows.", len(df))
        sys.exit(1)

    # Target: log price
    y = np.log(df["price_lkr"].values)

    X, district_stats = engineer_features(df)

    log.info("Feature matrix: %d rows × %d features", X.shape[0], X.shape[1])
    log.info("Features: %s", list(X.columns))

    # ── Model: Gradient Boosting (best single model for tabular house price data)
    model = GradientBoostingRegressor(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=5,
        min_samples_leaf=10,
        subsample=0.8,
        random_state=42,
    )

    # ── 5-fold cross-validation ───────────────────────────────────────────────
    log.info("Running 5-fold cross-validation…")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    cv_rmse_list, cv_mae_list, cv_r2_list = [], [], []
    for fold, (train_idx, val_idx) in enumerate(kf.split(X), 1):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)

        # Metrics on original price scale
        rmse = np.sqrt(mean_squared_error(np.exp(y_val), np.exp(y_pred)))
        mae  = mean_absolute_error(np.exp(y_val), np.exp(y_pred))
        r2   = r2_score(y_val, y_pred)

        cv_rmse_list.append(rmse)
        cv_mae_list.append(mae)
        cv_r2_list.append(r2)
        log.info("  Fold %d: RMSE=Rs %.0f  MAE=Rs %.0f  R²=%.3f", fold, rmse, mae, r2)

    metrics = {
        "cv_rmse_mean": np.mean(cv_rmse_list),
        "cv_rmse_std":  np.std(cv_rmse_list),
        "cv_mae_mean":  np.mean(cv_mae_list),
        "cv_r2_mean":   np.mean(cv_r2_list),
        "n_train":      len(df),
        "features":     list(X.columns),
    }

    log.info("─" * 50)
    log.info("CV Results (5-fold) on %d samples:", len(df))
    log.info("  RMSE:  Rs %.0f ± Rs %.0f", metrics["cv_rmse_mean"], metrics["cv_rmse_std"])
    log.info("  MAE:   Rs %.0f",            metrics["cv_mae_mean"])
    log.info("  R²:    %.3f",               metrics["cv_r2_mean"])

    if cv_only:
        return metrics

    # ── Final model: retrain on ALL data ─────────────────────────────────────
    log.info("Training final model on all %d rows…", len(df))
    model.fit(X, y)

    # Feature importances
    feat_imp = dict(zip(X.columns, model.feature_importances_))
    log.info("Feature importances:")
    for name, imp in sorted(feat_imp.items(), key=lambda x: x[1], reverse=True):
        log.info("  %-35s %.4f", name, imp)

    # Save
    payload = {
        "model":          model,
        "district_stats": district_stats,
        "feature_cols":   list(X.columns),
        "metrics":        metrics,
        "feat_imp":       feat_imp,
    }
    OUT_PKL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PKL, "wb") as f:
        pickle.dump(payload, f)
    log.info("Model saved → %s", OUT_PKL)

    return metrics


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train HousingLens price prediction model")
    parser.add_argument("--data",    default=None, help="Path to CSV data file")
    parser.add_argument("--cv-only", action="store_true", help="Cross-validate only, don't save model")
    args = parser.parse_args()

    data_path = Path(args.data) if args.data else None
    train(data_path=data_path, cv_only=args.cv_only)
