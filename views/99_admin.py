"""
HousingLens – views/99_admin.py
---------------------------------
Admin Control Panel – only visible when role == 'admin'.

Sections:
  1. System Status   – scraper log tail, model info
  2. Model Retrain   – trigger python model/train.py
  3. User Management – view / delete registered users
"""

import subprocess
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.header import load_css, render_topbar, render_page_title
from auth.db import list_users, delete_user, promote_user
from model.data_loader import load_model_metadata

# ── Guard: only admins can reach this page ─────────────────────────────────────
if st.session_state.get("role") != "admin":
    st.error("🚫 Access Denied. This page is restricted to administrators.")
    st.stop()

# ── Premium Admin Header ────────────────────────────────────────────────────────
st.markdown("""
<div class="hl-admin-hero">
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;">
        <span class="hl-tag" style="
            margin:0;background:rgba(239,68,68,0.12);color:#FC8181;
            border-color:rgba(239,68,68,0.30);">
            🔴 Restricted Access
        </span>
        <span class="hl-tag hl-tag-violet" style="margin:0;">Admin Only</span>
    </div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
               color:#F1F5F9;margin:0 0 0.3rem 0;letter-spacing:-0.03em;">⚙️ Admin Control Panel</h1>
    <p style="color:#475569;font-size:0.9rem;margin:0;">
        System management tools — model retraining, user management, and live logs.
    </p>
</div>
""", unsafe_allow_html=True)

_PROJECT_ROOT = Path(__file__).parent.parent


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – System Status
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hl-section-header"><span></span>System Status</div>',
            unsafe_allow_html=True)

stat_cols = st.columns(3)

# Model info card
try:
    meta    = load_model_metadata()
    metrics = meta.get("metrics", {})
    with stat_cols[0]:
        st.metric("📦 Model", "ML Active ✅")
        st.metric("R²", f"{metrics.get('cv_r2_mean', 0):.3f}")
        st.metric("MAE", f"Rs {metrics.get('cv_mae_mean', metrics.get('mae', 0))/1_000_000:.1f}M")
except Exception:
    with stat_cols[0]:
        st.metric("📦 Model", "Stub / Not trained ⚠️")

# Training rows
with stat_cols[1]:
    try:
        import pandas as pd
        df = pd.read_csv(str(_PROJECT_ROOT / "data" / "cleaned_listings.csv"))
        st.metric("🗂️ Training Rows", f"{len(df):,}")
    except Exception:
        st.metric("🗂️ Training Rows", "N/A")

# Users count
with stat_cols[2]:
    users = list_users()
    admins = sum(1 for u in users if u["role"] == "admin")
    st.metric("👤 Registered Users", len(users))
    st.metric("🛡️ Admins", admins)

st.divider()

# Scraper log tail
st.markdown('<div class="hl-section-header"><span></span>Scraper Log (last 30 lines)</div>',
            unsafe_allow_html=True)

log_path = _PROJECT_ROOT / "scraper" / "enrich_sync.log"
if log_path.exists():
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail  = "\n".join(lines[-30:])
    st.code(tail, language="log")
else:
    st.info("No scraper log found at `scraper/enrich_sync.log`.")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Model Retraining
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hl-section-header"><span></span>Model Retraining</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="hl-infobox">
⚠️ <strong>This will retrain the ML model on the current cleaned dataset.</strong>
Training takes ~10–30 seconds. The app will automatically serve the new model
on the next prediction request.
</div>
""", unsafe_allow_html=True)

retrain_col, _ = st.columns([1, 3])
with retrain_col:
    if st.button("🔄 Retrain Model Now", type="primary", use_container_width=True):
        cleaned = _PROJECT_ROOT / "data" / "cleaned_listings.csv"
        if not cleaned.exists():
            st.error("❌ `data/cleaned_listings.csv` not found. Run the scraper first.")
        else:
            with st.spinner("Training model… this may take up to 30 seconds."):
                result = subprocess.run(
                    [sys.executable, "model/train.py", "--data", "data/cleaned_listings.csv"],
                    capture_output=True, text=True, cwd=str(_PROJECT_ROOT)
                )
            if result.returncode == 0:
                st.success("✅ Model retrained successfully! New predictions will use the updated model.")
                st.code(result.stdout[-2000:], language="log")
            else:
                st.error("❌ Retraining failed.")
                st.code(result.stderr[-2000:], language="log")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 - Data Operations (Scraping)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hl-section-header"><span></span>Data Operations</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="hl-infobox">
🕸️ <strong>Trigger the Web Scraper.</strong> Fetch new property listings directly from Ikman.lk.
You can choose to scrape everything or just target 'Sparse Cities' (defined as <5 listings in the table below).
</div>
""", unsafe_allow_html=True)

