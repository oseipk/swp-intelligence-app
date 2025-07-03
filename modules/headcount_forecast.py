import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def linear_forecast(values, years):
    x = np.array([int(y) for y in years])
    y = np.array(values)
    coef = np.polyfit(x, y, 1)
    future_years = [int(years[-1]) + i for i in range(1, 5)]
    return np.round(coef[0] * np.array(future_years) + coef[1], 2)

def render_critical_workforce_forecasting():
    st.markdown("## 👷 Critical Workforce Forecasting")

    required_keys = ["clean_driver_data", "elasticity_table", "headcount_table", "headcount_years"]
    if not all(k in st.session_state for k in required_keys):
        st.warning("❗ Required data not found. Please run previous modules first.")
        return

    clean_drivers = st.session_state["clean_driver_data"]
    elasticity_df = st.session_state["elasticity_table"]
    df_headcount = st.session_state["headcount_table"]
    headcount_years = st.session_state["headcount_years"]
    forecast_years = [str(int(headcount_years[-1]) + i) for i in range(1, 5)]

    # === Step 1: Define Critical Roles
    st.subheader("🧑‍💼 Define Critical Roles")
    roles_input = st.text_area(
        "Enter critical roles (comma-separated)",
        value=st.session_state.get("critical_roles_raw", ""),
        key="roles_input"
    )
    roles = [r.strip() for r in roles_input.split(",") if r.strip()]
    st.session_state["critical_roles_raw"] = roles_input

    if not roles:
        st.info("Please input at least one critical role.")
        return

    # === Step 2: Map Roles to Function Units
    st.subheader("🏭 Role to Function Unit Assignment")
    all_funcs = df_headcount["Function Unit"].unique().tolist()

    if "role_func_map" not in st.session_state:
        st.session_state["role_func_map"] = {}
    role_func_map = st.session_state["role_func_map"]

    for role in roles:
        default = role_func_map.get(role, all_funcs[0])
        func = st.selectbox(
            f"Select function unit for **{role}**",
            all_funcs,
            key=f"{role}_func",
            index=all_funcs.index(default) if default in all_funcs else 0
        )
        role_func_map[role] = func

    # === Step 3: Assign Roles to Drivers with Weights
    st.subheader("Assign Roles to Drivers and Weights")

    if "driver_role_weights" not in st.session_state:
        st.session_state["driver_role_weights"] = {}
    driver_role_weights = st.session_state["driver_role_weights"]

    for item in clean_drivers:
        driver = item["Driver"]
        default_roles = [role for role in roles if role_func_map[role] in item["Function_Units"]]
        with st.expander(f"🎛️ Role Weighting for Driver: {driver}"):
            selected_roles = st.multiselect(
                f"Roles influenced by **{driver}**",
                roles,
                default=driver_role_weights.get(driver, {}).keys(),
                key=f"{driver}_roles"
            )
            weights = {}
            total = 0
            for role in selected_roles:
                default_weight = driver_role_weights.get(driver, {}).get(role, 0.0)
                wt = st.number_input(
                    f"→ Weight for {role} under {driver}",
                    0.0, 100.0, default_weight, 1.0,
                    key=f"{driver}_{role}_wt"
                )
                weights[role] = wt
                total += wt
            driver_role_weights[driver] = weights
            if round(total) != 100:
                st.error(f"❌ Total weight for {driver} = {total:.1f}%. Must equal 100%.")
                st.session_state[f"{driver}_weight_error"] = True
            else:
                st.session_state[f"{driver}_weight_error"] = False

    if any(st.session_state.get(f"{item['Driver']}_weight_error", False) for item in clean_drivers):
        st.warning("❗ Fix weighting errors above before running the forecast.")
        return

    # === Step 4: Forecast Logic
    st.subheader("📈 Forecasted Critical Role Headcount")
    st.markdown("""
    <div style="background-color:#e8f1fa;padding:12px;border-radius:6px;margin-bottom:10px;">
        📌 <strong>Note:</strong> Since role-level historical headcount data isn't available,
        this forecast estimates headcount <em>demand</em> based on:
        function-level headcount × role weight × elasticity impact from driver growth.
        These represent projected workforce needs rather than historic actuals.
    </div>
    """, unsafe_allow_html=True)

    results = []

    for item in clean_drivers:
        driver = item["Driver"]
        if driver not in driver_role_weights:
            continue

        try:
            elasticity = elasticity_df[elasticity_df["Driver"] == driver]["Elasticity"].values[0]
        except:
            continue

        driver_vals = pd.Series(item["Driver_Values"])
        valid_years = driver_vals.index.tolist()
        forecasted_kpis = linear_forecast(driver_vals.values, valid_years)
        base_kpi = np.mean(driver_vals.values)

        for role, wt in driver_role_weights[driver].items():
            func = role_func_map[role]
            func_df = df_headcount[df_headcount["Function Unit"] == func]
            if func_df.empty or func_df.shape[0] > 1:
                continue  

            base_hc_vals = pd.to_numeric(func_df[headcount_years].iloc[0], errors="coerce")
            base_hc = np.nanmean(base_hc_vals)
            if base_hc <= 0 or np.isnan(base_hc):
                continue

            row = {
                "Role": role,
                "Function Unit": func,
                "Driver": driver,
                "Elasticity": round(elasticity, 3),
                "Weight (%)": wt
            }

            for i, yr in enumerate(forecast_years):
                kpi_val = forecasted_kpis[i]
                growth = (kpi_val - base_kpi) / base_kpi
                forecasted = base_hc * (1 + elasticity * growth) * (wt / 100.0)
                row[f"KPI {yr}"] = round(kpi_val, 2)
                row[f"Forecast {yr}"] = round(forecasted)

            results.append(row)

    df_results = pd.DataFrame(results)
    if df_results.empty:
        st.info("No forecast generated. Check inputs.")
        return

    st.dataframe(df_results, use_container_width=True)
    st.session_state["critical_role_forecast"] = df_results
    st.session_state["scenario_planning_forecast"] = df_results  # ⬅️ Save for scenario planning module

    # === Step 5: Sum Forecast by Function Unit
    st.subheader("📊 Summarized Forecast by Function Unit")
    forecast_cols = [f"Forecast {yr}" for yr in forecast_years]
    summary = df_results[["Function Unit"] + forecast_cols]
    func_summary = summary.groupby("Function Unit")[forecast_cols].sum().reset_index()
    st.dataframe(func_summary, use_container_width=True)

    # === Optional: Visualization
    st.subheader("📉 Forecasted Headcount by Role")
    try:
        chart_df = df_results.melt(
            id_vars=["Role"],
            value_vars=forecast_cols,
            var_name="Year", value_name="Forecasted Headcount"
        )
        chart_df["Year"] = chart_df["Year"].str.extract(r"(\d{4})")
        fig = px.line(chart_df, x="Year", y="Forecasted Headcount", color="Role", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart rendering failed: {e}")
