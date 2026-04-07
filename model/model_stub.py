"""
HousingLens – Model Stub
-------------------------
Provides a realistic heuristic-based prediction in place of a trained ML model.
This stub will be swapped out for the real pickled model in a later sprint.

The heuristic is approximately derived from:
  - District-level base price per perch (LKR)
  - Floor area multiplier (LKR per sqft)
  - Room count adjustments
  - Property type multiplier
  - Geospatial proximity bonuses (if OSM features are provided)
"""

import numpy as np
import math
from typing import Optional


# ---------------------------------------------------------------------------
# District base prices (LKR per perch, approximate 2024 market data)
# ---------------------------------------------------------------------------
DISTRICT_BASE_PRICE_PER_PERCH: dict[str, float] = {
    "Colombo":       4_500_000,
    "Gampaha":       2_200_000,
    "Kalutara":      1_800_000,
    "Kandy":         1_600_000,
    "Galle":         1_900_000,
    "Matara":        1_200_000,
    "Nuwara Eliya":    900_000,
    "Ratnapura":       750_000,
    "Kegalle":         700_000,
    "Jaffna":          950_000,
    "Kurunegala":      800_000,
    "Puttalam":        650_000,
    "Anuradhapura":    600_000,
    "Polonnaruwa":     550_000,
    "Badulla":         650_000,
    "Monaragala":      450_000,
    "Hambantota":      850_000,
    "Trincomalee":     750_000,
    "Batticaloa":      650_000,
    "Ampara":          550_000,
    "Vavuniya":        500_000,
    "Mannar":          480_000,
    "Mullaitivu":      420_000,
    "Kilinochchi":     430_000,
    "Matale":          600_000,
}

DEFAULT_PRICE_PER_PERCH: float = 700_000

# Price per sqft of floor area (LKR)
PRICE_PER_SQFT: float = 18_000

# Property type multipliers
PROPERTY_TYPE_MULTIPLIER: dict[str, float] = {
    "House":              1.0,
    "Villa":              1.35,
    "Apartment":          0.85,
    "Land":               0.0,   # land only → no floor area component
    "Commercial Property":1.20,
    "Bare Land":          0.0,
}

# Bedroom adjustment (marginal LKR per extra bedroom beyond 1)
BED_ADJUSTMENT: float = 1_500_000

# Bathroom adjustment
BATH_ADJUSTMENT: float = 800_000

# OSM proximity bonuses (LKR)
OSM_SCHOOL_BONUS:    float =  800_000
OSM_HOSPITAL_BONUS:  float =  600_000
OSM_MAINROAD_BONUS:  float =  500_000
OSM_AMENITY_BONUS:   float =  300_000   # per 10 nearby amenities (capped)

# Noise factor (controlled CV → drives IRI)
_RNG = np.random.default_rng(seed=42)


def predict(inputs: dict) -> dict:
    """
    Generate a mock property price prediction.

    Parameters
    ----------
    inputs : dict
        Keys:
            district       (str)  : e.g. 'Colombo'
            property_type  (str)  : e.g. 'House'
            land_size      (float): perches
            floor_area     (float): sqft
            bedrooms       (int)
            bathrooms      (int)
            osm_school     (bool) : is nearest school < 1 km?
            osm_hospital   (bool) : is nearest hospital < 2 km?
            osm_mainroad   (bool) : is nearest main road < 0.5 km?
            osm_amenities  (int)  : count of amenities within 1 km

    Returns
    -------
    dict
        {
          'price': float,              # LKR
          'prediction_variance': float,# variance (std_dev²)
          'price_range_low': float,
          'price_range_high': float,
          'feature_importances': dict  # feature name → importance score
        }
    """
    district      = inputs.get("district", "Colombo")
    prop_type     = inputs.get("property_type", "House")
    land_size     = float(inputs.get("land_size", 10))
    floor_area    = float(inputs.get("floor_area", 1200))
    bedrooms      = int(inputs.get("bedrooms", 3))
    bathrooms     = int(inputs.get("bathrooms", 2))
    osm_school    = bool(inputs.get("osm_school", False))
    osm_hospital  = bool(inputs.get("osm_hospital", False))
    osm_mainroad  = bool(inputs.get("osm_mainroad", False))
    osm_amenities = int(inputs.get("osm_amenities", 0))

    # --- Land component ---
    base_ppperch = DISTRICT_BASE_PRICE_PER_PERCH.get(district, DEFAULT_PRICE_PER_PERCH)
    land_value   = base_ppperch * land_size

    # --- Structure component ---
    type_mult    = PROPERTY_TYPE_MULTIPLIER.get(prop_type, 1.0)
    floor_value  = PRICE_PER_SQFT * floor_area * type_mult

    # --- Room adjustments ---
    bed_val  = BED_ADJUSTMENT  * max(0, bedrooms  - 1)
    bath_val = BATH_ADJUSTMENT * max(0, bathrooms - 1)

    # --- OSM bonuses ---
    osm_val  = 0.0
    osm_val += OSM_SCHOOL_BONUS   if osm_school   else 0
    osm_val += OSM_HOSPITAL_BONUS if osm_hospital  else 0
    osm_val += OSM_MAINROAD_BONUS if osm_mainroad  else 0
    osm_val += OSM_AMENITY_BONUS  * (min(osm_amenities, 50) / 10)

    # --- Total estimate ---
    price = land_value + floor_value + bed_val + bath_val + osm_val
    price = max(price, 1_000_000)  # floor: 1M LKR

    # --- Variance model ---
    # Variance increases for rural districts and larger prices
    district_uncertainty = 1.0 - (base_ppperch / 4_500_000)  # 0 (Colombo) → 1 (most rural)
    base_cv = 0.08 + 0.22 * district_uncertainty             # 8% – 30% CV
    std_dev  = base_cv * price
    variance = std_dev ** 2

    # Simulated price range (±1 std dev)
    price_low  = max(price - std_dev, 500_000)
    price_high = price + std_dev

    # --- Feature importances (mock %) ---
    total = land_value + floor_value + bed_val + bath_val + osm_val
    total = max(total, 1)
    importances = {
        "Location (District)": round(100 * land_value / total, 1),
        "Floor Area":           round(100 * floor_value / total, 1),
        "Bedrooms":             round(100 * bed_val  / total, 1),
        "Bathrooms":            round(100 * bath_val / total, 1),
        "OSM / Proximity":      round(100 * osm_val  / total, 1),
    }

    return {
        "price":               price,
        "prediction_variance": variance,
        "price_range_low":     price_low,
        "price_range_high":    price_high,
        "feature_importances": importances,
    }


def format_lkr(value: float) -> str:
    """Format a float as a LKR string (e.g. 'LKR 12,500,000')."""
    return f"LKR {value:,.0f}"


def format_lkr_short(value: float) -> str:
    """Compact LKR formatter (e.g. 'LKR 12.5M')."""
    if value >= 1_000_000:
        return f"LKR {value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"LKR {value/1_000:.1f}K"
    return f"LKR {value:,.0f}"
