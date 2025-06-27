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
from modules import ui

def get_recent_years(n=4):
    current_year = datetime.today().year
    return [str(current_year - i - 1) for i in reversed(range(n))]

def render_driver_definition():
    inject_custom_styles()
    section_header("📌 Business Demand Drivers")

    # Predefined drivers (no file upload)
    predefined_drivers = ["e-Intensity (%)", "e-NNS", "E-Commerce growth","Marketing spend in Digital media (%)","Finished Good Inventory (# of days)","Organic Growth(%)","Customer Order Fulfillment(%)","On-Time In Full(%)"]

    st.markdown("### Select or Add Demand Drivers")
    selected = st.multiselect(
        "Select from pre-defined drivers",
        options=predefined_drivers,
        default=st.session_state.get("selected_driver_list", predefined_drivers),
        key="driver_multiselect"
    )
    st.session_state["selected_driver_list"] = selected

    st.markdown("### ➕ Add Custom Demand Drivers")
    manual_input = st.text_area(
        "Comma-separated custom drivers",
        value=st.session_state.get("manual_driver_input", ""),
        key="manual_input_area"
    )
    st.session_state["manual_driver_input"] = manual_input

    custom_drivers = [d.strip() for d in manual_input.split(",") if d.strip()]
    all_drivers = sorted(set(selected + custom_drivers))
    if not all_drivers:
        st.info("⚠️ Please select or enter at least one driver.")
        return

    st.markdown("### 📊 4-Year Historical Demand Driver KPI ")
    years = get_recent_years()

    if st.session_state.get("business_driver_table") is not None:
        prev_df = st.session_state["business_driver_table"]
        for d in all_drivers:
            if d not in prev_df["Business Driver"].values:
                new_row = {"Business Driver": d, **{y: "" for y in years}}
                prev_df = pd.concat([prev_df, pd.DataFrame([new_row])], ignore_index=True)
        df_editable = prev_df[prev_df["Business Driver"].isin(all_drivers)].copy()
    else:
        df_editable = pd.DataFrame([
            {"Business Driver": d, **{y: "" for y in years}} for d in all_drivers
        ])

    edited_df = st.data_editor(
        df_editable,
        use_container_width=True,
        num_rows="dynamic",
        key="driver_matrix_editor"
    )
    if edited_df is not None and not edited_df.empty:

    # Store in session
     st.session_state["business_driver_table"] = edited_df
    st.session_state["driver_years"] = years

    
    

