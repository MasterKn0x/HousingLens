"""
HousingLens – 🏠 Predict Page
-------------------------------
Two-column layout: property input form (left) + prediction output (right).
"""

import streamlit as st
from components.header import load_css, render_topbar, render_page_title
from components.iri_gauge import render_iri_gauge
from components.prediction_card import render_prediction_card
from components.feature_chart import render_feature_chart
from components.district_map import render_district_map
from components.location_utils import get_cities_for_district
from model import model_stub
from model.predictor import predict as ml_predict, get_model_info
from model.iri_calculator import calculate_iri
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration and layout is now handled by app.py via st.navigation

# ── Sidebar Info ──────────────────────────────────────────────────────────────
with st.sidebar:
    _minfo = get_model_info()
    if _minfo["trained"]:
        st.markdown(f"""
        <div style="font-size:0.75rem; color:#8A94A8; text-align:center; line-height:1.8;">
            <b style="color:#38BDF8">✅ ML Model Active</b><br>
            Trained on <b style="color:#F97316">{_minfo['n_train']:,}</b> listings<br>
            R² = <b style="color:#38BDF8">{_minfo['cv_r2']:.3f}</b> &nbsp;|&nbsp;
            MAE ≈ Rs {_minfo['cv_mae']/1e6:.1f}M
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:0.75rem; color:#8A94A8; text-align:center; line-height:1.6;">
            <b style="color:#F97316">⚠ Stub Mode Active</b><br>
            Run <code>python model/train.py</code><br>to enable ML predictions.
        </div>
        """, unsafe_allow_html=True)

# ── Page hero ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-page-hero">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
        <div>
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
                <span class="hl-tag" style="margin:0;">
                    <span class="hl-live-dot"></span>Live AI
                </span>
                <span class="hl-tag hl-tag-violet" style="margin:0;">Updates Instantly</span>
            </div>
            <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
                       color:#F1F5F9;margin:0 0 0.3rem 0;letter-spacing:-0.03em;">🔍 Property Price Predictor</h1>
            <p style="color:#475569;font-size:0.9rem;margin:0;">
                Enter property details to receive an AI-powered valuation + Investment Risk Index.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input form + Output columns ───────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

# ────────────────────────────────────────────────
# LEFT COLUMN – Input Form
# ────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="hl-section-header"><span></span>Property Details</div>',
                unsafe_allow_html=True)

    districts = list(model_stub.DISTRICT_BASE_PRICE_PER_PERCH.keys())
    property_types = list(model_stub.PROPERTY_TYPE_MULTIPLIER.keys())

    c1, c2 = st.columns(2)
    with c1:
        district = st.selectbox("📍 District", districts, index=0)
        
        valid_cities = get_cities_for_district(district)
        city = st.selectbox("🏙️ City/Suburb", valid_cities, index=0)

    with c2:
        prop_type = st.selectbox("🏘️ Property Type", property_types, index=0)

    c3, c4 = st.columns(2)
    with c3:
        land_size = st.number_input("🌿 Land Size (perches)", min_value=1.0, max_value=500.0,
                                     value=10.0, step=0.5,
                                     help="1 perch ≈ 25.29 m²")
    with c4:
        floor_area = st.number_input("📐 Floor Area (sqft)", min_value=200, max_value=20_000,
                                      value=1_200, step=50,
                                      help="Total built area in square feet")

    c5, c6 = st.columns(2)
    with c5:
        bedrooms = st.slider("🛏️ Bedrooms", 1, 10, 3)
    with c6:
        bathrooms = st.slider("🚿 Bathrooms", 1, 8, 2)

    st.markdown('<div class="hl-section-header" style="margin-top:1rem;"><span></span>Nearby Amenities (OSM)</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hl-infobox">🗺️ Toggle amenities near this property. '
                'These geospatial features (from OpenStreetMap) significantly improve prediction accuracy.</div>',
                unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)
    with ca:
        osm_school   = st.toggle("🏫 School < 1 km",    value=True)
    with cb:
        osm_hospital = st.toggle("🏥 Hospital < 2 km",  value=False)
    with cc:
        osm_mainroad = st.toggle("🛣️ Main Road < 0.5 km", value=True)

    osm_amenities = st.slider("🏪 Nearby Amenities (cafes, shops, etc.) within 1 km",
                               0, 50, 10)

    st.markdown('<div class="hl-section-header" style="margin-top:1rem;"><span></span>Location Map</div>',
                unsafe_allow_html=True)
    render_district_map(district)

# ────────────────────────────────────────────────
# RIGHT COLUMN – Prediction Output
# ────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="hl-section-header"><span></span>Prediction Output</div>', unsafe_allow_html=True)

    inputs = {
        "district":      district,
        "city":          city,
        "property_type": prop_type,
        "land_size":     land_size,
        "floor_area":    floor_area,
        "bedrooms":      bedrooms,
        "bathrooms":     bathrooms,
        "osm_school":    osm_school,
        "osm_hospital":  osm_hospital,
        "osm_mainroad":  osm_mainroad,
        "osm_amenities": osm_amenities,
    }

    # Don't spin for instantaneous local model predictions
    result = ml_predict(inputs)

    price      = result["price"]
    variance   = result["prediction_variance"]
    price_low  = result["price_range_low"]
    price_high = result["price_range_high"]
    importances = result["feature_importances"]
    iri        = calculate_iri(variance, price)

    # Main prediction card
    render_prediction_card(price, price_low, price_high, iri)

    st.markdown("<br>", unsafe_allow_html=True)

    # IRI gauge
    st.markdown('<div class="hl-section-header"><span></span>Investment Risk Index</div>',
                unsafe_allow_html=True)
    render_iri_gauge(iri)

    # IRI interpretation box
    if iri <= 3:
        st.success("✅ **Low Risk** – High model confidence. The market in this district is stable and data is dense.")
    elif iri <= 6:
        st.warning("⚠️ **Medium Risk** – Moderate confidence. Some market volatility or data sparsity detected.")
    else:
        st.error("🔴 **High Risk** – Low confidence. This area may have limited data or high price volatility.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature importance chart
    st.markdown('<div class="hl-section-header"><span></span>Key Price Drivers</div>',
                unsafe_allow_html=True)
    render_feature_chart(importances, title="Feature Importances for this Prediction")

# ── Footer tip ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-infobox" style="margin-top:1.5rem;">
    💡 <strong>Tip:</strong> Use the <strong style="color:#38BDF8;">🔮 Scenario Planner</strong>
    to compare how a single change (e.g. adding a bedroom, switching district) affects price and risk.
</div>
""", unsafe_allow_html=True)
