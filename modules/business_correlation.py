import streamlit as st
import pandas as pd
from scipy.stats import pearsonr
import plotly.express as px

def render_driver_headcount_correlation():
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
            <h3 style='color:#0A5A9C;margin:0;'>📈 Driver ↔ Headcount Correlation & Intercorrelation Filtering</h3>
        </div>
    """, unsafe_allow_html=True)

    if "business_driver_table" not in st.session_state or "headcount_table" not in st.session_state:
        st.warning("❗ Please complete the driver and headcount input steps first.")
        return

    df_drivers = st.session_state["business_driver_table"]
    df_headcount = st.session_state["headcount_table"]
    headcount_years = st.session_state["headcount_years"]
    unique_drivers = df_drivers["Business Driver"].tolist()
    unique_functions = df_headcount["Function Unit"].unique().tolist()

    st.subheader("🔗 Map Demand Drivers to Function Units")
    if "driver_function_mapping" not in st.session_state:
        st.session_state["driver_function_mapping"] = {}

    updated_mapping = {}
    for driver in unique_drivers:
        default = st.session_state["driver_function_mapping"].get(
            driver, [f for f in unique_functions if driver.lower() in f.lower()]
        )
        updated_mapping[driver] = st.multiselect(
            f"Function Units for Driver: **{driver}**",
            options=unique_functions,
            default=default,
            key=f"mapping_{driver}"
        )
    st.session_state["driver_function_mapping"] = updated_mapping

    st.subheader("📊 Correlation Summary with Headcount ")
    driver_vectors = {}
    driver_headcounts = {}
    driver_mappings = {}
    correlation_summary = []

    for driver, funcs in updated_mapping.items():
        if not funcs:
            continue

        try:
            driver_vals = pd.to_numeric(
                df_drivers[df_drivers["Business Driver"] == driver][headcount_years].iloc[0], errors="coerce"
            )
        except:
            continue

        hc_vals = df_headcount[df_headcount["Function Unit"].isin(funcs)][headcount_years]
        hc_sum = pd.to_numeric(hc_vals.apply(pd.to_numeric, errors="coerce").sum(), errors="coerce")

        # Remove zero or NaN years from both
        valid_years = [y for y in headcount_years
                       if pd.notna(driver_vals[y]) and pd.notna(hc_sum[y]) and driver_vals[y] != 0]

        if len(valid_years) < 2:
            continue

        x = driver_vals[valid_years]
        y = hc_sum[valid_years]

        try:
            r, p = pearsonr(x, y)
            # if abs(r) >= 0.5:  # High correlation threshold
            correlation_summary.append({
                    "Driver": driver,
                    "Function Units": ", ".join(funcs),
                    "Correlation": round(r, 3),
                    "p-value": round(p, 4),
                    "Significant": "✅ Yes" if p < 0.05 else "⚠️ No"
                })
            driver_vectors[driver] = x
            driver_headcounts[driver] = y
            driver_mappings[driver] = funcs
        except:
            continue

    df_corr = pd.DataFrame(correlation_summary)
    st.dataframe(df_corr)

    if not driver_vectors:
        st.warning("No valid drivers with strong correlation to headcount.")
        return

    st.subheader("🧭 Intercorrelation Matrix (Drivers Only)")
    df_driver_matrix = pd.DataFrame(driver_vectors).T
    corr_matrix = df_driver_matrix.T.corr(method="pearson").round(2)
    st.plotly_chart(
        px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu", zmin=-1, zmax=1,
                  title="Driver Intercorrelation Matrix, Threshold < 0.5"),
        use_container_width=True
    )

    st.subheader("✅ Filter Drivers with Intercorrelation < 0.5")
    threshold = 0.5
    corr_abs = corr_matrix.abs()
    clean_drivers = [
        d for d in corr_abs.columns if all(corr_abs[d].drop(d) < threshold)
    ]

    if not clean_drivers:
        st.warning("No drivers meet the intercorrelation threshold (< 0.5).")
        return

    st.success(f"{len(clean_drivers)} driver(s) passed the intercorrelation filter.")
    st.write("Drivers:", clean_drivers)

    # Save clean drivers and their aligned vectors for use in the next module
    clean_driver_data = []
    for d in clean_drivers:
        clean_driver_data.append({
            "Driver": d,
            "Driver_Values": driver_vectors[d],
            "Headcount_Values": driver_headcounts[d],
            "Function_Units": driver_mappings[d]
        })

    st.session_state["clean_driver_data"] = clean_driver_data
