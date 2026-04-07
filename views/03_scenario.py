"""
HousingLens – 🔮 Scenario Planner Page
-----------------------------------------
Compare a base property against a modified "what-if" scenario side by side.
"""

import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.header import load_css, render_topbar, render_page_title
from components.prediction_card import render_mini_pred_card
from model import model_stub
from model.predictor import predict as ml_predict
from model.iri_calculator import calculate_iri
from model.model_stub import format_lkr_short
from components.location_utils import get_cities_for_district
from components.pdf_generator import generate_scenario_pdf

# Page configuration and layout is now handled by app.py via st.navigation

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-page-hero" style="border-left-color:#FB923C;">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
        <span class="hl-tag hl-tag-coral" style="margin:0;">⚡ What-If Analysis</span>
        <span class="hl-tag hl-tag-violet" style="margin:0;">Real-time Comparison</span>
    </div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:800;
               color:#F1F5F9;margin:0 0 0.3rem 0;letter-spacing:-0.03em;">🔮 Scenario Planner</h1>
    <p style="color:#475569;font-size:0.9rem;margin:0;">
        Define a base property and explore What-If scenarios to see how changes impact price and risk.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hl-infobox">
    💡 <strong>How to use:</strong> Set your base property in the left column.
    Then adjust the <em>What-If</em> controls on the right to instantly compare
    how each change affects the valuation and Investment Risk Index.
</div>
""", unsafe_allow_html=True)

districts    = list(model_stub.DISTRICT_BASE_PRICE_PER_PERCH.keys())
prop_types   = list(model_stub.PROPERTY_TYPE_MULTIPLIER.keys())

# ── Two Scenario Columns ──────────────────────────────────────────────────────
base_col, mod_col = st.columns(2, gap="large")

# ──── BASE SCENARIO ─────────────────────
with base_col:
    st.markdown('<div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;'
                'letter-spacing:0.1em;color:#7B61FF;margin-bottom:0.6rem;">🟣 BASE SCENARIO</div>',
                unsafe_allow_html=True)
    with st.container(border=True):
        b_district  = st.selectbox("📍 District",      districts,   index=0,  key="b_dist")
        b_city      = st.selectbox("🏙️ City/Suburb", get_cities_for_district(b_district), index=0, key="b_city")
        b_proptype  = st.selectbox("🏘️ Property Type", prop_types,  index=0,  key="b_type")
        b_land      = st.number_input("🌿 Land Size (perches)", 1.0, 500.0, 10.0, 0.5, key="b_land")
        b_floor     = st.number_input("📐 Floor Area (sqft)",   200, 20000, 1200, 50,  key="b_floor")
        b_bed       = st.slider("🛏️ Bedrooms",  1, 10, 3, key="b_bed")
        b_bath      = st.slider("🚿 Bathrooms", 1, 8,  2, key="b_bath")
        st.markdown("**Nearby Amenities**")
        b_school    = st.toggle("🏫 School < 1 km",     True,  key="b_school")
        b_hospital  = st.toggle("🏥 Hospital < 2 km",   False, key="b_hosp")
        b_mainroad  = st.toggle("🛣️ Main Road < 0.5 km", True, key="b_road")
        b_amenities = st.slider("🏪 Amenities within 1 km", 0, 50, 10, key="b_amen")

# ──── MODIFIED SCENARIO ─────────────────
with mod_col:
    st.markdown('<div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;'
                'letter-spacing:0.1em;color:#00D4AA;margin-bottom:0.6rem;">🟢 WHAT-IF SCENARIO</div>',
                unsafe_allow_html=True)
    with st.container(border=True):
        m_district  = st.selectbox("📍 District",      districts,   index=0,  key="m_dist")
        m_city      = st.selectbox("🏙️ City/Suburb", get_cities_for_district(m_district), index=0, key="m_city")
        m_proptype  = st.selectbox("🏘️ Property Type", prop_types,  index=0,  key="m_type")
        m_land      = st.number_input("🌿 Land Size (perches)", 1.0, 500.0, 10.0, 0.5, key="m_land")
        m_floor     = st.number_input("📐 Floor Area (sqft)",   200, 20000, 1500, 50,  key="m_floor")
        m_bed       = st.slider("🛏️ Bedrooms",  1, 10, 4, key="m_bed")
        m_bath      = st.slider("🚿 Bathrooms", 1, 8,  3, key="m_bath")
        st.markdown("**Nearby Amenities**")
        m_school    = st.toggle("🏫 School < 1 km",     True,  key="m_school")
        m_hospital  = st.toggle("🏥 Hospital < 2 km",   True,  key="m_hosp")
        m_mainroad  = st.toggle("🛣️ Main Road < 0.5 km", True,  key="m_road")
        m_amenities = st.slider("🏪 Amenities within 1 km", 0, 50, 20, key="m_amen")

# ── Run both predictions ──────────────────────────────────────────────────────
base_inputs = {
    "district": b_district, "city": b_city, "property_type": b_proptype,
    "land_size": b_land,    "floor_area": b_floor,
    "bedrooms": b_bed,      "bathrooms": b_bath,
    "osm_school": b_school, "osm_hospital": b_hospital,
    "osm_mainroad": b_mainroad, "osm_amenities": b_amenities,
}
mod_inputs = {
    "district": m_district, "city": m_city, "property_type": m_proptype,
    "land_size": m_land,    "floor_area": m_floor,
    "bedrooms": m_bed,      "bathrooms": m_bath,
    "osm_school": m_school, "osm_hospital": m_hospital,
    "osm_mainroad": m_mainroad, "osm_amenities": m_amenities,
}

base_result = ml_predict(base_inputs)
mod_result  = ml_predict(mod_inputs)

base_price = base_result["price"]
mod_price  = mod_result["price"]
base_iri   = calculate_iri(base_result["prediction_variance"], base_price)
mod_iri    = calculate_iri(mod_result["prediction_variance"],  mod_price)

# ── Results Section ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<div class="hl-section-header"><span></span>Comparison Results</div>',
            unsafe_allow_html=True)

res_l, res_r = st.columns(2, gap="large")
with res_l:
    render_mini_pred_card("🟣 Base Scenario", base_price, base_iri, border_colour="#7B61FF")
with res_r:
    render_mini_pred_card("🟢 What-If Scenario", mod_price, mod_iri, border_colour="#00D4AA")

# ── Delta Summary ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
price_delta  = mod_price - base_price
iri_delta    = mod_iri   - base_iri
pct_change   = (price_delta / base_price) * 100 if base_price else 0

d1, d2, d3 = st.columns(3)
with d1:
    arrow  = "📈" if price_delta >= 0 else "📉"
    colour = "#34D399" if price_delta >= 0 else "#FC8181"
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
        box-shadow: 0 0 20px {"rgba(52,211,153,0.12)" if price_delta >= 0 else "rgba(252,129,129,0.12)"};
    ">
        <div style="font-size:0.72rem;font-weight:700;color:#475569;text-transform:uppercase;
                    letter-spacing:0.1em;margin-bottom:0.5rem;">Price Change</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.8rem;
                    font-weight:800;color:{colour};letter-spacing:-0.03em;">
            {arrow} {format_lkr_short(abs(price_delta))}
        </div>
        <div style="font-size:0.88rem;color:{colour};margin-top:4px;font-weight:600;">
            {'+' if price_delta>=0 else ''}{pct_change:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with d2:
    iri_colour_d = "#34D399" if iri_delta <= 0 else "#FC8181"
    iri_arrow    = "📉" if iri_delta <= 0 else "📈"
    iri_note     = "Risk Decreased" if iri_delta < 0 else ("No Change" if iri_delta == 0 else "Risk Increased")
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
        box-shadow: 0 0 20px {"rgba(52,211,153,0.12)" if iri_delta <= 0 else "rgba(252,129,129,0.12)"};
    ">
        <div style="font-size:0.72rem;font-weight:700;color:#475569;text-transform:uppercase;
                    letter-spacing:0.1em;margin-bottom:0.5rem;">IRI Change</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.8rem;
                    font-weight:800;color:{iri_colour_d};letter-spacing:-0.03em;">
            {iri_arrow} {'+' if iri_delta>0 else ''}{iri_delta} pts
        </div>
        <div style="font-size:0.88rem;color:{iri_colour_d};margin-top:4px;font-weight:600;">{iri_note}</div>
    </div>
    """, unsafe_allow_html=True)

