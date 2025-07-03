import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def inject_custom_styles():
    st.markdown("""
        <style>
            #MainMenu, footer {visibility: hidden;}
            .stApp {
                font-family: 'Segoe UI', sans-serif;
                background-color: #f9fbfc;
                padding: 2rem;
            }
            h1, h2, h3, h4 { color: #0A5A9C; }
            .stDataFrame, .css-1d391kg {
                background-color: white;
                border-radius: 8px;
                padding: 12px;
            }
        </style>
    """, unsafe_allow_html=True)

def section_header(title: str):
    st.markdown(f"""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>{title}</h3>
        </div>
    """, unsafe_allow_html=True)

def render_scenario_planning():
    inject_custom_styles()
    section_header("📊 Scenario Planning: Workforce Demand vs. Supply")

    if "scenario_planning_forecast" not in st.session_state:
        st.warning("❗ Please complete the Critical Workforce Forecasting step first.")
        return

    df_forecast = st.session_state["scenario_planning_forecast"]

    forecast_years = sorted({
        col.split()[-1] for col in df_forecast.columns if col.startswith("Forecast ")
    })

    st.sidebar.header("⚙️ Scenario Settings")
    growth_scenario = st.sidebar.selectbox(
        "Scenario Growth Assumption",
        ["Baseline (0%)", "Optimistic (+5%)", "Pessimistic (-3%)"]
    )
    growth_rate = 0.05 if "Optimistic" in growth_scenario else -0.03 if "Pessimistic" in growth_scenario else 0.0

    st.subheader("⚖️ Role-Level Supply Planning")

    roles = df_forecast["Role"].unique().tolist()
    rate_inputs = []

    for role in roles:
        col1, col2, col3 = st.columns(3)
        with col1:
            attr = st.number_input(f"{role} - Attrition (%)", 0.0, 50.0, 5.0, 0.5, key=f"{role}_attr")
        with col2:
            retire = st.number_input(f"{role} - Retirement (%)", 0.0, 30.0, 2.0, 0.5, key=f"{role}_retire")
        with col3:
            inflow = st.number_input(f"{role} - Internal Pipeline (FTE/year)", 0.0, 100.0, 5.0, 1.0, key=f"{role}_pipeline")

        rate_inputs.append({
            "Role": role,
            "Attrition Rate": attr / 100,
            "Retirement Rate": retire / 100,
            "Pipeline": inflow
        })

    rate_df = pd.DataFrame(rate_inputs).set_index("Role")

    # === Demand Projection ===
    base_cols = [f"Forecast {y}" for y in forecast_years]
    base_by_role = df_forecast[["Role"] + base_cols].set_index("Role")
    scenario_demand_by_role = base_by_role.copy()
    for i, year in enumerate(forecast_years):
        col = f"Forecast {year}"
        scenario_demand_by_role[col] = base_by_role[col] * ((1 + growth_rate) ** i)

    # === Supply Projection ===
    supply_by_role = base_by_role.copy()
    for i, year in enumerate(forecast_years):
        col = f"Forecast {year}"
        if i == 0:
            supply_by_role[col] = base_by_role[col]
        else:
            prev_year = forecast_years[i - 1]
            prev_col = f"Forecast {prev_year}"
            for role in roles:
                if role not in supply_by_role.index or role not in rate_df.index:
                    continue
                prev_val = supply_by_role.loc[role, prev_col]
                attr = rate_df.loc[role]["Attrition Rate"]
                retire = rate_df.loc[role]["Retirement Rate"]
                inflow = rate_df.loc[role]["Pipeline"]
                updated_val = prev_val * (1 - attr - retire) + inflow
                supply_by_role.loc[role, col] = round(updated_val, 1)

    # === Gap Calculation (Raw Data)
    role_gap = scenario_demand_by_role.copy()
    for year in forecast_years:
        role_gap[f"Gap {year}"] = (
            scenario_demand_by_role[f"Forecast {year}"].astype(float).round(0) -
            supply_by_role[f"Forecast {year}"].astype(float).round(0)
        )

    role_gap["Role"] = role_gap.index
    role_gap.reset_index(drop=True, inplace=True)

    # === Summarize Gap by Unique Role ===
    gap_cols = [f"Gap {y}" for y in forecast_years]
    role_gap_summary = role_gap.groupby("Role")[gap_cols].sum().reset_index()

    st.subheader("📋 Role-Level Gap Forecast")
    st.dataframe(role_gap_summary, use_container_width=True)

    # === Summary View
    result_df = pd.DataFrame({
        "Year": forecast_years,
        "Scenario Demand": scenario_demand_by_role[[f"Forecast {y}" for y in forecast_years]].sum().values,
        "Projected Supply": supply_by_role[[f"Forecast {y}" for y in forecast_years]].sum().values,
        "Workforce Gap": role_gap[[f"Gap {y}" for y in forecast_years]].sum().values
    })

    st.subheader("📈 Summary Forecast (Total)")
    st.dataframe(result_df, use_container_width=True)

    melt_df = result_df.melt(id_vars="Year", var_name="Metric", value_name="Headcount")
    fig = px.line(melt_df, x="Year", y="Headcount", color="Metric", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # === Save to Session for Later Modules ===
    st.session_state["scenario_planning_output"] = result_df
    st.session_state["scenario_plan_role_table"] = role_gap_summary
    st.session_state["scenario_plan_role_detailed"] = role_gap
    st.session_state["scenario_assumptions"] = {
        "growth_rate": growth_rate,
        "attrition_rates": rate_df["Attrition Rate"].to_dict(),
        "retirement_rates": rate_df["Retirement Rate"].to_dict(),
        "internal_pipeline": rate_df["Pipeline"].to_dict()
    }
