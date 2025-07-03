import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Inject custom CSS styles
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
            .stSlider { margin-bottom: 20px; }
            .stRadio > div { gap: 10px; }
        </style>
    """, unsafe_allow_html=True)

# Render section header
def section_header(title: str):
    st.markdown(f"""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>{title}</h3>
        </div>
    """, unsafe_allow_html=True)

# Predefined selectable function units
FUNCTION_UNIT_LIST = sorted([
    "R&D Team", "Sales", "Marketing", "Finance", "HR", "IT", "Procurement",
    "Supply Chain", "Product Development", "Operations", "Strategy", "Data Analytics",
    "Manufacturing", "Quality Assurance", "Customer Service"
])

# Return the past 4 years
def get_year_columns():
    current_year = datetime.today().year
    return [str(current_year - i) for i in range(4, 0, -1)]

# Headcount UI logic
def render_headcount_input():
    inject_custom_styles()
    section_header("👥 Headcount Entry by Function Unit")
    st.markdown("Define the function units and input headcount values for each of the last 4 years.")

    # Reset input
    if st.button("🔄 Reset Function Unit Input"):
        st.session_state.pop("function_units", None)
        st.session_state.pop("headcount_table", None)

    # Collect function unit input only once
    if "function_units" not in st.session_state:
        selected = st.multiselect("📌 Select Function Units", options=FUNCTION_UNIT_LIST)
        manual_input = st.text_area("➕ Add Custom Function Units (comma-separated)")
        custom = [x.strip() for x in manual_input.split(",") if x.strip()]
        all_units = sorted(set(selected + custom))

        if st.button("✅ Confirm Selection"):
            if not all_units:
                st.warning("⚠️ Please add at least one function unit.")
                return
            st.session_state["function_units"] = all_units
            st.rerun()
        else:
            return

    function_units = st.session_state["function_units"]
    years = get_year_columns()

    # Build base editable table
    if "headcount_table" in st.session_state:
        df = st.session_state["headcount_table"]
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

    # ✅ Only save when user clicks the save button
    if st.button("💾 Save Headcount Data"):
        st.session_state["headcount_table"] = df_edit
        st.session_state["headcount_years"] = years
        st.success("✅ Headcount data saved successfully!")

    # ✅ Visualization from saved data
    st.markdown("### 📉 Headcount Visualization")
    if "headcount_table" in st.session_state:
        try:
            df_viz = st.session_state["headcount_table"].melt(
                id_vars="Function Unit", var_name="Year", value_name="Headcount"
            )
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
                st.info("ℹ️ Please enter and save headcount values to display chart.")
        except Exception as e:
            st.error(f"Chart rendering failed: {e}")


