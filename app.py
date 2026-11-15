import os
import sys
from pathlib import Path

# Add project root to sys.path so modules can import database and utils cleanly
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from dotenv import load_dotenv

# Load .env file
load_dotenv(ROOT_DIR / ".env")

from utils.ai_helper import (
    sanitize_api_key,
    test_api_connection,
    mask_api_key
)
from database.db import init_db
from modules.dashboard import render_dashboard
from modules.email_generator import render_email_generator
from modules.email_rewriter import render_email_rewriter
from modules.email_reply import render_email_reply
from modules.email_history import render_email_history
from modules.about_project import render_about_project

# Page configuration
st.set_page_config(
    page_title="MailGen AI - Intelligent Email Writing Assistant",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema
init_db()

# Load custom CSS
css_file = ROOT_DIR / "assets" / "style.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Navigation mapping as requested in requirements:
# 1. Dashboard
# 2. Generate Email
# 3. Rewrite Email
# 4. Generate Reply
# 5. Email History
# 6. About Project
NAVIGATION_MENU = {
    "Dashboard": ("📊", render_dashboard),
    "Generate Email": ("✉️", render_email_generator),
    "Rewrite Email": ("✎", render_email_rewriter),
    "Generate Reply": ("↩", render_email_reply),
    "Email History": ("📁", render_email_history),
    "About Project": ("ℹ️", render_about_project),
}

# Initialize session state for navigation
if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "Dashboard"

# Ensure nav_selection is valid
if st.session_state["nav_selection"] not in NAVIGATION_MENU:
    st.session_state["nav_selection"] = "Dashboard"

# Sidebar Architecture
with st.sidebar:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-icon-box">✉️</div>
            <div>
                <div class="brand-title">MailGen <span>AI</span></div>
                <div class="brand-subtitle">Intelligent Email Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-category-header">NAVIGATION</div>', unsafe_allow_html=True)

    menu_keys = list(NAVIGATION_MENU.keys())
    current_index = menu_keys.index(st.session_state["nav_selection"])

    selected_page = st.radio(
        "Navigation Menu",
        options=menu_keys,
        index=current_index,
        format_func=lambda x: f"{NAVIGATION_MENU[x][0]}  {x}",
        label_visibility="collapsed",
        key="sidebar_radio_nav"
    )

    # Sync selection if changed via radio
    if selected_page != st.session_state["nav_selection"]:
        st.session_state["nav_selection"] = selected_page
        st.rerun()

    st.markdown("---")

    st.markdown('<div class="sidebar-category-header">AI CONFIGURATION</div>', unsafe_allow_html=True)
    
    # Check for existing key in .env or secrets
    default_env_key = sanitize_api_key(os.getenv("GEMINI_API_KEY", ""))
    try:
        secret_key = sanitize_api_key(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        secret_key = ""

    current_stored_key = st.session_state.get("gemini_api_key", secret_key or default_env_key)

    entered_key = st.text_input(
        "Google Gemini API Key",
        value=current_stored_key,
        type="password",
        placeholder="AIzaSy...",
        help="Paste your free Gemini API key from Google AI Studio. It will be sanitized and used for this session.",
        key="sidebar_gemini_key_input"
    )
    
    # Sanitize key immediately
    clean_key = sanitize_api_key(entered_key)
    
    # If key was modified, reset verification status if key changed
    if clean_key != st.session_state.get("gemini_api_key"):
        st.session_state["gemini_api_key"] = clean_key
        st.session_state["api_test_result"] = None

    # Test Gemini API Connection Button
    if st.button("⚡ Test Gemini API Connection", width="stretch", key="btn_test_gemini_conn"):
        if not clean_key:
            st.session_state["api_test_result"] = ("MISSING_KEY", "Please enter an API key first.")
        else:
            with st.spinner("Pinging Google Gemini API..."):
                success, cat, msg = test_api_connection(clean_key)
                st.session_state["api_test_result"] = (cat, msg)

    # Render API Key and Test Status
    test_result = st.session_state.get("api_test_result")
    if test_result:
        cat, msg = test_result
        if cat == "SUCCESS":
            st.success(f"✅ {msg}")
        elif cat == "INVALID_KEY":
            st.error("❌ Invalid API Key (400 / 401)")
            st.caption("Google rejected this key. Ensure you copied the entire key starting with `AIza` from Google AI Studio.")
        elif cat == "PERMISSION_DENIED":
            st.error("🚫 Permission Denied (403)")
            st.caption("The Google Cloud project or key does not have permission to access the Gemini API.")
        elif cat == "RATE_LIMIT":
            st.error("⏳ Quota / Rate Limit (429)")
            st.caption("Free tier quota exceeded. Please wait a few moments before trying again.")
        elif cat == "NETWORK_ERROR":
            st.error("🌐 Network Connection Error")
            st.caption("Unable to reach Google API servers. Check your internet connection.")
        elif cat == "MISSING_KEY":
            st.warning("⚠️ Please enter a Gemini API key.")
        else:
            st.error(f"❌ Error: {msg}")
    elif not clean_key:
        st.markdown(
            """
            <div style="font-size: 11px; color: #f59e0b; margin-top: 4px;">
                ⚠️ <strong>Key Missing:</strong> <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #818cf8; text-decoration: underline;">Get free API key</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; display: flex; align-items: center; gap: 5px;">
                <span class="pulse-dot" style="background:#f59e0b; box-shadow:0 0 8px #f59e0b;"></span> Key entered: <code>{mask_api_key(clean_key)}</code> (Click Test to verify)
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # College Project Badge in Sidebar
    st.markdown(
        """
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(148, 163, 184, 0.12); border-radius: 10px; padding: 10px; font-size: 11px; color: #94a3b8;">
            <div style="font-weight: 700; color: #cbd5e1; margin-bottom: 2px;">🎓 B.Tech CSE (AI)</div>
            College Capstone Project Edition<br>
            <span style="font-size: 10px; color: #64748b;">SQLite Local DB · Google GenAI</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Top Bar Breadcrumbs
active_section = st.session_state["nav_selection"]
st.markdown(
    f"""
    <div class="top-nav-bar">
        <div>
            <span>MAILGEN AI</span> &nbsp;/&nbsp; <span class="page-tag">{active_section.upper()}</span>
        </div>
        <div class="pill-badge">
            <span class="pulse-dot"></span> SECURE WORKSPACE &nbsp;•&nbsp; LOCAL SQLITE ACTIVE
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Render the active section
icon, page_renderer = NAVIGATION_MENU[active_section]
page_renderer()