with d3:
    verdict_icon  = "✅" if price_delta >= 0 and iri_delta <= 0 else ("⚠️" if price_delta >= 0 else "🔴")
    verdict_text  = ("More valuable & safer!" if price_delta >= 0 and iri_delta <= 0 else
                     ("More valuable but riskier" if price_delta >= 0 else "Lower value scenario"))
    verdict_color = "#34D399" if verdict_icon == "✅" else ("#FCD34D" if verdict_icon == "⚠️" else "#FC8181")
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
    ">
        <div style="font-size:0.72rem;font-weight:700;color:#475569;text-transform:uppercase;
                    letter-spacing:0.1em;margin-bottom:0.5rem;">Verdict</div>
        <div style="font-size:2rem;margin:0.3rem 0;">{verdict_icon}</div>
        <div style="font-size:0.9rem;font-weight:700;color:{verdict_color};">{verdict_text}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Feature Comparison Bar Chart ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>Feature Contribution Comparison</div>',
            unsafe_allow_html=True)

base_imp = base_result["feature_importances"]
mod_imp  = mod_result["feature_importances"]
keys     = list(base_imp.keys())

fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(
    name="Base Scenario", x=keys, y=[base_imp[k] for k in keys],
    marker_color="rgba(123,97,255,0.7)", marker_line=dict(color="#7B61FF", width=1),
))
fig_comp.add_trace(go.Bar(
    name="What-If Scenario", x=keys, y=[mod_imp[k] for k in keys],
    marker_color="rgba(0,212,170,0.7)", marker_line=dict(color="#00D4AA", width=1),
))
fig_comp.update_layout(
    barmode="group",
    xaxis=dict(color="#E8EDF5", gridcolor="rgba(255,255,255,0.03)", tickangle=-10),
    yaxis=dict(color="#8A94A8", title="Contribution (%)", gridcolor="rgba(255,255,255,0.04)"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(font=dict(color="#E8EDF5"), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=20, b=40, l=20, r=20),
    height=320, font=dict(family="Inter", color="#E8EDF5"),
)
st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

# ── PDF Export Button ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
pdf_bytes = generate_scenario_pdf(
    base_data=base_inputs,
    base_price=base_price,
    base_iri=base_iri,
    mod_data=mod_inputs,
    mod_price=mod_price,
    mod_iri=mod_iri,
    price_delta=price_delta,
    pct_change=pct_change
)

st.download_button(
    label="📄 Download Scenario PDF Report",
    data=pdf_bytes,
    file_name=f"HousingLens_Scenario_Report_{base_inputs.get('district', 'Loc')}.pdf",
    mime="application/pdf",
    type="primary"
)
