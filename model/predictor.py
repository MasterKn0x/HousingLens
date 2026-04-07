"""
HousingLens – Inference Layer
==============================
Drop-in replacement for model_stub.predict() that uses the trained
Gradient Boosting model when model/ml_model.pkl exists.

Falls back to model_stub if the pickle doesn't exist yet.

Interface is identical to model_stub.predict() — same input dict, same output dict.
"""

import logging
import pickle
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)

_PKL_PATH   = Path(__file__).parent / "ml_model.pkl"
_PAYLOAD    = None          # loaded lazily
_STUB_MODE  = False


def _load_model():
    global _PAYLOAD, _STUB_MODE
    if _PAYLOAD is not None:
        return  # already loaded
    if _PKL_PATH.exists():
        try:
            with open(_PKL_PATH, "rb") as f:
                _PAYLOAD = pickle.load(f)
            log.info("Loaded ML model from %s (R²=%.3f, n=%d)",
                     _PKL_PATH.name,
                     _PAYLOAD["metrics"].get("cv_r2_mean", 0),
                     _PAYLOAD["metrics"].get("n_train", 0))
        except Exception as exc:
            log.warning("Failed to load ML model (%s) — falling back to stub", exc)
            _STUB_MODE = True
    else:
        _STUB_MODE = True
        log.info("No trained model found (%s) — using heuristic stub", _PKL_PATH)


# District ordinal mapping (same as train.py)
_DISTRICT_ORDER = [
    "Mullaitivu", "Monaragala", "Mannar", "Kilinochchi", "Vavuniya",
    "Polonnaruwa", "Ampara", "Batticaloa", "Matale", "Puttalam",
    "Anuradhapura", "Badulla", "Trincomalee", "Ratnapura", "Kegalle",
    "Hambantota", "Jaffna", "Kurunegala", "Matara", "Nuwara Eliya",
    "Galle", "Kalutara", "Kandy", "Gampaha", "Colombo",
]
_DISTRICT_MAP = {d: i for i, d in enumerate(_DISTRICT_ORDER)}


def _build_feature_row(inputs: dict, district_stats: dict) -> list[float]:
    """Convert inputs dict → single feature row compatible with model."""
    district   = inputs.get("district", "Colombo")
    city       = inputs.get("city", "Unknown")
    is_apt     = 1 if inputs.get("property_type", "House") == "Apartment" else 0
    bedrooms   = min(max(float(inputs.get("bedrooms", 3)), 1), 10)
    bathrooms  = min(max(float(inputs.get("bathrooms", 2)), 1), 10)
    total_rooms = bedrooms + bathrooms

    # Land size
    land_raw = float(inputs.get("land_size", 8))
    if land_raw <= 0:
        land_raw = district_stats["land_medians"].get(district, 8.0)
    log_land = np.log1p(land_raw)

    # District price median
    global_median = np.median(list(district_stats["price_medians"].values()))
    dist_median   = district_stats["price_medians"].get(district, global_median)
    log_dist_med  = np.log(dist_median)

    # City price median
    city_median   = district_stats.get("city_price_medians", {}).get(city, dist_median)
    log_city_med  = np.log(city_median)

    # District ordinal
    dist_ord = _DISTRICT_MAP.get(district, len(_DISTRICT_ORDER) // 2)

    row = [
        dist_ord,          # district_ord
        is_apt,            # is_apartment
        bedrooms,          # bedrooms
        bathrooms,         # bathrooms
        total_rooms,       # total_rooms
        log_land,          # log_land
        log_dist_med,      # log_district_price_median
        log_city_med,      # log_city_price_median
        bedrooms * log_land,  # beds_x_land
        bathrooms * log_land, # bath_x_land
    ]
    return row


def predict(inputs: dict) -> dict:
    """
    Predict property price.

    Parameters (same as model_stub.predict):
        district, property_type, land_size (perches), floor_area (sqft),
        bedrooms, bathrooms, osm_school, osm_hospital, osm_mainroad, osm_amenities

    Returns:
        price, prediction_variance, price_range_low, price_range_high,
        feature_importances
    """
    _load_model()

    if _STUB_MODE:
        from model.model_stub import predict as stub_predict
        return stub_predict(inputs)

    payload        = _PAYLOAD
    model          = payload["model"]
    district_stats = payload["district_stats"]
    feat_imp       = payload.get("feat_imp", {})

    # Build feature row
    row    = _build_feature_row(inputs, district_stats)
    X_pred = np.array([row], dtype=np.float64)

    # Predict (log-space)
    log_price = model.predict(X_pred)[0]
    price     = np.exp(log_price)

    # Prediction interval: use mean district spread as uncertainty proxy
    district    = inputs.get("district", "Colombo")
    dist_median = district_stats["price_medians"].get(district, price)
    # CV spread scaled by district uncertainty (rural = wider)
    max_median  = max(district_stats["price_medians"].values())
    uncertainty = 1.0 - (dist_median / max_median)         # 0 (Colombo) → 1 (rural)
    cv          = 0.10 + 0.20 * uncertainty                 # 10%–30% CV
    std_dev     = cv * price
    variance    = std_dev ** 2

    price_low  = max(price - std_dev, 500_000)
    price_high = price + std_dev

    # Feature importances — map model features to UI-friendly names
    _FRIENDLY = {
        "log_district_price_median": "Location (District)",
        "log_land":                  "Land Size",
        "district_ord":              "Location (District)",
        "total_rooms":               "Rooms",
        "bedrooms":                  "Bedrooms",
        "bathrooms":                 "Bathrooms",
        "is_apartment":              "Property Type",
        "beds_x_land":               "Beds × Land",
        "bath_x_land":               "Baths × Land",
    }
    merged: dict[str, float] = {}
    for feat, imp in feat_imp.items():
        label = _FRIENDLY.get(feat, feat)
        merged[label] = merged.get(label, 0) + imp

    # Normalise to percentages
    total_imp = sum(merged.values()) or 1
    feature_importances = {k: round(v / total_imp * 100, 1) for k, v in merged.items()}

    return {
        "price":               price,
        "prediction_variance": variance,
        "price_range_low":     price_low,
        "price_range_high":    price_high,
        "feature_importances": feature_importances,
    }


def get_model_info() -> dict:
    """Return metadata about the loaded model."""
    _load_model()
    if _STUB_MODE:
        return {"mode": "stub", "trained": False}
    metrics = _PAYLOAD.get("metrics", {})
    return {
        "mode":       "ml",
        "trained":    True,
        "n_train":    metrics.get("n_train", 0),
        "cv_r2":      round(metrics.get("cv_r2_mean", 0), 3),
        "cv_rmse":    round(metrics.get("cv_rmse_mean", 0)),
        "cv_mae":     round(metrics.get("cv_mae_mean", 0)),
    }
