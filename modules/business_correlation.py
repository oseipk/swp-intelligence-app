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
from scipy.stats import pearsonr, spearmanr
import plotly.express as px
from modules import ui

def render_driver_headcount_correlation():
    inject_custom_styles()
    section_header("📈 Demand Driver ↔ Headcount Correlation Analysis")

    # Check prerequisites
    if "business_driver_table" not in st.session_state or "headcount_table" not in st.session_state:
        st.warning("❗ Please complete the driver and headcount input steps first.")
        return

    df_drivers = st.session_state["business_driver_table"]
    df_headcount = st.session_state["headcount_table"]
    headcount_years = st.session_state["headcount_years"]

    # Manual Mapping UI
    st.subheader("🔗 Map Demand Drivers to Function Units")
    unique_drivers = df_drivers["Business Driver"].tolist()
    unique_functions = df_headcount["Function Unit"].unique().tolist()

    # Load previous mapping or initialize
    if "driver_function_mapping" not in st.session_state:
        st.session_state["driver_function_mapping"] = {}

    updated_mapping = {}
    for driver in unique_drivers:
        default = st.session_state["driver_function_mapping"].get(
            driver,
            [f for f in unique_functions if driver.lower() in f.lower()]
        )
        updated_mapping[driver] = st.multiselect(
            f"Function Units for Driver: **{driver}**",
            options=unique_functions,
            default=default,
            key=f"mapping_{driver}"
        )

    st.session_state["driver_function_mapping"] = updated_mapping
    mapping = updated_mapping

    if not any(mapping.values()):
        st.warning("⚠️ Please map at least one function unit to each demand driver.")
        return

    # Correlation with Headcount
    st.subheader("📊 Correlation with Headcount")
    result_rows = []
    driver_vectors = {}

    for driver, funcs in mapping.items():
        if not funcs:
            continue

        try:
            driver_row = df_drivers[df_drivers["Business Driver"] == driver][headcount_years].iloc[0]
            driver_values = pd.to_numeric(driver_row, errors="coerce")
        except Exception:
            continue

        subset = df_headcount[df_headcount["Function Unit"].isin(funcs)]
        headcount_values = subset[headcount_years].apply(pd.to_numeric, errors="coerce").sum()

        valid_years = [y for y in headcount_years if pd.notna(driver_values[y]) and pd.notna(headcount_values[y])]
        if len(valid_years) < 2:
            continue

        x = driver_values[valid_years].values
        y = headcount_values[valid_years].values

        try:
            corr, pval = pearsonr(x, y)
            method = "Pearson"
            if pval >= 0.05:
                corr, pval = spearmanr(x, y)
                method = "Spearman"

            result_rows.append({
                "Driver": driver,
                "Function Units": ", ".join(funcs),
                "Method": method,
                "Correlation": round(corr, 3),
                "p-value": round(pval, 4),
                "Significant": "✅ Yes" if pval < 0.05 else "⚠️ No"
            })

            driver_vectors[driver] = x

        except Exception:
            continue

    df_result = pd.DataFrame(result_rows)
    st.dataframe(df_result)
    st.session_state["driver_headcount_correlation"] = df_result

    # Intercorrelation Matrix
    st.subheader("🔀 Intercorrelation Between Drivers")
    st.markdown("### Correlation Coefficients from 0.7 are considered high")
    df_matrix = pd.DataFrame(driver_vectors).T
    inter_corr = df_matrix.T.corr(method="pearson").round(2)
    st.plotly_chart(px.imshow(inter_corr, text_auto=True, title="Driver Intercorrelation Matrix"))

    # Store intercorrelation matrix
    st.session_state["driver_intercorrelation_matrix"] = inter_corr

    # Identify Independent Drivers (not strongly correlated with others)
    threshold = 0.7
    independent_drivers = []
    for driver in inter_corr.index:
        other_corrs = inter_corr.loc[driver].drop(index=driver).abs()
        if all(other_corrs < threshold):
            independent_drivers.append(driver)

    df_indep = df_result[df_result["Driver"].isin(independent_drivers)]
    st.subheader("🧩 Independent Drivers Highly Correlated with Headcount")
    if df_indep.empty:
        st.info("No independent drivers found with strong correlation to headcount.")
    else:
        st.dataframe(df_indep)

    # Save to session
    st.session_state["independent_driver_table"] = df_indep
    st.session_state["independent_driver_correlation"] = df_indep  
    st.session_state["driver_function_mapping"] = mapping   
     
     
