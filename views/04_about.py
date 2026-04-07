"""
HousingLens – ℹ️ About Page
-----------------------------
Product overview, methodology, technology stack, and contact information.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.header import load_css, render_topbar, render_page_title

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-page-hero" style="border-left-color:#34D399;">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
        <span class="hl-tag hl-tag-success" style="margin:0;">🇱🇰 Sri Lanka</span>
        <span class="hl-tag" style="margin:0;">PropTech</span>
    </div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:800;
               color:#F1F5F9;margin:0 0 0.3rem 0;letter-spacing:-0.03em;">ℹ️ About HousingLens</h1>
    <p style="color:#475569;font-size:0.9rem;margin:0;">
        Modernizing property valuation in Sri Lanka through data science and transparency.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Mission Statement ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-hero" style="padding:2rem 2.5rem;">
    <h2 style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:700;
               color:#E8EDF5; margin:0 0 0.8rem 0;">
        Defining Fair Market Value
    </h2>
    <p style="color:#C8D0E0; font-size:0.97rem; line-height:1.8; margin:0 0 1rem 0;">
        Conventional real estate listings often suffer from price ambiguity. A single asking price rarely reflects the true 
        market depth or the surrounding volatility. For buyers and investors, this "black box" approach leads to 
        misinformed decisions and over-leveraged risks.
    </p>
    <p style="color:#C8D0E0; font-size:0.97rem; line-height:1.8; margin:0;">
        <strong style="color:#00D4AA;">HousingLens</strong> was engineered to bridge this information gap. By combining 
        sophisticated machine learning with our proprietary <strong style="color:#00D4AA;">Investment Risk Index (IRI)</strong>, 
        we provide a dual-perspective valuation: what a property is worth, and exactly how much confidence you can place in that figure.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── The Two Core Outputs ───────────────────────────────────────────────────────
st.markdown('<div class="hl-section-header"><span></span>The HousingLens Framework</div>',
            unsafe_allow_html=True)

o1, o2 = st.columns(2, gap="large")
with o1:
    st.markdown("""
    <div style="background:#131827; border:1px solid rgba(0,212,170,0.25);
                border-top: 3px solid #00D4AA; border-radius:14px; padding:1.8rem; height:100%;">
        <div style="font-size:2rem; margin-bottom:0.8rem;">💰</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem;
                    font-weight:700; color:#E8EDF5; margin-bottom:0.5rem;">
            AI-Powered Valuation
        </div>
        <div style="color:#8A94A8; font-size:0.9rem; line-height:1.7;">
            Our core engine uses gradient-boosted trees trained on thousands of active Sri Lankan listings. 
            It models complex, non-linear relationships between structural features, hyper-local geography, 
            and proximity to urban hubs to deliver precise LKR estimates.
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
            We don't just give you a number; we give you context. The IRI translates model prediction variance—a statistical 
            measure of market stability and data density—into an actionable <strong style="color:#E8EDF5;">1–10 score</strong>. 
            Identify volatile neighborhoods and high-confidence opportunities at a glance.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Methodology ───────────────────────────────────────────────────────────────
st.markdown('<div class="hl-section-header"><span></span>Precision Engineering Workflow</div>',
            unsafe_allow_html=True)

steps = [
    ("🔢", "1. Hedonic Feature Modeling",
     "We break down property value into constituent parts—land, structure, and location—using an "
     "optimized hedonic framework that accounts for both tangible and intangible asset drivers."),
    ("🗺️", "2. Geospatial Intelligence",
     "Standard location names aren't enough. We utilize the <strong style='color:#E8EDF5;'>OpenStreetMap Overpass API</strong> "
     "to calculate real-world walking and driving distances to essential amenities, schools, and hospitals."),
    ("🤖", "3. Predictive Analytics",
     "Our production model utilizes high-performance <strong style='color:#E8EDF5;'>XGBoost</strong> architecture, "
     "validated against cross-market test sets to ensure robust generalization across diverse Sri Lankan districts."),
    ("📐", "4. Uncertainty Quantification",
     "The engine calculates prediction intervals by analyzing local market volatility and historical data sparsity, "
     "normalizing these results into the customer-facing Investment Risk Index."),
    ("🖥️", "5. Real-Time Deployment",
     "Valuations are processed instantly through a lightweight, high-performance Python backend, delivering "
     "scenario-based insights and interactive reports in under 2 seconds."),
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

# ── Market Gap ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>The HousingLens Advantage</div>',
            unsafe_allow_html=True)

