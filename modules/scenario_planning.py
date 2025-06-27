import streamlit as st
from textwrap import dedent

def inject_custom_styles():
    st.markdown("""
        <style>
            /* Hide Streamlit branding */
            #MainMenu, footer {visibility: hidden;}

            /* App layout */
            .stApp {
                font-family: 'Segoe UI', sans-serif;
                background-color: #f9fbfc;
                padding: 2rem;
            }

            /* Section headers */
            h1, h2, h3, h4 {
                color: #0A5A9C;
            }

            .stDataFrame, .css-1d391kg {
                background-color: white;
                border-radius: 8px;
                padding: 12px;
            }

            .stSlider {
                margin-bottom: 20px;
            }

            .stRadio > div {
                gap: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

def section_header(title: str):
    st.markdown(f"""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>{title}</h3>
        </div>
    """, unsafe_allow_html=True)


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from modules import ui

def render_scenario_planning():
    inject_custom_styles()
    section_header("📊 Scenario Planning: Workforce Demand vs. Supply")

    if "critical_workforce_forecast" not in st.session_state:
        st.warning("❗ Please complete the Critical Workforce Forecasting step first.")
        return

    df_forecast = st.session_state["critical_workforce_forecast"]

    # Forecast years
    forecast_years = sorted({
        col.split()[-1] for col in df_forecast.columns if col.startswith("Workforce ")
    })

    st.sidebar.header("⚙️ Scenario Settings")
    growth_scenario = st.sidebar.selectbox(
        "Scenario Growth Assumption",
        ["Baseline (0%)", "Optimistic (+5%)", "Pessimistic (-3%)"]
    )

    internal_pipeline = st.sidebar.number_input(
        "Internal Hiring Pipeline (FTE/year)", min_value=0, value=50, step=10
    )

    # Growth multiplier
    growth_rate = 0.05 if "Optimistic" in growth_scenario else -0.03 if "Pessimistic" in growth_scenario else 0.0

    # Attrition & Retirement inputs
    st.subheader("⚖️ Role-Specific Attrition & Retirement Rates")

    roles = df_forecast["Role"].unique().tolist()
    rate_inputs = []
    for role in roles:
        col1, col2 = st.columns(2)
        with col1:
            attr = st.number_input(f"{role} - Attrition Rate (%)", min_value=0.0, max_value=50.0,
                                   value=5.0, step=0.5, key=f"{role}_attr")
        with col2:
            retire = st.number_input(f"{role} - Retirement Rate (%)", min_value=0.0, max_value=30.0,
                                     value=2.0, step=0.5, key=f"{role}_retire")
        rate_inputs.append({
            "Role": role,
            "Attrition Rate": attr / 100,
            "Retirement Rate": retire / 100
        })

    rate_df = pd.DataFrame(rate_inputs).set_index("Role")

    # Base demand per role/year
    base_cols = [f"Workforce {y}" for y in forecast_years]
    base_by_role = df_forecast[["Role"] + base_cols].set_index("Role")

    # Scenario demand per role/year
    scenario_demand_by_role = base_by_role.copy()
    for idx, year in enumerate(forecast_years):
        col = f"Workforce {year}"
        scenario_demand_by_role[col] = base_by_role[col] * ((1 + growth_rate) ** idx)

    # Supply projection per role
    supply_by_role = base_by_role.copy()
    for i, year in enumerate(forecast_years):
        col = f"Workforce {year}"
        if i == 0:
            supply_by_role[col] = base_by_role[col]
        else:
            prev_year = forecast_years[i - 1]
            prev_col = f"Workforce {prev_year}"
            updated = []
            for role in roles:
                prev_val = supply_by_role.loc[role, prev_col]
                attr = rate_df.loc[role]["Attrition Rate"]
                retire = rate_df.loc[role]["Retirement Rate"]
                inflow = internal_pipeline / len(roles)
                updated_val = prev_val * (1 - attr - retire) + inflow
                updated.append(round(updated_val, 1))
            supply_by_role[col] = updated

    # Aggregate totals
    base_demand_total = base_by_role.sum()
    scenario_demand_total = scenario_demand_by_role.sum()
    supply_total = supply_by_role.sum()

    result_df = pd.DataFrame({
        "Year": forecast_years,
        "Base Demand": base_demand_total.values,
        "Scenario Demand": scenario_demand_total.values,
        "Projected Supply": supply_total.values
    })

    st.subheader("📋 Forecasted Workforce Summary")
    st.dataframe(result_df, use_container_width=True)

    # Line chart
    st.subheader("📊 Scenario Demand vs. Supply Over Time")
    melt_df = result_df.melt(id_vars="Year", var_name="Metric", value_name="Headcount")
    fig = px.line(melt_df, x="Year", y="Headcount", color="Metric", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # Save to session
    st.session_state["scenario_planning_output"] = result_df
    st.session_state["scenario_plan_role_table"] = supply_by_role  # optional, for downstream gap analysis
    st.session_state["scenario_assumptions"] = {
        "growth_rate": growth_rate,
        "attrition_rates": rate_df["Attrition Rate"].to_dict(),
        "retirement_rates": rate_df["Retirement Rate"].to_dict(),
        "internal_pipeline": internal_pipeline
    }
