# modules/auth.py

import streamlit as st
import requests
import re
from modules import logger

# 🔐 Admin override list
ADMIN_EMAILS = {
    "kwadwo.osei@gh.nestle.com",
    "your.colleague@xx.nestle.com",
    "analytics.admin@nestle.com"
}

# 🔐 Toggle strict region matching
STRICT_REGION_MATCH = False  # Set to True to enforce strict region validation

# Regex pattern for Nestlé email validation
NESTLE_EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-z]{2,3}\.nestle\.com$"


def is_valid_nestle_email(email):
    """
    Validates email format against Nestlé domain and pattern.
    """
    return re.match(NESTLE_EMAIL_PATTERN, email) is not None


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

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None

    if not st.session_state['authenticated']:
        email = st.text_input("Enter your Nestlé email")
        login_button = st.button("Login")

        if login_button:
            email = email.lower()
            email_valid = is_valid_nestle_email(email)
            email_region = extract_region_from_email(email)
            ip_region = get_user_country_code()
            is_admin = email in ADMIN_EMAILS

            # Log login attempt with region info
            login_note = f"Login (email_region={email_region}, ip_region={ip_region}, admin={is_admin})"
            logger.log_access(email, page=login_note)

            # Authentication logic
            if email_valid and (
                email_region == ip_region or is_admin or not STRICT_REGION_MATCH
            ):
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = email
                st.session_state['last_logged_page'] = None  # Reset on login

                # Feedback messages
                if is_admin:
                    st.info("Admin override: region mismatch bypassed.")
                elif email_region != ip_region:
                    st.warning(f" Region mismatch detected (email: {email_region} ≠ IP: {ip_region.upper()}). If you’re using a VPN, this is expected.")
                else:
                    st.success(f" Region verified: {email_region}")

                st.success(f"Access granted for {email}")
                st.rerun()

            else:
                st.error("Access denied. Invalid Nestlé email or region mismatch. Contact the People Analytics Team.")

    # Optionally provide logout
    elif st.session_state['authenticated']:
        st.write(f"Logged in as **{st.session_state['user_email']}**")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully.")
            st.rerun()

    return st.session_state['authenticated'], st.session_state['user_email']
