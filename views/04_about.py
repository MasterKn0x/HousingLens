"""
HousingLens – ℹ️ About Page
-----------------------------
Project overview, methodology, technology stack, and academic references.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.header import load_css, render_topbar, render_page_title

# Page configuration and layout is now handled by app.py via st.navigation

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-page-hero" style="border-left-color:#34D399;">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
        <span class="hl-tag hl-tag-success" style="margin:0;">🇱🇰 Sri Lanka</span>
        <span class="hl-tag" style="margin:0;">Open Research</span>
    </div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:800;
               color:#F1F5F9;margin:0 0 0.3rem 0;letter-spacing:-0.03em;">ℹ️ About HousingLens</h1>
    <p style="color:#475569;font-size:0.9rem;margin:0;">
        What it is, how it works, and why it matters for the Sri Lankan property market.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Mission Statement ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-hero" style="padding:2rem 2.5rem;">
    <h2 style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:700;
               color:#E8EDF5; margin:0 0 0.8rem 0;">
        The Problem with Property Valuation Today
    </h2>
    <p style="color:#C8D0E0; font-size:0.97rem; line-height:1.8; margin:0 0 1rem 0;">
        Existing online real estate platforms — including Sri Lankan portals like ikman.lk — display a
        <strong style="color:#E8EDF5;">single, fixed price estimate</strong> with no indication of how
        reliable that number actually is. A property listed for LKR 45M could realistically be worth anywhere
        from LKR 32M to LKR 60M depending on market conditions — yet the buyer sees only one number.
    </p>
    <p style="color:#C8D0E0; font-size:0.97rem; line-height:1.8; margin:0;">
        <strong style="color:#00D4AA;">HousingLens</strong> was built to fix this. It combines a machine learning
        valuation engine with a unique transparency metric — the
        <strong style="color:#00D4AA;">Investment Risk Index (IRI)</strong> — to show not just <em>what</em> a
        property is worth, but <em>how confident</em> that estimate is.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── The Two Core Outputs ───────────────────────────────────────────────────────
st.markdown('<div class="hl-section-header"><span></span>Two Outputs. One Decision.</div>',
            unsafe_allow_html=True)

o1, o2 = st.columns(2, gap="large")
with o1:
    st.markdown("""
    <div style="background:#131827; border:1px solid rgba(0,212,170,0.25);
                border-top: 3px solid #00D4AA; border-radius:14px; padding:1.8rem; height:100%;">
        <div style="font-size:2rem; margin-bottom:0.8rem;">💰</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem;
                    font-weight:700; color:#E8EDF5; margin-bottom:0.5rem;">
            AI-Powered Price Prediction
        </div>
        <div style="color:#8A94A8; font-size:0.9rem; line-height:1.7;">
            A machine learning model — trained on Sri Lankan residential property listings from
            <strong style="color:#E8EDF5;">ikman.lk</strong> — estimates the fair market value of any
            property in LKR. It goes beyond a simple average by modelling the complex, non-linear
            relationships between location, size, room count, and proximity to amenities.
        </div>
    </div>
    """, unsafe_allow_html=True)

with o2:
    st.markdown("""
    <div style="background:#131827; border:1px solid rgba(123,97,255,0.25);
                border-top: 3px solid #7B61FF; border-radius:14px; padding:1.8rem; height:100%;">
        <div style="font-size:2rem; margin-bottom:0.8rem;">📉</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem;
                    font-weight:700; color:#E8EDF5; margin-bottom:0.5rem;">
            Investment Risk Index (IRI)
        </div>
        <div style="color:#8A94A8; font-size:0.9rem; line-height:1.7;">
            The IRI is HousingLens's original contribution. It translates the model's
            <strong style="color:#E8EDF5;">prediction variance</strong> — a measure of how spread-out
            the possible valuations are — into a simple <strong style="color:#E8EDF5;">1–10 score</strong>.
            A score of 1 means high confidence and a stable market. A score of 10 means the market is
            volatile or data is sparse: proceed with caution.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Methodology ───────────────────────────────────────────────────────────────
st.markdown('<div class="hl-section-header"><span></span>How It Works Under the Hood</div>',
            unsafe_allow_html=True)

