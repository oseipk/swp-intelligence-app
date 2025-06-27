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
from datetime import datetime
import plotly.express as px
from modules import ui

def linear_forecast(values, years):
    x = np.array([int(y) for y in years])
    y = np.array(values)
    coef = np.polyfit(x, y, 1)
    future_years = [int(years[-1]) + i for i in range(1, 5)]
    return np.round(coef[0] * np.array(future_years) + coef[1], 2)

def cagr_forecast(values):
    start, end = values[0], values[-1]
    if start <= 0 or end <= 0:
        return [np.nan] * 4
    rate = (end / start) ** (1 / (len(values) - 1)) - 1
    return np.round([end * ((1 + rate) ** i) for i in range(1, 5)], 2)

def render_critical_workforce_forecasting():
    inject_custom_styles()
    section_header("👷 Critical Workforce Forecasting")

    required_keys = [
        "independent_driver_table", "elasticity_table",
        "business_driver_table", "driver_years", "headcount_table", "headcount_years"
    ]
    if not all(k in st.session_state for k in required_keys):
        st.warning("❗ Please complete previous steps before running critical workforce forecasting.")
        return

    df_drivers = st.session_state["business_driver_table"]
    df_indep = st.session_state["independent_driver_table"]
    elasticity_df = st.session_state["elasticity_table"]
    df_headcount = st.session_state["headcount_table"]
    historical_years = st.session_state["driver_years"]
    headcount_years = st.session_state["headcount_years"]
    forecast_years = [str(int(historical_years[-1]) + i) for i in range(1, 5)]

    # === Step 1: Critical Roles ===
    st.subheader("👤 Define Critical Roles")
    roles_input = st.text_area("Enter Critical Roles (comma-separated)", 
                               value=st.session_state.get("critical_roles_raw", ""),
                               placeholder="e.g. Data Scientist, Sales Analyst")
    st.session_state["critical_roles_raw"] = roles_input
    roles = [r.strip() for r in roles_input.split(",") if r.strip()]
    if not roles:
        st.info("⚠️ Please enter at least one critical role.")
        return

    # === Step 2: Map Roles to Function Units
    st.subheader("🏭 Assign Each Role to a Function Unit")
    role_function_map = st.session_state.get("role_function_map", {})
    for role in roles:
        function = st.selectbox(
            f"Function unit for role: **{role}**",
            options=sorted(df_headcount["Function Unit"].unique()),
            index=0 if role not in role_function_map else sorted(df_headcount["Function Unit"].unique()).index(role_function_map[role]),
            key=f"{role}_function"
        )
        role_function_map[role] = function
    st.session_state["role_function_map"] = role_function_map

    # === Step 3: Assign Roles to Drivers and Weights
    st.subheader("🔗 Assign Roles to Drivers (Weights must sum to 100 per driver)")
    driver_role_map = st.session_state.get("critical_driver_role_map", {})

    for driver in df_indep["Driver"].tolist():
        with st.expander(f"🔧 Assign roles to driver: **{driver}**"):
            assigned_roles = st.multiselect(
                f"Select critical roles influenced by **{driver}**",
                options=roles,
                default=driver_role_map.get(driver, {}).keys(),
                key=f"{driver}_roles"
            )
            role_weights = {}
            total_weight = 0
            for role in assigned_roles:
                default_weight = driver_role_map.get(driver, {}).get(role, 0.0)
                wt = st.number_input(
                    f"→ Weight for **{role}** (%) under {driver}",
                    min_value=0.0, max_value=100.0, step=1.0,
                    value=default_weight,
                    key=f"{driver}_{role}_weight"
                )
                role_weights[role] = wt
                total_weight += wt

            if assigned_roles:
                if round(total_weight) != 100:
                    st.warning(f"⚠️ Total weight for {driver} must be 100%. Currently: {total_weight:.1f}%")
                else:
                    driver_role_map[driver] = role_weights
    st.session_state["critical_driver_role_map"] = driver_role_map

    # === Step 4: Forecast Method
    st.subheader("📈 Select Forecasting Method")
    method = st.radio(
        "Forecasting Method:",
        ["Linear Trend", "CAGR"],
        help="Linear = straight-line projection, CAGR = compound annual growth",
        index=0
    )
    st.session_state["critical_forecast_method"] = method

    # === Step 5: Forecasting Logic
    st.markdown("---")
    st.subheader("🔮 Forecasted Critical Workforce")

    results = []
    for driver, role_weights in driver_role_map.items():
        try:
            elasticity = elasticity_df[elasticity_df["Driver"] == driver]["Elasticity"].values[0]
            hist_kpi_vals = pd.to_numeric(
                df_drivers[df_drivers["Business Driver"] == driver][historical_years].iloc[0],
                errors="coerce"
            ).values
            hist_kpi_vals = [v for v in hist_kpi_vals if pd.notna(v)]
            if len(hist_kpi_vals) < 2:
                continue

            base_kpi = np.mean(hist_kpi_vals)

            if method == "Linear Trend":
                forecasted_kpis = linear_forecast(hist_kpi_vals, historical_years)
            else:
                forecasted_kpis = cagr_forecast(hist_kpi_vals)

            for role, weight in role_weights.items():
                func = role_function_map.get(role)
                func_headcount = df_headcount[df_headcount["Function Unit"] == func]
                if func_headcount.empty:
                    continue

                try:
                    base_hc_vals = pd.to_numeric(func_headcount[headcount_years].values[0], errors="coerce")
                    base_hc = np.nanmean(base_hc_vals)
                except Exception:
                    base_hc = 1  # fallback

                weight_ratio = weight / 100.0
                row = {
                    "Role": role,
                    "Function Unit": func,
                    "Driver": driver,
                    "Weight (%)": round(weight, 1),
                    "Elasticity": round(elasticity, 3)
                }

                for i, yr in enumerate(forecast_years):
                    kpi_val = forecasted_kpis[i]
                    growth_factor = (kpi_val - base_kpi) / base_kpi
                    forecasted = base_hc * (1 + elasticity * growth_factor) * weight_ratio
                    row[f"KPI {yr}"] = kpi_val
                    row[f"Workforce {yr}"] = round(forecasted)

                results.append(row)
        except Exception as e:
            st.warning(f"⚠ Error processing {driver}: {e}")
            continue

    df_forecast = pd.DataFrame(results)
    if df_forecast.empty:
        st.info("⚠️ No forecast data generated.")
        return

    st.dataframe(df_forecast, use_container_width=True)
    st.session_state["critical_workforce_forecast"] = df_forecast

    # === Visualization
    st.subheader("📊 Forecasted Workforce by Role")
    try:
        viz_df = df_forecast.melt(
            id_vars=["Role"],
            value_vars=[c for c in df_forecast.columns if c.startswith("Workforce")],
            var_name="Year", value_name="Forecasted Headcount"
        )
        viz_df["Year"] = viz_df["Year"].str.extract(r"(\d{4})")
        fig = px.line(
            viz_df,
            x="Year", y="Forecasted Headcount",
            color="Role", markers=True,
            title="Forecasted Workforce by Role"
        )
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Arial", size=12, color="#333"),
            margin=dict(l=40, r=20, t=50, b=40))

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart rendering failed: {e}")
        
