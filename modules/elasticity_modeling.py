import streamlit as st
import pandas as pd
import numpy as np

def render_elasticity_modeling():
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

    st.markdown("""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>Elasticity Modeling:Using Low Intercorrelation Drivers with High Headcount Functions</h3>
        </div>
    """, unsafe_allow_html=True)

    if "clean_driver_data" not in st.session_state or not st.session_state["clean_driver_data"]:
        st.warning("❗ No driver data available. Please run the correlation module first.")
        return

    clean_drivers = st.session_state["clean_driver_data"]
    st.subheader(" Elasticity Estimates Using Simplified Linear Model")

    elasticity_results = []

    for item in clean_drivers:
        driver = item["Driver"]
        funcs = item["Function_Units"]

        try:
            x_vals = pd.Series(item["Driver_Values"])
            y_vals = pd.Series(item["Headcount_Values"])
            x_vals, y_vals = x_vals.align(y_vals, join="inner")

            # Remove pairs where driver is zero or headcount is zero
            valid_mask = (x_vals != 0) & (y_vals != 0) & x_vals.notna() & y_vals.notna()
            x_clean = x_vals[valid_mask]
            y_clean = y_vals[valid_mask]

            if len(x_clean) < 2:
                st.warning(f"⚠️ Skipped driver '{driver}' – not enough valid (non-zero) data points.")
                continue

            # Calculate slope (ΔY / ΔX using linear regression)
            x_mean = x_clean.mean()
            y_mean = y_clean.mean()
            cov = np.mean((x_clean - x_mean) * (y_clean - y_mean))
            var_x = np.mean((x_clean - x_mean) ** 2)
            slope = cov / var_x

            # Simplified elasticity formula
            elasticity = slope * (x_mean / y_mean)

            elasticity_results.append({
                "Driver": driver,
                "Function Units": ", ".join(funcs),
                "Elasticity": round(elasticity, 3),
                "Mean Driver": round(x_mean, 2),
                "Mean Headcount": round(y_mean, 2),
                "Data Points Used": len(x_clean)
            })

        except Exception as e:
            st.error(f" Elasticity calc failed for driver '{driver}': {e}")
            continue

    if not elasticity_results:
        st.warning(" No valid elasticity values could be estimated.")
        return

    df_results = pd.DataFrame(elasticity_results)
    st.dataframe(df_results, use_container_width=True)
    st.session_state["elasticity_table"] = df_results

    st.subheader("💥 Most Impactful Driver per Function Unit")

    func_impacts = {}
    for row in elasticity_results:
        for func in row["Function Units"].split(", "):
            if func not in func_impacts or abs(row["Elasticity"]) > abs(func_impacts[func]["Elasticity"]):
                func_impacts[func] = {
                    "Driver": row["Driver"],
                    "Elasticity": row["Elasticity"]
                }

    df_impact = pd.DataFrame([
        {
            "Function Unit": func,
            "Most Impactful Driver": data["Driver"],
            "Elasticity": data["Elasticity"]
        }
        for func, data in func_impacts.items()
    ])
    st.dataframe(df_impact, use_container_width=True)
    st.session_state["function_impact_mapping"] = df_impact

    st.subheader("🗣️ Business Planning Insights")
    narratives = []
    for _, row in df_impact.iterrows():
        func = row["Function Unit"]
        driver = row["Most Impactful Driver"]
        elasticity = row["Elasticity"]
        impact = round(elasticity * 100)
        direction = "increase" if elasticity > 0 else "decrease"
        narratives.append(
            f" A 1% increase in **{driver}** has an impact of **{abs(impact)}%** {direction} on **{func}** function unit."
)

    for n in narratives:
        st.markdown(n)

    st.session_state["insight_narratives"] = narratives