g1, g2 = st.columns(2, gap="large")
with g1:
    st.markdown("""
    <div style="background:rgba(255,107,107,0.05); border:1px solid rgba(255,107,107,0.2);
                border-radius:12px; padding:1.3rem;">
        <div style="font-weight:700; color:#FF6B6B; margin-bottom:0.6rem;">❌ Conventional Tools</div>
        <ul style="color:#8A94A8; font-size:0.88rem; line-height:1.9; margin:0; padding-left:1.2rem;">
            <li>Reliance on subjective listing prices</li>
            <li>Lack of hyper-local amenity data</li>
            <li>No quantification of market risk</li>
            <li>Static analysis without interactive scenarios</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with g2:
    st.markdown("""
    <div style="background:rgba(0,196,140,0.05); border:1px solid rgba(0,196,140,0.2);
                border-radius:12px; padding:1.3rem;">
        <div style="font-weight:700; color:#00C48C; margin-bottom:0.6rem;">✅ HousingLens Platform</div>
        <ul style="color:#8A94A8; font-size:0.88rem; line-height:1.9; margin:0; padding-left:1.2rem;">
            <li>Production-grade AI trained on 🇱🇰 data</li>
            <li>Dynamic Geospatial Engineering (OSM)</li>
            <li>Integrated Risk Index transparency</li>
            <li>Scenario-based investment planning</li>
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

# ── Performance Benchmarks ────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>Service Level Objectives</div>',
            unsafe_allow_html=True)

col_fr, col_nfr = st.columns(2, gap="large")
with col_fr:
    st.markdown("**Core Capabilities**")
    reqs = [
        ("01", "Dynamic property feature ingestion"),
        ("02", "Near real-time valuation engine"),
        ("03", "Investment Risk Score generation"),
        ("04", "Explainable feature importance analytics"),
        ("05", "Interactive Scenario Planning hub"),
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
    st.markdown("**Performance & Quality**")
    nfrs = [
        ("01", "Latency < 2s for end-to-end inference"),
        ("02", "Fully responsive multi-device interface"),
        ("03", "Cross-validated R² > 0.85 accuracy target"),
        ("04", "Privacy-first: No user data retention"),
        ("05", "Modular, scalable micro-architecture"),
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

# ── Contact ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>Contact & Support</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="hl-hero" style="padding:1.5rem 2rem; background:rgba(0,212,170,0.05); border:1px solid rgba(0,212,170,0.15);">
    <div style="display:flex; align-items:center; gap:1.2rem;">
        <div style="font-size:2.5rem;">📬</div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:700; color:#E8EDF5; margin-bottom:4px;">
                Get in Touch
            </div>
            <div style="color:#8A94A8; font-size:0.9rem; margin-bottom:0.8rem;">
                For support, partnerships, or data inquiries, please reach out via email.
            </div>
            <a href="mailto:support@housinglens.com" style="color:#00D4AA; font-weight:700; text-decoration:none; 
                        padding:0.5rem 1rem; border:1px solid #00D4AA; border-radius:6px; display:inline-block;">
                support@housinglens.com
            </a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Technical References ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="hl-section-header"><span></span>Technical References</div>',
            unsafe_allow_html=True)

references = [
    ("Géron, A. (2022)", "Hands-on Machine Learning with Scikit-Learn, Keras & TensorFlow. 3rd edn. O'Reilly Media."),
    ("Gunarathna et al. (2022)", "A machine learning approach to predict housing prices in Sri Lanka. ICAC 2022. IEEE. doi: 10.1109/ICAC57688.2022.10023447."),
    ("Niu, H., et al. (2023)", "A comprehensive comparison of machine learning models for house price prediction. Heliyon, 9(6). doi: 10.1016/j.heliyon.2023.e17149."),
    ("Rosen, S. (1974)", "Hedonic Prices and Implicit Markets: Product Differentiation in Pure Competition. Journal of Political Economy, 82(1), pp. 34–55."),
    ("VanderPlas, J. (2016)", "Python Data Science Handbook. O'Reilly Media."),
    ("Yilmaz & Kina (2023)", "An explainable house price prediction model using geospatial data. Expert Systems with Applications, 226, 120155."),
]

with st.expander("📚 View Technical & Methodology Sources", expanded=False):
    for author, text in references:
        st.markdown(f"""
        <div style="display:flex;gap:0.8rem;margin-bottom:0.6rem;font-size:0.86rem;color:#C8D0E0;line-height:1.6;">
            <span style="color:#00D4AA;font-weight:600;min-width:180px;flex-shrink:0;">{author}</span>
            <span>{text}</span>
        </div>
        """, unsafe_allow_html=True)
