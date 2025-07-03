import streamlit as st
import pandas as pd
from datetime import datetime

# Custom styling
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

# Section headers
def section_header(title: str):
    st.markdown(f"""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>{title}</h3>
        </div>
    """, unsafe_allow_html=True)

# Get last N years
def get_recent_years(n=4):
    current_year = datetime.today().year
    return [str(current_year - i - 1) for i in reversed(range(n))]

# Render UI
def render_driver_definition():
    inject_custom_styles()
    section_header("Business Demand Drivers")

    predefined_drivers = [
        "e-Intensity (%)", "e-NNS", "E-Commerce growth", "Marketing spend in Digital media (%)",
        "Finished Good Inventory (# of days)", "Organic Growth(%)",
        "Customer Order Fulfillment(%)", "On-Time In Full(%)"
    ]

    # Reset logic
    if st.button(" Reset Driver Input"):
        st.session_state.pop("selected_driver_list", None)
        st.session_state.pop("manual_driver_input", None)
        st.session_state.pop("business_driver_table", None)
        st.rerun()

    # 🧠 Input accepted once and saved
    if "selected_driver_list" not in st.session_state or "manual_driver_input" not in st.session_state:
        st.markdown("### Select or Add Demand Drivers")

        selected = st.multiselect(
            "Select from pre-defined drivers",
            options=predefined_drivers,
            default=[],
            key="driver_multiselect_temp"
        )

        manual_input = st.text_area(
            "➕ Add Custom Demand Drivers (comma-separated)",
            value="",
            key="manual_input_area_temp"
        )

        if st.button("✅ Confirm Selection"):
            custom_drivers = [d.strip() for d in manual_input.split(",") if d.strip()]
            combined_drivers = sorted(set(selected + custom_drivers))
            if not combined_drivers:
                st.warning("⚠️ Please select or enter at least one driver.")
                return
            # Store once
            st.session_state["selected_driver_list"] = selected
            st.session_state["manual_driver_input"] = manual_input
            st.rerun()
        else:
            return

    # 🎯 Use stored inputs
    selected = st.session_state["selected_driver_list"]
    manual_input = st.session_state["manual_driver_input"]
    custom_drivers = [d.strip() for d in manual_input.split(",") if d.strip()]
    all_drivers = sorted(set(selected + custom_drivers))
    years = get_recent_years()

    st.markdown("### 📊 4-Year Historical Demand Driver KPI")

    if "business_driver_table" in st.session_state:
        prev_df = st.session_state["business_driver_table"]
        # Add any missing drivers
        for d in all_drivers:
            if d not in prev_df["Business Driver"].values:
                new_row = {"Business Driver": d, **{y: "" for y in years}}
                prev_df = pd.concat([prev_df, pd.DataFrame([new_row])], ignore_index=True)
        df_editable = prev_df[prev_df["Business Driver"].isin(all_drivers)].copy()
    else:
        df_editable = pd.DataFrame([
            {"Business Driver": d, **{y: "" for y in years}} for d in all_drivers
        ])

    # 🚧 Editable Table UI
    edited_df = st.data_editor(
        df_editable,
        use_container_width=True,
        num_rows="dynamic",
        key="driver_matrix_editor"
    )

    # ✅ Save manually via button
    if st.button("💾 Save Driver Data"):
        st.session_state["business_driver_table"] = edited_df
        st.session_state["driver_years"] = years

    # ✅ Show current saved table
    if "business_driver_table" in st.session_state:
        st.markdown("### 📁 Last Saved Driver Data")
        st.dataframe(st.session_state["business_driver_table"], use_container_width=True)


