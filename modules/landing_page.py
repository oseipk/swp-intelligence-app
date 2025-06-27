import streamlit as st
from modules import ui

def render_landing_page():
    # === Custom Styling ===
    st.markdown("""
    <style>
        .css-1d391kg, .css-1kyxreq, .css-qbe2hs {
            font-size: 16px !important;
        }
        .sidebar .sidebar-content {
            background-color: #f4f4f4;
            padding: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # === Page Title ===
    st.title(" Welcome to the Future Workforce Planning")

    # === Intro ===
    st.markdown("""
    This application is designed to help you **analyze, forecast, and plan** your workforce needs 
    based on **business demand drivers, strategic priorities, and operational realities** over a multi-year horizon.

    ---
    """)

    # === Project Overview ===
    st.header("📘 Project Overview")
    st.markdown("""
    The purpose of this tool is to enable **data-driven workforce decisions** by:

    - Identifying business demand drivers.
    - Forecasting future workforce needs based on elasticity.
    - Simulating scenarios considering attrition, retirement and internal pipelines.
    - Conducting gap analysis to identify future surpluses or shortfalls.
    - Assigning strategic actions using the 4Bs strategy.
    - Planning initiatives to close identified workforce gaps.
    """)

    # === Guide ===
    st.header("How to Use This Application")
    st.markdown("Follow the modules in sequence to build your strategic workforce plan:")

    st.markdown("""
    ### 1. 🔍 **Demand Driver Definition**
    - Select key business demand drivers (e.g., E-Commerce Growth, e-NNS, etc.).
    - Input 4 years of historical KPI values for each.

    ### 2. 👥 **Headcount Input**
    - Define functional units (Sales, IT, etc.).
    - Enter headcount values across the same historical 4 years.

    ### 3. 📈 **Driver–Headcount Correlation**
    - Map drivers to functions.
    - Automatically calculate which drivers correlate strongly with workforce changes.

    ### 4. 🧮 **Elasticity Modeling**
    - Elasticity is calculated to determine how sensitive workforce needs are to demand driver changes.

    ### 5. 🚨 **Critical Workforce Forecasting**
    - Define critical roles (e.g., Data Scientist, Sales Analyst).
    - Assign critical roles to Function Units.
    - Assign roles to drivers with weightings.
    - Forecast future role needs using driver elasticity and forecasted KPI trends.

    ### 6. 🧪 **Scenario Planning**
    - Apply attrition, retirement, and internal pipeline assumptions.
    - Visualize base demand, scenario demand, and supply lines.

    ### 7. ⚖️ **Gap Analysis**
    - Identify shortfalls and surpluses by role and year.
    - Compute percentage gaps and future workforce risk.

    ### 8. 🧠 **Gap Management with 4Bs Strategy**
    - Automatically categorize each role using the 4Bs:
        - **Buy** → hire externally  
        - **Build** → upskill internally  
        - **Borrow** → external temporary capacity  
        - **Boost** → tech & productivity improvements

    ### 9. 🔍 **Gap Strategy Analysis**
    - Get targeted suggestions based on the selected strategy for each role.

    ### 10. 🎯 **Action Planning**
    - Define, cost, and prioritize initiatives to close your workforce gaps.
    - Track expected impact, feasibility, and alignment to strategy.

    ---
    """)
