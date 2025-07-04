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
        </style>
    """, unsafe_allow_html=True)

def section_header(title: str):
    st.markdown(f"""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>{title}</h3>
        </div>
    """, unsafe_allow_html=True)

# 🔍 Strategy mapping logic
def suggest_action(strategy, impact, gap):
    if strategy == "Buy":
        return "Hire externally (urgently)" if gap >= 50 else "Hire externally"
    elif strategy == "Build":
        return "Upskill internally (targeted programs)"
    elif strategy == "Borrow":
        return "Use contractors or redeploy from low-impact areas"
    elif strategy == "Boost":
        return "Monitor and retain existing staff"
    return "No action required"

def render_gap_strategy_analysis():
    inject_custom_styles()
    section_header("🧠 Intelligent Gap Strategy Prioritization")

    if "gap_management_output" not in st.session_state:
        st.warning("⚠️ Please complete Gap Management first.")
        return

    df = st.session_state["gap_management_output"].copy()
    df["Gap"] = df["Gap"].abs()

    # Step 1: Identify peak year of gap per role
    role_summary = df.groupby("Critical Role").agg({
        "Gap": "sum",
        "Strategic Impact": "mean",
        "Final Strategy": "first"
    }).reset_index()

    peak_years = df.loc[df.groupby("Critical Role")["Gap"].idxmax()][["Critical Role", "Year"]]
    role_summary = role_summary.merge(peak_years, on="Critical Role", how="left")
    role_summary.rename(columns={"Gap": "Total Gap", "Year": "Peak Year"}, inplace=True)

    # Step 2: AI-inspired action recommendation
    role_summary["Recommended Action"] = role_summary.apply(
        lambda row: suggest_action(row["Final Strategy"], row["Strategic Impact"], row["Total Gap"]),
        axis=1
    )

    # Step 3: Priority Score 
    role_summary["Priority Score"] = (
        role_summary["Total Gap"] * 0.5 +
        role_summary["Strategic Impact"] * 10
    ).round(1)

    role_summary = role_summary.sort_values(by="Priority Score", ascending=False)

    # Display strategy table
    st.subheader(" Recommended Strategic Actions by Role")
    st.dataframe(role_summary[[
        "Critical Role", "Peak Year", "Total Gap", "Strategic Impact",
        "Final Strategy", "Recommended Action", "Priority Score"
    ]], use_container_width=True)

    # Step 4: Visual summary
    st.subheader(" Strategy Mix by Total Gap")
    chart = df.groupby("Final Strategy")["Gap"].sum().reset_index()
    chart["Gap"] = chart["Gap"].round(1)
    fig = px.bar(chart, x="Final Strategy", y="Gap", color="Final Strategy", text="Gap")
    fig.update_layout(template="plotly_white", title="Total Gaps by Strategy")
    st.plotly_chart(fig, use_container_width=True)

    # Save for action planning
    st.session_state["gap_strategy_output"] = role_summary
    