steps = [
    ("🔢", "1. Hedonic Pricing Theory",
     "Every property price is the sum of its parts — the land, the structure, the location. "
     "HousingLens encodes this economic framework (Rosen, 1974) as machine learning features "
     "rather than relying on a simple linear regression."),
    ("🗺️", "2. Geospatial Feature Engineering",
     "A property's street name tells us almost nothing. So HousingLens uses the "
     "<strong style='color:#E8EDF5;'>OpenStreetMap Overpass API</strong> to compute real, quantitative "
     "distances — to the nearest school, hospital, and main road — plus the count of amenities "
     "within 1 km, for every listing."),
    ("🤖", "3. ML Algorithm Bake-Off",
     "Multiple algorithms are trained and compared head-to-head: Linear Regression (baseline), "
     "Random Forest, <strong style='color:#E8EDF5;'>XGBoost</strong> (primary candidate), and a "
     "Keras Neural Network. The winner is chosen by R² on a held-out test set — target: R² > 0.85."),
    ("📐", "4. IRI Calculation",
     "The winning model's <strong style='color:#E8EDF5;'>prediction variance</strong> across an ensemble "
     "is converted to a Coefficient of Variation (CV = σ / price). The CV is linearly scaled to a "
     "1–10 integer — the Investment Risk Index."),
    ("🖥️", "5. Streamlit Dashboard",
     "The trained model is serialised as a <code style='color:#00D4AA;'>model.pkl</code> file and loaded "
     "into a lightweight Streamlit web app. Users enter property details, the app calls "
     "<code style='color:#00D4AA;'>model.predict()</code>, computes the IRI, and displays both outputs "
     "in under 2 seconds."),
]

