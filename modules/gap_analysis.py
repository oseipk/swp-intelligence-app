import streamlit as st
import pandas as pd
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
            h1, h2, h3, h4 {
                color: #0A5A9C;
            }
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

def render_gap_analysis():
    inject_custom_styles()
    section_header("📉 Future Workforce Gap Analysis")

    if "scenario_plan_role_table" not in st.session_state or \
       "scenario_planning_forecast" not in st.session_state or \
       "scenario_assumptions" not in st.session_state:
        st.warning("❗ Please complete the Scenario Planning step first.")
        return

    supply_df = st.session_state["scenario_plan_role_table"].copy().set_index("Role")
    demand_df = st.session_state["scenario_planning_forecast"].copy()
    assumptions = st.session_state["scenario_assumptions"]
    attrition_rates = assumptions.get("attrition_rates", {})
    retirement_rates = assumptions.get("retirement_rates", {})
    internal_pipeline = assumptions.get("internal_pipeline", {})

    forecast_years = sorted({
        col.split()[-1] for col in demand_df.columns if col.startswith("Forecast ")
    })

    roles = demand_df["Role"].unique()
    rows = []

    for role in roles:
        for year in forecast_years:
            demand_col = f"Forecast {year}"
            gap_col = f"Gap {year}"

            scenario_demand_series = demand_df[demand_df["Role"] == role][demand_col]
            scenario_demand = scenario_demand_series.sum() if not scenario_demand_series.empty else 0

            if year == forecast_years[0]:
                projected_supply = supply_df.at[role, gap_col] + scenario_demand if (role in supply_df.index and gap_col in supply_df.columns) else 0
            else:
                prev_year = forecast_years[forecast_years.index(year) - 1]
                prev_supply = rows[-1]["Projected Supply"]
                attr = attrition_rates.get(role, 0)
                retire = retirement_rates.get(role, 0)
                inflow = internal_pipeline.get(role, 0)
                projected_supply = prev_supply * (1 - attr - retire) + inflow

            gap = (scenario_demand) - (projected_supply)
            gap_pct = (gap / scenario_demand * 100) if scenario_demand else 0
            status = "Shortfall" if gap > 0 else "Surplus" if gap < 0 else "Balanced"

            rows.append({
                "Critical Role": role,
                "Year": year,
                "Scenario Demand": round(scenario_demand, 1),
                "Projected Supply": round(projected_supply, 1),
                "Gap": round(gap, 1),
                "Gap %": round(gap_pct, 1),
                "Status": status
            })

    df_gap = pd.DataFrame(rows)

    st.subheader("🎯 Filter by Role")
    selected_roles = st.multiselect("Select Critical Role(s)", sorted(roles), default=sorted(roles))
    filtered_df = df_gap[df_gap["Critical Role"].isin(selected_roles)]

    st.subheader("📋 Role-Level Gap Analysis Table")
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("📊 Demand vs Supply vs Gap (Total)")
    df_summary = filtered_df.groupby("Year")[["Scenario Demand", "Projected Supply", "Gap"]].sum().reset_index()
    df_melt = df_summary.melt(id_vars="Year", var_name="Metric", value_name="Headcount")

    fig = px.line(df_melt, x="Year", y="Headcount", color="Metric", markers=True)
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", size=12, color="#333"),
        margin=dict(l=40, r=20, t=50, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.session_state["workforce_role_gap_table"] = df_gap
