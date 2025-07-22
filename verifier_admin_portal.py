# verifier_admin_portal.py
import streamlit as st
from verifier_manage_ui import main as manage_verifier_ui
from verifier_organisation_ui_db import main as upload_verifier_ui  # updated reference

# === Add frontend path so we can import app.py cleanly ===
import sys
from pathlib import Path

FRONTEND_PATH = Path(__file__).parent / "frontend"
sys.path.append(str(FRONTEND_PATH))

from app_admin import main as run_kyc_app  # app.py must have main()

# ===========================
# 🧭 Unified Sidebar Navigation
# ===========================
def main():
    st.set_page_config(page_title="Verifier Admin Portal", layout="wide")
    st.sidebar.title("🧭 Navigation")

    page = st.sidebar.radio("Go to", [
        "🏦 Video KYC Main App",
        "📥 Upload Verifiers (CSV)",
        "✏️ Manage Existing Verifiers"
    ])

    if page == "🏦 Video KYC Main App":
        run_kyc_app()

    elif page == "📥 Upload Verifiers (CSV)":
        upload_verifier_ui()

    elif page == "✏️ Manage Existing Verifiers":
        manage_verifier_ui()

if __name__ == "__main__":
    main()
