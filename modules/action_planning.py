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
from modules import ui
def render_action_planning():
    inject_custom_styles()
    section_header("🛠️ Action Planning Based on Gap Strategy")

    if "gap_management_output" not in st.session_state:
        st.warning("❗ Please complete Gap Management step first.")
        return

    df = st.session_state["gap_management_output"]
    forecast_years = sorted(df["Year"].unique().tolist())

    initiatives = []
    st.subheader("🎯 Define Actions by Strategy")

    for role in df["Critical Role"].unique():
        strategy = df[df["Critical Role"] == role]["Strategy"].mode()[0]
        total_gap = df[df["Critical Role"] == role]["Gap"].sum()

        st.markdown(f"### 📌 Role: **{role}** | Strategy: **{strategy}** | Total Gap: {total_gap:.1f} FTE")

        initiative = st.text_input(f"Initiative for {role}", key=f"{role}_initiative")
        start = st.selectbox("Start Year", forecast_years, key=f"{role}_start")
        end = st.selectbox("End Year", forecast_years, index=len(forecast_years)-1, key=f"{role}_end")
        impact = st.number_input(f"Expected FTE Impact", min_value=0, key=f"{role}_impact")
        cost = st.number_input(f"Estimated Cost (€k)", min_value=0.0, key=f"{role}_cost")
        feasibility = st.selectbox("Feasibility", ["High", "Medium", "Low"], key=f"{role}_feasibility")

        initiatives.append({
            "Role": role,
            "Strategy": strategy,
            "Initiative": initiative,
            "Start Year": start,
            "End Year": end,
            "Expected Impact (FTE)": impact,
            "Estimated Cost (€k)": cost,
            "Feasibility": feasibility
        })

    df_plan = pd.DataFrame(initiatives)
    st.subheader("📋 Summary of Action Plans")
    st.dataframe(df_plan, use_container_width=True)

    st.session_state["action_plan_table"] = df_plan
    st.success("✅ Action plan saved for tracking.")


