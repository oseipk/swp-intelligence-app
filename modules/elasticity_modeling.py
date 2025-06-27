import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import statsmodels.api as sm

def render_elasticity_modeling():
    # === Styles ===
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

    # === Section Header ===
    st.markdown("""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>📐 Elasticity Modeling: Independent Drivers vs Headcount</h3>
        </div>
    """, unsafe_allow_html=True)

    # === Session Validation ===
    required_keys = [
        "independent_driver_table",
        "business_driver_table",
        "headcount_table",
        "headcount_years",
        "driver_function_mapping"
    ]
    missing_keys = [k for k in required_keys if k not in st.session_state]
    if missing_keys:
        st.warning(f"Missing required session data: {', '.join(missing_keys)}")
        st.stop()

    # === Load Session Data ===
    df_indep = st.session_state["independent_driver_table"]
    df_drivers = st.session_state["business_driver_table"]
    df_headcount = st.session_state["headcount_table"]
    years = st.session_state["headcount_years"]
    mapping = st.session_state["driver_function_mapping"]

    results = []
    skipped = []
    model_options = {}
    final_selected_models = {}

    # === Modeling ===
    for _, row in df_indep.iterrows():
        driver = row["Driver"]
        functions = mapping.get(driver, [])

        try:
            driver_vals = df_drivers[df_drivers["Business Driver"] == driver][years].iloc[0]
            driver_vals = pd.to_numeric(driver_vals, errors="coerce")
        except:
            skipped.append({"Driver": driver, "Reason": "Missing or invalid driver KPI values"})
            continue

        hc_subset = df_headcount[df_headcount["Function Unit"].isin(functions)]
        headcount_vals = hc_subset[years].apply(pd.to_numeric, errors="coerce").sum()

        valid_years = [y for y in years if pd.notna(driver_vals[y]) and pd.notna(headcount_vals[y])]
        if len(valid_years) < 2:
            skipped.append({"Driver": driver, "Reason": "Fewer than 2 valid years of data"})
            continue

        x = driver_vals[valid_years]
        y = headcount_vals[valid_years]

        if x.nunique() < 2 or y.nunique() < 2:
            skipped.append({"Driver": driver, "Reason": "No variation in data (constant values)"})
            continue

        try:
            # Linear
            X_lin = sm.add_constant(x)
            model_lin = sm.OLS(y, X_lin).fit()
            r2_lin = model_lin.rsquared
            p_lin = model_lin.pvalues[1]
            slope_lin = model_lin.params[1]
            elasticity_lin = slope_lin * (x.mean() / y.mean())

            # Log–Log
            x_log = np.log(x)
            y_log = np.log(y)
            X_log = sm.add_constant(x_log)
            model_log = sm.OLS(y_log, X_log).fit()
            r2_log = model_log.rsquared
            p_log = model_log.pvalues[1]
            slope_log = model_log.params[1]

            # Recommendation
            recommended_model = "Log–Log" if (r2_log > r2_lin and p_log < 0.05) else "Linear"
            model_options[driver] = {
                "log": {"model": model_log, "r2": r2_log, "p": p_log, "elasticity": slope_log},
                "lin": {"model": model_lin, "r2": r2_lin, "p": p_lin, "elasticity": elasticity_lin},
                "rec": recommended_model
            }

            elasticity = slope_log if recommended_model == "Log–Log" else elasticity_lin
            r2 = r2_log if recommended_model == "Log–Log" else r2_lin
            p_val = p_log if recommended_model == "Log–Log" else p_lin

            results.append({
                "Driver": driver,
                "Recommended Model": recommended_model,
                "Elasticity": round(elasticity, 3),
                "R²": round(r2, 3),
                "p-value": round(p_val, 4),
                "Significant": "✅ Yes" if p_val < 0.05 else "⚠️ No"
            })

        except Exception as e:
            skipped.append({"Driver": driver, "Reason": f"Regression error: {e}"})
            continue

    # === Display Results ===
    if results:
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)

        st.markdown("### 📊 Explanation Table")
        st.markdown("""
        | Criteria | Description |
        |----------|-------------|
        | R² | Goodness of fit – higher is better |
        | p-value | Statistical significance (< 0.05 is good) |
        | Elasticity | % impact on headcount per 1% change in driver |
        """)

        st.markdown("### 🔧 Manual Override of Recommended Models")

        for i, row in df_results.iterrows():
            driver = row["Driver"]
            recommended = row["Recommended Model"]
            override = st.radio(
                f"Select model for **{driver}**", ["Log–Log", "Linear"],
                index=["Log–Log", "Linear"].index(recommended),
                key=f"{driver}_model"
            )
            model_obj = model_options[driver]["log"] if override == "Log–Log" else model_options[driver]["lin"]
            final_selected_models[driver] = {
                "Model": override,
                "Elasticity": round(model_obj["elasticity"], 3),
                "R²": round(model_obj["r2"], 3),
                "p-value": round(model_obj["p"], 4)
            }

        st.session_state["elasticity_table"] = df_results
        st.session_state["selected_elasticity"] = final_selected_models

    else:
        st.info("ℹ️ No valid elasticity models could be computed.")

    # === Skipped Drivers Diagnostics ===
    if skipped:
        st.subheader("⚠️ Skipped Drivers (Diagnostics)")
        df_skipped = pd.DataFrame(skipped)
        st.dataframe(df_skipped, use_container_width=True)