for icon, title, desc in steps:
    st.markdown(f"""
    <div style="display:flex; gap:1.2rem; align-items:flex-start; margin-bottom:0.9rem;
                background:#131827; border:1px solid rgba(0,212,170,0.1);
                border-radius:12px; padding:1.1rem 1.3rem;">
        <div style="font-size:1.5rem; flex-shrink:0; padding-top:1px;">{icon}</div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:600;
                        color:#E8EDF5; margin-bottom:4px;">{title}</div>
            <div style="font-size:0.87rem; color:#8A94A8; line-height:1.7;">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Research Gap ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>What Gap Does It Fill?</div>',
            unsafe_allow_html=True)

g1, g2 = st.columns(2, gap="large")
with g1:
    st.markdown("""
    <div style="background:rgba(255,107,107,0.05); border:1px solid rgba(255,107,107,0.2);
                border-radius:12px; padding:1.3rem;">
        <div style="font-weight:700; color:#FF6B6B; margin-bottom:0.6rem;">❌ Current State</div>
        <ul style="color:#8A94A8; font-size:0.88rem; line-height:1.9; margin:0; padding-left:1.2rem;">
            <li>Zillow &amp; Redfin target US/Canada — not Sri Lanka</li>
            <li>ikman.lk shows user-set listing prices, no AI valuation</li>
            <li>No platform in Sri Lanka provides a risk or confidence metric</li>
            <li>Academic papers compare model accuracy but don't translate uncertainty into a user-friendly score</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with g2:
    st.markdown("""
    <div style="background:rgba(0,196,140,0.05); border:1px solid rgba(0,196,140,0.2);
                border-radius:12px; padding:1.3rem;">
        <div style="font-weight:700; color:#00C48C; margin-bottom:0.6rem;">✅ HousingLens Provides</div>
        <ul style="color:#8A94A8; font-size:0.88rem; line-height:1.9; margin:0; padding-left:1.2rem;">
            <li>AI valuation trained specifically on <strong style='color:#E8EDF5;'>Sri Lankan data</strong></li>
            <li>Custom geospatial features via OpenStreetMap (not just city names)</li>
            <li>The <strong style='color:#00D4AA;'>Investment Risk Index</strong> — a first-of-its-kind transparency metric for this market</li>
            <li>Full explainability: feature importance charts show <em>why</em> a price was assigned</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ── Technology Stack ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>Technology Stack</div>', unsafe_allow_html=True)

tech = [
    ("🐍", "Python 3.11"),  ("🌊", "Streamlit"),    ("📊", "Plotly"),
    ("🤖", "Scikit-learn"), ("⚡", "XGBoost"),       ("🧠", "TensorFlow / Keras"),
    ("🐼", "Pandas"),       ("🔢", "NumPy"),         ("🕷️", "BeautifulSoup4"),
    ("🗺️", "OpenStreetMap"),("📍", "Geopy"),         ("🧪", "pytest"),
]
st.markdown('<div class="hl-tech-grid">' + "".join(
    f'<div class="hl-tech-card"><span class="hl-tech-icon">{icon}</span>{name}</div>'
    for icon, name in tech
) + '</div>', unsafe_allow_html=True)

# ── Requirements ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>System Requirements</div>',
            unsafe_allow_html=True)

col_fr, col_nfr = st.columns(2, gap="large")
with col_fr:
    st.markdown("**What the system does (Functional)**")
    reqs = [
        ("FR1", "Property feature input UI — location, size, rooms"),
        ("FR2", "AI-powered forecasted property price"),
        ("FR3", "Investment Risk Index score (1–10)"),
        ("FR4", "Feature importance chart — top 5 price drivers"),
        ("FR5", "Scenario Planning Tool — real-time what-if analysis"),
    ]
    for code, desc in reqs:
        st.markdown(f"""
        <div style="display:flex;gap:0.8rem;align-items:flex-start;
                    background:rgba(0,212,170,0.05);border-radius:8px;
                    padding:0.65rem 0.9rem;margin-bottom:0.35rem;">
            <span style="font-weight:700;color:#00D4AA;min-width:36px;">{code}</span>
            <span style="font-size:0.85rem;color:#C8D0E0;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

with col_nfr:
    st.markdown("**How well the system does it (Non-Functional)**")
    nfrs = [
        ("NFR1", "Response time < 2 seconds per prediction"),
        ("NFR2", "Clean, responsive UI on desktop and mobile"),
        ("NFR3", "Model R² > 0.85 on the held-out test set"),
        ("NFR4", "No personal user data stored or transmitted"),
        ("NFR5", "PEP 8 compliant, fully commented Python code"),
    ]
    for code, desc in nfrs:
        st.markdown(f"""
        <div style="display:flex;gap:0.8rem;align-items:flex-start;
                    background:rgba(123,97,255,0.05);border-radius:8px;
                    padding:0.65rem 0.9rem;margin-bottom:0.35rem;">
            <span style="font-weight:700;color:#7B61FF;min-width:40px;">{code}</span>
            <span style="font-size:0.85rem;color:#C8D0E0;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

# ── References ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>Academic References</div>',
            unsafe_allow_html=True)

references = [
    ("Géron, A. (2022)", "Hands-on Machine Learning with Scikit-Learn, Keras & TensorFlow. 3rd edn. O'Reilly Media."),
    ("Gunarathna et al. (2022)", "A machine learning approach to predict housing prices in Sri Lanka. ICAC 2022. IEEE. doi: 10.1109/ICAC57688.2022.10023447."),
    ("Niu, H., et al. (2023)", "A comprehensive comparison of machine learning models for house price prediction. Heliyon, 9(6). doi: 10.1016/j.heliyon.2023.e17149."),
    ("Rosen, S. (1974)", "Hedonic Prices and Implicit Markets: Product Differentiation in Pure Competition. Journal of Political Economy, 82(1), pp. 34–55."),
    ("VanderPlas, J. (2016)", "Python Data Science Handbook. O'Reilly Media."),
    ("Yilmaz & Kina (2023)", "An explainable house price prediction model using geospatial data. Expert Systems with Applications, 226, 120155."),
    ("OpenStreetMap (2025)", "Overpass API. wiki.openstreetmap.org/wiki/Overpass_API"),
    ("ikman.lk (2025)", "Property & Real Estate for Sale and Rent in Sri Lanka. ikman.lk/en/ads/sri-lanka/property"),
]

with st.expander("📚 View All References", expanded=False):
    for author, text in references:
        st.markdown(f"""
        <div style="display:flex;gap:0.8rem;margin-bottom:0.6rem;font-size:0.86rem;color:#C8D0E0;line-height:1.6;">
            <span style="color:#00D4AA;font-weight:600;min-width:180px;flex-shrink:0;">{author}</span>
            <span>{text}</span>
        </div>
        """, unsafe_allow_html=True)
