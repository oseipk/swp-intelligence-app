# modules/auth.py

import streamlit as st
import requests
from modules import logger

# 🔐 Admin override list
ADMIN_EMAILS = {
    "kwadwo.osei@gh.nestle.com",
    "your.colleague@xx.nestle.com",
    "analytics.admin@nestle.com"
}

def get_user_country_code():
    """
    Fetches the user's country code using IP geolocation.
    """
    try:
        response = requests.get("https://ipapi.co/json", timeout=3)
        if response.status_code == 200:
            return response.json().get("country_code", "").lower()
    except:
        pass
    return ""

def extract_region_from_email(email):
    """
    Extracts the regional subdomain from a Nestlé email.
    Example: gh.nestle.com → "gh"
    """
    try:
        domain_part = email.split("@")[1]
        subdomain = domain_part.split(".")[0]
        return subdomain.lower()
    except:
        return ""

def email_authenticate():
    """
    Streamlit auth block: checks email, verifies region, handles admin override,
    logs attempts, and updates session state.
    """
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        st.title("🔐 Nestlé Internal Access")


    # Initialize session state keys
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None

    # Show login input only if not authenticated
    if not st.session_state['authenticated']:
        email = st.text_input("Enter your Nestlé email", placeholder="your.name@gh.nestle.com")
        login_button = st.button("Login")

        if login_button:
            email = email.lower()
            email_valid = email.endswith(".nestle.com")
            email_region = extract_region_from_email(email)
            ip_region = get_user_country_code()
            is_admin = email in ADMIN_EMAILS

            # Log login attempt with region info
            login_note = f"Login (email_region={email_region}, ip_region={ip_region}, admin={is_admin})"
            logger.log_access(email, page=login_note)

            # Auth logic
            if email_valid and (email_region == ip_region or is_admin):
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = email
                st.session_state['last_logged_page'] = None  # Reset tracker on login

                if is_admin:
                    st.info(" Admin override: region mismatch bypassed.")
                elif email_region != ip_region:
                    st.warning(f" VPN detected: {email_region} ≠ {ip_region.upper()}")

                st.success(f"Access granted for {email}")
                st.rerun()
            else:
                st.error(" Access denied. Your email must match your region or contact the admin.")

    return st.session_state['authenticated'], st.session_state['user_email']
