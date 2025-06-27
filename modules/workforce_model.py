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
from datetime import datetime
import plotly.express as px
from modules import ui

# 🔹 Predefined selectable function units (no default)
FUNCTION_UNIT_LIST = sorted([
    "R&D Team", "Sales", "Marketing", "Finance", "HR", "IT", "Procurement",
    "Supply Chain", "Product Development", "Operations", "Strategy", "Data Analytics",
    "Manufacturing", "Quality Assurance", "Customer Service"
])

def get_function_units():
    """Collect selected and custom function units from user input."""
    selected = st.multiselect(
        "📌 Select Function Units",
        options=FUNCTION_UNIT_LIST
    )

    manual_input = st.text_area("➕ Add Custom Function Units (comma-separated)")
    custom = [x.strip() for x in manual_input.split(",") if x.strip()]
    return sorted(set(selected + custom))

def get_year_columns():
    """Return the past 4 years from current year."""
    current_year = datetime.today().year
    return [str(current_year - i) for i in range(4, 0, -1)]

def render_headcount_input():
    inject_custom_styles()
    section_header("👥 Headcount Entry by Function Unit")
    st.markdown("Define the function units and input headcount values for each of the last 4 years.")

    function_units = get_function_units()
    if not function_units:
        st.info("⚠️ Please add at least one function unit.")
        return

    years = get_year_columns()

    # 🔁 Retrieve or initialize table
    if "headcount_table" in st.session_state:
        df = st.session_state["headcount_table"]
        # Ensure new units are included
        new_units = [f for f in function_units if f not in df["Function Unit"].values]
        for unit in new_units:
            df = pd.concat([df, pd.DataFrame([{**{"Function Unit": unit}, **{y: "" for y in years}}])], ignore_index=True)
    else:
        df = pd.DataFrame([
            {"Function Unit": unit, **{y: "" for y in years}} for unit in function_units
        ])

    st.markdown("### ✏️ Input Headcount Data")
    df_edit = st.data_editor(
        df,
        column_config={"Function Unit": st.column_config.TextColumn(required=True)},
        use_container_width=True,
        num_rows="dynamic",
        key="headcount_matrix_editor"
    )

    # ✅ Save to session
    if df_edit is not None and not df_edit.empty:
     st.session_state["headcount_table"] = df_edit
    st.session_state["headcount_years"] = years


    # 📊 Visualize as bar chart
    st.markdown("### 📉 Headcount Visualization")
    try:
        df_viz = df_edit.melt(id_vars="Function Unit", var_name="Year", value_name="Headcount")
        df_viz["Headcount"] = pd.to_numeric(df_viz["Headcount"], errors="coerce")
        df_viz = df_viz.dropna(subset=["Headcount"])

        if not df_viz.empty:
            fig = px.bar(
                df_viz,
                x="Year",
                y="Headcount",
                color="Function Unit",
                barmode="group",
                title="Headcount by Function Unit Across Years",
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Please enter headcount values to display chart.")
    except Exception as e:
        st.error(f"Chart rendering failed: {e}")
