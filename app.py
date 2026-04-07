"""
HousingLens – Main Entry Point (app.py)
-----------------------------------------
Master router using Streamlit 1.36+ st.navigation API.

Authentication model:
  - Public users MUST log in (register or sign in) before accessing any page.
  - Admins see an extra "Admin Control Panel" in the navigation sidebar.
  - No property or personal data is stored beyond session login credentials.

Run with: streamlit run app.py
"""

import streamlit as st
from components.header import load_css, get_logo_html

# ── Global Page Configuration ─────────────────────────────────────────────────
st.set_page_config(
    page_title="HousingLens – AI Property Valuation",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="auto",
)

# Load the custom "Vibrant Slate" CSS Theme globally
load_css()

# ── Initialise session auth state ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# ── Auth Gate ─────────────────────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    from components.auth_ui import render_auth_screen
    render_auth_screen()
    st.stop()   # Do NOT render the navigation below for unauthenticated users

# ── Global Sidebar Branding (only shown when authenticated) ───────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0;">
        <div style="margin-bottom:0.8rem; display:inline-flex;">
            {get_logo_html(width="60px", height="60px", border_radius="16px")}
        </div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.4rem;
                    font-weight:700; color:#E8EDF5;">HousingLens</div>
        <div style="font-size:0.78rem; color:#8A94A8; margin-top:4px;">
            AI Property Valuation · Sri Lanka
        </div>
    </div>
    <hr style="border-color:rgba(0,212,170,0.1);"/>
    """, unsafe_allow_html=True)

    # ── User badge + logout ───────────────────────────────────────────────────
    role       = st.session_state["role"]
    username   = st.session_state["username"]
    badge_icon = "🛡️" if role == "admin" else "👤"
    badge_col  = "#7B61FF" if role == "admin" else "#00D4AA"

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(0,212,170,0.12);
                border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.8rem;">
        <div style="font-size:0.72rem;color:#8A94A8;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:2px;">Signed in as</div>
        <div style="font-weight:700;color:{badge_col};font-size:0.95rem;">
            {badge_icon} {username}
        </div>
        <div style="font-size:0.72rem;color:#8A94A8;text-transform:uppercase;
                    letter-spacing:0.06em;">{role.capitalize()}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        for key in ["authenticated", "username", "role"]:
            st.session_state[key] = None
        st.session_state["authenticated"] = False
        st.rerun()

    st.markdown("<hr style='border-color:rgba(0,212,170,0.08);'/>", unsafe_allow_html=True)


# ── Navigation Definition (role-aware) ────────────────────────────────────────

pg_home     = st.Page("views/00_home.py",     title="Home",             icon="🏡", default=True)
pg_predict  = st.Page("views/01_predict.py",  title="Predict Price",    icon="🔍")
pg_analytic = st.Page("views/02_analytics.py", title="Analytics",       icon="📊")
pg_scenario = st.Page("views/03_scenario.py", title="Scenario Planner", icon="🔮")
pg_about    = st.Page("views/04_about.py",    title="About",            icon="ℹ️")

nav_sections = {
    "Main Dashboard": [pg_home, pg_predict],
    "Tools":          [pg_analytic, pg_scenario],
    "Information":    [pg_about],
}

# Admins get an extra locked section
if st.session_state["role"] == "admin":
    pg_admin = st.Page("views/99_admin.py", title="Admin Panel", icon="⚙️")
    nav_sections["Administration"] = [pg_admin]

pg = st.navigation(nav_sections)
pg.run()
