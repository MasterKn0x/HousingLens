"""
HousingLens – IRI Calculator
-----------------------------
Converts a model's prediction variance into a 1-10 Investment Risk Index (IRI).

Formula rationale:
  - Coefficient of variation (CV) = std_dev / predicted_price
  - CV is then normalised and scaled to a 1-10 integer score.
  - A perfectly confident model (CV → 0) scores 1 (Low Risk).
  - A highly uncertain model (CV ≥ threshold) scores 10 (High Risk).
"""

import math


# CV thresholds: CV of 0 → IRI 1, CV ≥ MAX_CV → IRI 10
_MIN_CV: float = 0.0
_MAX_CV: float = 0.60   # 60% coefficient of variation = maximum expected uncertainty


def calculate_iri(prediction_variance: float, predicted_price: float) -> int:
    """
    Convert a model's prediction variance into a 1-10 Investment Risk Index.

    Parameters
    ----------
    prediction_variance : float
        Variance of the model's prediction output (e.g. from an ensemble spread).
    predicted_price : float
        The model's central price estimate (LKR).

    Returns
    -------
    int
        IRI score in range [1, 10].
        1  = Very Low Risk (high model confidence)
        10 = Very High Risk (low model confidence / high volatility)
    """
    if predicted_price <= 0:
        return 10

    std_dev = math.sqrt(max(prediction_variance, 0.0))
    cv = std_dev / predicted_price

    # Clamp CV to [MIN, MAX]
    cv = max(_MIN_CV, min(cv, _MAX_CV))

    # Linear scale: 0 → 1, MAX_CV → 10
    raw_score = 1 + (cv / _MAX_CV) * 9
    iri = int(round(raw_score))
    return max(1, min(10, iri))


def iri_label(iri: int) -> tuple[str, str]:
    """
    Return a human-readable label and CSS class for an IRI score.

    Returns
    -------
    (label, css_class)
    """
    if iri <= 3:
        return "Low Risk", "hl-iri-low"
    elif iri <= 6:
        return "Medium Risk", "hl-iri-medium"
    else:
        return "High Risk", "hl-iri-high"


def iri_colour(iri: int) -> str:
    """Return a hex colour for the IRI score."""
    if iri <= 3:
        return "#00C48C"
    elif iri <= 6:
        return "#FFB347"
    else:
        return "#FF6B6B"
