# app/main.py

from dotenv import load_dotenv
load_dotenv()

import sys
import os
import streamlit as st
from collections import OrderedDict
from datetime import datetime, timedelta
import feedparser
import requests


# Add root path for import resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# === Import all modules ===
from modules import (
    auth,
    logger,
    ui,
    landing_page,
    driver_definition,
    workforce_model,
    business_correlation,
    elasticity_modeling,
    headcount_forecast,
    scenario_planning,
    gap_analysis,
    gap_management,
    gap_strategy_analysis,
    action_planning,
)

# === Inject Custom Styles ===
def inject_custom_styles():
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .stApp {
            font-family: 'Segoe UI', sans-serif;
            padding: 2rem;
        }

        section[data-testid="stSidebar"] {
            width: 250px !important;
        }

        .stRadio > div {
            gap: 10px;
        }

        .stDataFrame, .css-1d391kg {
            background-color: white;
            border-radius: 8px;
        }

        h1, h2, h3 {
            color: #0A5A9C;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_styles()

# === Authenticate user via Nestlé email ===
authenticated, user_email = auth.email_authenticate()
if not authenticated:
    st.stop()

# === Helper functions for welcome banner ===
def get_ip_region():
    try:
        response = requests.get("https://ipapi.co/json", timeout=3)
        if response.status_code == 200:
            return response.json().get("country_code", "").lower()
    except:
        pass
    return ""

def extract_user_info(email):
    try:
        name_part = email.split("@")[0]
        first_name = name_part.split(".")[0].capitalize()
        domain_part = email.split("@")[1]
        region_code = domain_part.split(".")[0].lower()
        return first_name, region_code
    except:
        return "User", "unknown"

def show_welcome_banner():
    email = st.session_state.get("user_email", "")
    if not email:
        return
    first_name, email_region = extract_user_info(email)
    ip_region = get_ip_region()

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
        <div style="background-color:#e8f4ff;padding:10px;border-radius:8px;margin-bottom:20px;">
            <b>👋 Welcome, {first_name}!</b><br>
            You are signed in from <code>@{email_region}.nestle.com</code>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if ip_region and ip_region != email_region:
            st.warning("VPN? IP region ≠ email region")

# === Define all pages ===
PAGES = OrderedDict({
    "Landing Page": landing_page.render_landing_page,
    "Business Demand Driver": driver_definition.render_driver_definition,
    "Workforce Data Insights": workforce_model.render_headcount_input,
    "Workforce Correlation": business_correlation.render_driver_headcount_correlation,
    "Elasticity Modeling": elasticity_modeling.render_elasticity_modeling,
    "Critical Workforce Forecast": headcount_forecast.render_critical_workforce_forecasting,
    "Scenario Planning": scenario_planning.render_scenario_planning,
    "Gap Analysis": gap_analysis.render_gap_analysis,
    "Workforce Strategy": gap_management.render_gap_management,
    "Gap Strategy Analysis": gap_strategy_analysis.render_gap_strategy_analysis,
    "Action Planning": action_planning.render_action_planning
})

# === Auto-refresh news every 2 minutes ===
NEWS_REFRESH_MINUTES = 2
if "news_last_refresh" not in st.session_state:
    st.session_state["news_last_refresh"] = datetime.now()
else:
    elapsed = datetime.now() - st.session_state["news_last_refresh"]
    if elapsed > timedelta(minutes=NEWS_REFRESH_MINUTES):
        st.session_state["news_last_refresh"] = datetime.now()
        st.rerun()

# === Sidebar navigation ===
with st.sidebar:
    st.header("📁 Navigate Modules")

    selected_page = st.selectbox(
        "", list(PAGES.keys()),
        index=list(PAGES.keys()).index(st.session_state.get("current_page", list(PAGES.keys())[0]))
    )
    st.session_state["current_page"] = selected_page

    # === Logout Button ===
    st.markdown("---")
    st.subheader("🔐 Account")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    # === Contact Info ===
    st.markdown("---")
    st.subheader("Contact")
    st.markdown("For support or suggestions, please reach out to:")
    st.markdown('📬 **[People Analytics Team](mailto:kwadwo.osei@gh.nestle.com)**')

# === Page Title + Welcome Banner ===
st.title("📊 Nestlé People Analytics")


# === Log and Render selected page ===
if st.session_state.get("authenticated", False):
    current_page = st.session_state["current_page"]
    last_page = st.session_state.get("last_logged_page")

    if last_page != current_page:
        logger.log_access(st.session_state["user_email"], page=current_page)
        st.session_state["last_logged_page"] = current_page

    PAGES[current_page]()  # Render the selected page

# === Continue Button ===
page_keys = list(PAGES.keys())
current_idx = page_keys.index(st.session_state["current_page"])

if current_idx < len(page_keys) - 1:
    if st.button("➡️ Continue", key=f"continue_{current_idx}"):
        st.session_state["current_page"] = page_keys[current_idx + 1]
        st.rerun()
