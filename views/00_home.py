"""
HousingLens – 🏡 Home Page (Premium Redesign)
-----------------------------------------------
Animated hero, glassmorphism stat cards, feature showcase, radar chart.
"""

import streamlit as st
import plotly.graph_objects as go
from model.data_loader import load_listings, dataset_stats
from model.predictor import get_model_info


def render():
    df    = load_listings()
    stats = dataset_stats(df)
    minfo = get_model_info()
    n_train = minfo.get('n_train', stats.get('total', 0))
    r2 = minfo.get('cv_r2', 0)

    # ── Hero Section ──────────────────────────────────────────────────────────
    hero_html = (
        '<div class="hl-hero">'
        '<div class="hl-hero-orb"></div>'
        '<div style="margin-bottom:1.5rem;display:flex;flex-wrap:wrap;gap:0;">'
        '<span class="hl-tag"><span class="hl-live-dot"></span>AI-Powered</span>'
        '<span class="hl-tag hl-tag-violet">Sri Lanka Market</span>'
        '<span class="hl-tag hl-tag-coral">19K+ Real Listings</span>'
        '<span class="hl-tag hl-tag-success">Open Research</span>'
        '</div>'
        '<h1 class="hl-hero-title">Know Your Property\'s<br><em>True Value.</em></h1>'
        '<p class="hl-hero-sub">HousingLens delivers AI-powered residential property price predictions '
        'and a unique <strong style="color:#38BDF8;font-weight:700;">Investment Risk Index (IRI)</strong> '
        '— giving buyers and investors the clarity they deserve in the Sri Lankan real estate market.</p>'
        '<div class="hl-stat-grid">'
        f'<div class="hl-stat-card"><span class="hl-stat-value">{stats.get("districts", 24)}</span>'
        '<span class="hl-stat-label">Districts Covered</span></div>'
        f'<div class="hl-stat-card"><span class="hl-stat-value">{n_train:,}</span>'
        '<span class="hl-stat-label">Training Listings</span></div>'
        f'<div class="hl-stat-card"><span class="hl-stat-value">R² {r2:.2f}</span>'
        '<span class="hl-stat-label">Model Accuracy</span></div>'
        '<div class="hl-stat-card"><span class="hl-stat-value">1–10</span>'
        '<span class="hl-stat-label">IRI Risk Scale</span></div>'
        '</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── How It Works ─────────────────────────────────────────────────────────
    st.markdown('<div class="hl-section-header"><span></span>How It Works</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    steps = [
        ("01", "🏡", "Input Property Details",
         "Enter district, property type, land size, floor area, bedrooms, bathrooms, and nearby OSM amenities.",
         "#38BDF8"),
        ("02", "🤖", "AI Engine Predicts",
         "The trained XGBoost model analyses your inputs against thousands of Sri Lankan property transactions.",
         "#A78BFA"),
        ("03", "📊", "Review Price + IRI",
         "Get the estimated market value in LKR, a confidence range, and a 1–10 Investment Risk Index.",
         "#FB923C"),
    ]
    for col, (num, icon, title, desc, colour) in zip([c1, c2, c3], steps):
        with col:
            card = (
                f'<div class="hl-glass-card" style="text-align:center;border-top:3px solid {colour};'
                f'padding:2rem 1.5rem;min-height:220px;">'
                f'<div style="font-family:\'Space Grotesk\',sans-serif;font-size:0.68rem;font-weight:800;'
                f'color:{colour};text-transform:uppercase;letter-spacing:0.18em;margin-bottom:0.8rem;opacity:0.7;">'
                f'{num}</div>'
                f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);'
                f'border-radius:16px;width:60px;height:60px;display:inline-flex;align-items:center;'
                f'justify-content:center;font-size:1.7rem;margin-bottom:1rem;">{icon}</div>'
                f'<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1rem;font-weight:700;'
                f'color:#F1F5F9;margin-bottom:0.6rem;">{title}</div>'
                f'<div style="font-size:0.85rem;color:#64748B;line-height:1.65;">{desc}</div>'
                f'</div>'
            )
            st.markdown(card, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── What Makes HousingLens Different ─────────────────────────────────────
    st.markdown('<div class="hl-section-header"><span></span>What Makes HousingLens Different</div>',
                unsafe_allow_html=True)

    col_feat, col_radar = st.columns([3, 2], gap="large")

    with col_feat:
        features = [
            ("🎯", "Investment Risk Index (IRI)",
             "No other Sri Lankan platform quantifies prediction confidence as a transparent 1–10 score.",
             "#38BDF8"),
            ("📍", "Geospatial Feature Engineering",
             "Real distances to schools, hospitals & main roads via OpenStreetMap — not just a city name.",
             "#A78BFA"),
            ("🔮", "Scenario Planning Tool",
             "See exactly how changing bedrooms, land size, or district shifts valuation in real time.",
             "#FB923C"),
            ("📊", "Model Transparency",
             "Feature importance charts reveal why the model arrived at a price — never a black box.",
             "#34D399"),
            ("🇱🇰", "Built for Sri Lanka",
             "Trained on 19,000+ live-scraped ikman.lk listings, capturing real market dynamics.",
             "#7DD3FC"),
        ]
        for icon, title, desc, colour in features:
            feat = (
                f'<div class="hl-feature-card">'
                f'<div style="background:{colour}18;border:1px solid {colour}33;border-radius:12px;'
                f'width:44px;height:44px;display:flex;align-items:center;justify-content:center;'
                f'font-size:1.3rem;flex-shrink:0;">{icon}</div>'
                f'<div>'
                f'<div style="font-weight:700;color:#F1F5F9;margin-bottom:3px;font-size:0.95rem;">{title}</div>'
                f'<div style="font-size:0.84rem;color:#64748B;line-height:1.55;">{desc}</div>'
                f'</div></div>'
            )
            st.markdown(feat, unsafe_allow_html=True)

    with col_radar:
        categories = ["Price Prediction", "Risk Metric", "Geospatial", "Local Market", "Transparency"]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[8, 2, 7, 2, 3], theta=categories, fill="toself",
            name="Typical Platforms",
            line=dict(color="#6366F1", width=2),
            fillcolor="rgba(99,102,241,0.08)",
        ))
        fig.add_trace(go.Scatterpolar(
            r=[9, 10, 9, 10, 9], theta=categories, fill="toself",
            name="HousingLens",
            line=dict(color="#38BDF8", width=2.5),
            fillcolor="rgba(56,189,248,0.10)",
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], color="#475569",
                                gridcolor="rgba(255,255,255,0.04)",
                                tickfont=dict(size=9, color="#475569")),
                angularaxis=dict(color="#94A3B8", gridcolor="rgba(255,255,255,0.04)",
                                 tickfont=dict(size=10)),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#94A3B8", size=11),
                        bgcolor="rgba(255,255,255,0.03)",
                        bordercolor="rgba(255,255,255,0.06)"),
            margin=dict(t=50, b=30, l=50, r=50),
            height=380,
            title=dict(text="Platform Capability Comparison",
                       font=dict(color="#94A3B8", size=12), x=0.5),
            font=dict(family="Inter", color="#94A3B8"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── CTA Banner ────────────────────────────────────────────────────────────
    cta = (
        '<div style="background:linear-gradient(135deg,rgba(14,165,233,0.08) 0%,rgba(124,58,237,0.08) 100%);'
        'border:1px solid rgba(56,189,248,0.18);border-radius:18px;padding:2.5rem 2rem;'
        'text-align:center;margin:1.5rem 0;position:relative;overflow:hidden;">'
        '<div style="position:absolute;top:0;left:0;right:0;height:2px;'
        'background:linear-gradient(90deg,#38BDF8,#A78BFA,#F97316);"></div>'
        '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.7rem;font-weight:800;'
        'color:#F1F5F9;margin-bottom:0.5rem;letter-spacing:-0.02em;">Ready to value a property?</div>'
        '<div style="color:#64748B;margin-bottom:0.5rem;font-size:0.95rem;">'
        'Use the <strong style="color:#38BDF8;">🔍 Predict Price</strong> page in the sidebar to get started instantly.'
        '</div></div>'
    )
    st.markdown(cta, unsafe_allow_html=True)


render()
