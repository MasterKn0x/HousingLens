"""
HousingLens – Shared Header / Branding Component
--------------------------------------------------
Injects the HousingLens logo strip and loads the custom CSS stylesheet.
"""

import streamlit as st
from pathlib import Path


import base64

def get_base64_image(image_path: str | Path) -> str:
    path = Path(image_path)
    if not path.exists():
        return ""
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def load_css() -> None:
    """Load the custom stylesheet into the Streamlit page."""
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        st.logo(str(logo_path))

    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def get_logo_html(width="40px", height="40px", border_radius="10px") -> str:
    """Returns HTML for the custom Base64 injected logo, or a fallback."""
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    b64_logo = get_base64_image(logo_path)
    
    if b64_logo:
        return f'<img src="data:image/png;base64,{b64_logo}" style="width:{width}; height:{height}; border-radius:{border_radius}; object-fit:cover; flex-shrink:0;">'
    else:
        return f'<div style="background: linear-gradient(135deg, #00D4AA, #7B61FF); border-radius: {border_radius}; width: {width}; height: {height}; display: flex; align-items: center; justify-content: center; font-size: calc({width}/2.5); flex-shrink:0;">🏠</div>'

def render_topbar(subtitle: str = "") -> None:
    """
    Render the HousingLens top branding bar.

    Parameters
    ----------
    subtitle : str  Optional page-level subtitle shown below the logo.
    """
    logo_html = get_logo_html(width="40px", height="40px", border_radius="10px")

    sub_html = f'<div style="font-size:0.9rem; color:#8A94A8; margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; padding:0.5rem 0 1.2rem 0;
                border-bottom:1px solid rgba(0,212,170,0.12); margin-bottom:1.5rem;">
        {logo_html}
        <div>
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:1.25rem; font-weight:700; color:#E8EDF5;
                line-height:1.2;
            ">HousingLens</div>
            {sub_html}
        </div>
        <div style="margin-left:auto; text-align:right;">
            <div class="hl-badge">Beta</div>
            <div class="hl-badge">Sri Lanka</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_page_title(icon: str, title: str, description: str = "") -> None:
    """Render a consistent page-level title with icon."""
    desc_html = f'<p style="color:#8A94A8; font-size:0.95rem; margin:0.3rem 0 0 0;">{description}</p>' if description else ""
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="
            font-family:'Space Grotesk',sans-serif;
            font-size:1.9rem; font-weight:700; color:#E8EDF5;
            margin:0; display:flex; align-items:center; gap:12px;
        ">{icon} {title}</h1>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)
