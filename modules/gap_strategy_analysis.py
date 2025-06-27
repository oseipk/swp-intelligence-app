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
import plotly.express as px
from modules import ui

def render_gap_strategy_analysis():
    inject_custom_styles()
    section_header("🔍 Gap Strategy Analysis by 4Bs")

    if "gap_management_output" not in st.session_state:
        st.warning("⚠️ Please complete Gap Management first.")
        return

    df = st.session_state["gap_management_output"].copy()

    # Group by strategy and year
    strategy_summary = df.groupby(["Strategy", "Year"])["Gap"].sum().reset_index()
    strategy_summary["Gap"] = strategy_summary["Gap"].abs()

    st.subheader("📊 Strategy Distribution Over Time")
    fig = px.bar(
        strategy_summary,
        x="Year",
        y="Gap",
        color="Strategy",
        barmode="group",
        title="Total Workforce Gap by Strategy Over Years",
        labels={"Gap": "Gap (FTE)"}
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial", size=12, color="#333"),
        margin=dict(l=40, r=20, t=50, b=40))

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Strategy Breakdown by Role")
    role_summary = df.groupby(["Critical Role", "Strategy"]).agg({
        "Gap": "sum",
        "Strategic Impact": "mean"
    }).reset_index()
    role_summary["Gap"] = role_summary["Gap"].abs()
    st.dataframe(role_summary, use_container_width=True)

    st.success("✅ Gap strategy analysis complete.")
    