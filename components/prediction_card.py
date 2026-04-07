"""
HousingLens – Prediction Card Component
----------------------------------------
Renders a styled price prediction output card with range and IRI badge.
"""

import streamlit as st
from model.model_stub import format_lkr, format_lkr_short
from model.iri_calculator import iri_label, iri_colour


def render_prediction_card(price: float, price_low: float, price_high: float, iri: int) -> None:
    """
    Render the main prediction output card.

    Parameters
    ----------
    price      : float  Predicted price (LKR)
    price_low  : float  Low-end estimate
    price_high : float  High-end estimate
    iri        : int    Investment Risk Index (1–10)
    """
    label_text, css_class = iri_label(iri)
    colour = iri_colour(iri)

    # Determine risk icon
    risk_icon = "🟢" if iri <= 3 else ("🟡" if iri <= 6 else "🔴")

    st.markdown(f"""
    <div class="hl-pred-card hl-predict-active">
        <div class="hl-pred-label">⚡ Estimated Property Value</div>
        <div class="hl-pred-price">{format_lkr_short(price)}</div>
        <div class="hl-pred-price-sub">{format_lkr(price)}</div>
        <hr class="hl-divider" style="margin: 1rem 0;">
        <div style="display:flex; gap:1rem; margin-bottom:1rem; flex-wrap:wrap;">
            <div>
                <div class="hl-pred-label">Range Low</div>
                <div style="font-size:1.1rem; font-weight:600; color:#E8EDF5;">{format_lkr_short(price_low)}</div>
            </div>
            <div style="color:#3a4560; font-size:1.5rem; align-self:center;">→</div>
            <div>
                <div class="hl-pred-label">Range High</div>
                <div style="font-size:1.1rem; font-weight:600; color:#E8EDF5;">{format_lkr_short(price_high)}</div>
            </div>
        </div>
        <div class="hl-iri-badge {css_class}">
            {risk_icon} IRI {iri}/10 &nbsp;·&nbsp; {label_text}
        </div>
        <div style="margin-top:0.8rem; font-size:0.78rem; color:#8A94A8;">
            * Powered by HousingLens AI Engine · Sri Lankan residential market
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_mini_pred_card(label: str, price: float, iri: int, border_colour: str = "#00D4AA") -> None:
    """
    Compact comparison card for the Scenario Planner page.
    """
    label_text, _ = iri_label(iri)
    colour = iri_colour(iri)
    risk_icon = "🟢" if iri <= 3 else ("🟡" if iri <= 6 else "🔴")

    st.markdown(f"""
    <div style="
        background:#131827;
        border:1px solid {border_colour}55;
        border-top: 3px solid {border_colour};
        border-radius:12px;
        padding:1.3rem;
    ">
        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:{border_colour}; margin-bottom:0.6rem;">
            {label}
        </div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.9rem;
                    font-weight:700; color:#00D4AA; line-height:1;">
            {format_lkr_short(price)}
        </div>
        <div style="font-size:0.82rem; color:#8A94A8; margin:4px 0 10px 0;">{format_lkr(price)}</div>
        <div style="display:inline-flex; align-items:center; gap:6px;
                    padding:5px 12px; border-radius:20px;
                    background:rgba(0,0,0,0.3); border:1px solid {colour}44;
                    color:{colour}; font-size:0.88rem; font-weight:600;">
            {risk_icon} IRI {iri}/10 · {label_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
