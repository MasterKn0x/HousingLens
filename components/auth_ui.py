"""
HousingLens – components/auth_ui.py
--------------------------------------
Premium centered authentication screen.
"""

import streamlit as st
from auth.db import verify_login, register_user
from components.header import get_logo_html

def render_auth_screen():
    # Inject auth-specific styles
    st.markdown(
        '<style>'
        '/* Hide sidebar and header */'
        'section[data-testid="stSidebar"] { display: none !important; }'
        '[data-testid="collapsedControl"] { display: none !important; }'
        'header { display: none !important; }'
        
        '/* Constrain central layout */'
        '.block-container { '
        '    padding-top: 5rem !important; '
        '    max-width: 480px !important; '
        '    margin: 0 auto !important; '
        '}'
        
        '/* Style the Forms into Glass Cards */'
        'div[data-testid="stForm"] { '
        '    background: rgba(17, 24, 39, 0.80) !important;'
        '    backdrop-filter: blur(24px) !important;'
        '    -webkit-backdrop-filter: blur(24px) !important;'
        '    border: 1px solid rgba(255, 255, 255, 0.08) !important;'
        '    border-top: 3px solid #38BDF8 !important;'
        '    border-radius: 16px !important;'
        '    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.6) !important;'
        '    padding: 2.5rem 2rem !important;'
        '}'

        '/* Buttons */'
        'div[data-testid="stFormSubmitButton"] > button {'
        '    height: 3rem;'
        '    font-weight: 700;'
        '    background: linear-gradient(90deg, #38BDF8, #A78BFA) !important;'
        '    border: none !important;'
        '    color: white !important;'
        '    border-radius: 8px;'
        '    transition: opacity 0.2s;'
        '}'
        'div[data-testid="stFormSubmitButton"] > button:hover {'
        '    opacity: 0.9;'
        '}'
        '</style>',
        unsafe_allow_html=True
    )

    # ── Centered Brand Header ──────────────────────────────────────────
    st.markdown(
        f'<div style="text-align:center;margin-bottom:2.5rem;">'
        f'<div style="margin-bottom:1.5rem; display:inline-flex; filter: drop-shadow(0 10px 30px rgba(14,165,233,0.3));">'
        f'{get_logo_html(width="64px", height="64px", border_radius="18px")}</div>'
        '<h1 style="font-family:\'Space Grotesk\',sans-serif;font-size:2.4rem;font-weight:800;'
        'color:#F1F5F9;margin:0 0 0.5rem 0;letter-spacing:-0.03em;">'
        'Housing<span style="color:#38BDF8;">Lens</span></h1>'
        '<p style="color:#94A3B8;font-size:0.95rem;margin:0;">AI Property Valuation Platform</p>'
        '</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with tab_login:
        with st.form("hl_login_form", clear_on_submit=False):
            st.markdown(
                '<div style="font-size:0.75rem;font-weight:700;color:#94A3B8;'
                'text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Username</div>',
                unsafe_allow_html=True
            )
            username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed")
            st.markdown(
                '<div style="margin-top:1rem;font-size:0.75rem;font-weight:700;color:#94A3B8;'
                'text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Password</div>',
                unsafe_allow_html=True
            )
            password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
            
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = verify_login(username, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user["username"]
                    st.session_state["role"] = user["role"]
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
                    
    with tab_register:
        with st.form("hl_register_form", clear_on_submit=False):
            st.markdown(
                '<div style="font-size:0.75rem;font-weight:700;color:#94A3B8;'
                'text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Choose Username</div>',
                unsafe_allow_html=True
            )
            new_username = st.text_input("Username", placeholder="Enter new username", label_visibility="collapsed")
            
            st.markdown(
                '<div style="margin-top:1rem;font-size:0.75rem;font-weight:700;color:#94A3B8;'
                'text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Choose Password</div>',
                unsafe_allow_html=True
            )
            new_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", label_visibility="collapsed")
            confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", label_visibility="collapsed")

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

        if submitted:
            if new_password != confirm_pwd:
                st.error("❌ Passwords do not match.")
            else:
                ok, msg = register_user(new_username, new_password, role="user")
                if ok:
                    st.success(f"✅ {msg} You can now sign in.")
                else:
                    st.error(f"❌ {msg}")

    st.markdown(
        '<div style="text-align:center;color:#475569;font-size:0.8rem;margin-top:2rem;">'
        '🔒 Encrypted connection. No data is retained beyond session.'
        '</div>',
        unsafe_allow_html=True
    )