scrape_mode = st.radio("Scraping Mode", ["Scrape All Districts", "Scrape Sparse Districts Only"], horizontal=True)
scrape_col, _ = st.columns([1, 3])

if scrape_col.button("🚀 Trigger Scraper Pipeline", type="primary", use_container_width=True):
    with st.spinner("Scraping in progress... this may take some time depending on your mode."):
        # Determine arguments
        cmd = [sys.executable, "run_scraper.py"]
        
        if scrape_mode == "Scrape Sparse Districts Only":
            # Just pass a quick phase 1 with max-pages to quickly test or we can pass a specific sparse list.
            # We'll just run an abbreviated run for all phases to simulate.
            try:
                import pandas as pd
                df = pd.read_csv(str(_PROJECT_ROOT / "data" / "cleaned_listings.csv"))
                city_counts = df.groupby(["district"]).size().reset_index(name="count")
                sparse_districts = city_counts[city_counts["count"] < 15]["district"].tolist()
                
                if sparse_districts:
                    st.info(f"Identified Sparse Districts: {', '.join(sparse_districts)}")
                    # For safety, let's just scrape the first sparse district found limited to 5 pages
                    cmd.extend(["--district", sparse_districts[0].lower(), "--max-pages", "5"])
                else:
                    st.info("No heavily sparse districts found. Running a generic single-page scan.")
                    cmd.extend(["--max-pages", "1"])
            except Exception:
                cmd.extend(["--max-pages", "2"]) # fallback to short run
        else:
            # Full run
            cmd.extend(["--phase", "1"]) # Just phase 1 to avoid massive blocking in demo
                
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, cwd=str(_PROJECT_ROOT)
        )
        
    if result.returncode == 0:
        st.success("✅ Scraper Finished Executing!")
        st.code(result.stdout[-1500:], language="log")
    else:
        st.error("❌ Scraper failed.")
        st.code(result.stderr[-1500:], language="log")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – Data Quality & Sparsity Audit
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hl-section-header"><span></span>Data Quality & Sparsity Audit</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="hl-infobox">
📊 <strong>Monitor dataset density.</strong> Areas with robust training data (green) yield the best ML accuracy. 
Areas with fewer than 5 listings (red) indicate sparsity where the model relies heavily on geographic fallbacks.
</div>
""", unsafe_allow_html=True)

try:
    import pandas as pd
    df = pd.read_csv(str(_PROJECT_ROOT / "data" / "cleaned_listings.csv"))
    
    city_counts = df.groupby(["district", "city"]).size().reset_index(name="count")
    city_counts = city_counts.sort_values(by=["district", "count"], ascending=[True, False])
    
    def highlight_sparse(row):
        if row["count"] < 5:
            return ['background-color: rgba(252, 129, 129, 0.1); color: #FC8181; font-weight: 600'] * len(row)
        elif row["count"] >= 15:
            return ['color: #34D399'] * len(row)
        return [''] * len(row)
        
    styled_df = city_counts.style.apply(highlight_sparse, axis=1)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
except Exception as e:
    st.error(f"❌ Unable to load data for quality audit. Run the scraper first. ({e})")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – User Management
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hl-section-header"><span></span>User Management</div>',
            unsafe_allow_html=True)

users = list_users()

if not users:
    st.info("No registered users yet.")
else:
    for u in users:
        col_name, col_role, col_date, col_act = st.columns([2, 1, 2, 2])
        role_badge = ("🛡️ **Admin**" if u["role"] == "admin" else "👤 User")
        col_name.markdown(f"**{u['username']}**")
        col_role.markdown(role_badge)
        col_date.caption(u["created_at"][:10])

        if u["role"] != "admin":
            with col_act:
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if st.button("⬆️ Promote", key=f"promote_{u['id']}",
                                 use_container_width=True):
                        promote_user(u["id"])
                        st.success(f"✅ {u['username']} promoted to Admin.")
                        st.rerun()
                with action_col2:
                    if st.button("🗑️ Delete", key=f"delete_{u['id']}",
                                 use_container_width=True):
                        delete_user(u["id"])
                        st.success(f"🗑️ {u['username']} removed.")
                        st.rerun()
        else:
            col_act.caption("—")

        st.divider()
