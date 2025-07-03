import streamlit as st
from modules import ui

def render_landing_page():
    # === Custom Styling ===
    st.markdown("""
    <style>
        body {
            background-color: #f3f3f3;
        }
        .reportview-container .main .block-container{
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
            background-color: #f5f9fc;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .css-1d391kg, .css-1kyxreq, .css-qbe2hs {
            font-size: 16px !important;
            color: #003B71;
        }
        .sidebar .sidebar-content {
            background-color: #e6f0fa;
            padding: 1rem;
        }
        h1, h2, h3 {
            color: #004B8D;
        }
        ul {
            margin-left: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # === Page Title ===
    st.title("🌐 Welcome to the Future of Workforce Planning")

    # === Intro ===
    st.markdown("""
    Discover a smarter way to **analyze, forecast, and plan** your workforce. 

    This intuitive platform is designed to help you make **strategic, data-informed decisions** about your organization's talent needs—aligned with business priorities, evolving demand drivers, and operational realities.

    ---
    """)

    # === Project Overview ===
    st.header("📘 Project Overview")
    st.markdown("""
    Our mission is to help you make **confident workforce decisions** by:

    - Identifying and tracking key business demand drivers
    - Forecasting workforce needs using driver elasticity
    - Simulating multiple scenarios (e.g., attrition, retirement, internal mobility)
    - Pinpointing future talent gaps or surpluses
    - Applying the strategic 4Bs workforce framework
    - Defining actionable plans to close critical gaps
    """)

    # === Guide ===
    st.header("📒 How to Use This Tool")
    st.markdown("Follow the step-by-step modules to build your strategic workforce plan:")

    st.markdown("""
    ### 1. 🔍 Define Demand Drivers
    Identify the business trends that shape your talent needs. Input up to 4 years of historical KPIs.

    ### 2. 👥 Input Headcount Data
    Define your core functions and input historical headcount data to build your baseline.

    ### 3. 📈 Correlate Drivers & Headcount
    Discover which business drivers most strongly influence workforce demand.

    ### 4. 🧰 Model Elasticity
    Understand how responsive your workforce needs are to changes in each demand driver.

    ### 5. 🚨 Forecast Critical Workforce
    Project future needs for high-impact roles using elasticity and business trends.

    ### 6. 🤞 Plan Scenarios
    Layer in assumptions like attrition and retirement to stress-test your forecasts.

    ### 7. ⚖️ Conduct Gap Analysis
    Identify workforce shortfalls and surpluses across years and functions.

    ### 8. 🧠 Strategize with the 4Bs
    Apply targeted strategies: **Buy**, **Build**, **Borrow**, or **Boost** to bridge talent gaps.

    ### 9. 🔎 Analyze Strategies
    Dive deeper into role-specific strategies and see what actions make the most impact.

    ### 10. 🎯 Plan & Prioritize Actions
    Define initiatives, estimate costs, and prioritize actions aligned to business goals.

    ---
    Ready to plan a future-ready workforce? Start with your demand drivers.
    """)
