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

def assign_strategy(gap_pct, strategic_score):
    if strategic_score >= 4:
        return "Buy" if gap_pct >= 50 else "Build"
    elif 2 <= strategic_score < 4:
        return "Borrow" if gap_pct >= 50 else "Boost"
    else:
        return "Boost"

def render_gap_management():
    inject_custom_styles()
    section_header("🎯 Workforce Gap Management with 4Bs Strategy")

    # 🔄 Validate prerequisites
    if "workforce_role_gap_table" not in st.session_state:
        st.warning("❗ Please complete the Gap Analysis step first.")
        return

    df_gap = st.session_state["workforce_role_gap_table"].copy()
    years = sorted(df_gap["Year"].unique())

    st.subheader("⭐ Assign Strategic Importance Scores (1 = Low, 5 = High)")
    strategic_scores = st.session_state.get("strategic_scores", {})

    for role in df_gap["Critical Role"].unique():
        default = strategic_scores.get(role, 3)
        score = st.slider(
            f"Strategic Impact for **{role}**",
            min_value=1, max_value=5, value=default,
            key=f"strategic_score_{role}"
        )
        strategic_scores[role] = score

    st.session_state["strategic_scores"] = strategic_scores

    # 📊 Strategy Assignment
    df_gap["Strategic Impact"] = df_gap["Critical Role"].map(strategic_scores)
    df_gap["Strategy"] = df_gap.apply(
        lambda row: assign_strategy(row["Gap %"], row["Strategic Impact"]),
        axis=1
    )

    # 💡 Role-Strategy Table
    st.subheader("📋 4Bs Strategy Assignment Table")
    summary_table = df_gap[[
        "Critical Role", "Year", "Scenario Demand", "Projected Supply",
        "Gap", "Gap %", "Strategic Impact", "Strategy"
    ]].copy()
    st.dataframe(summary_table, use_container_width=True)

    # 🧠 Strategy Count Summary
    st.subheader("🔢 Strategy Distribution Overview")
    strategy_summary = summary_table.groupby(["Strategy", "Year"]).agg(
        Roles=("Critical Role", "nunique"),
        Total_Gap=("Gap", "sum")
    ).reset_index()
    st.dataframe(strategy_summary, use_container_width=True)

    # 📊 Bubble Plot
    st.subheader("🧠 Strategic Gap Bubble Plot")
    try:
        chart_data = df_gap.copy()
        chart_data["Gap Size"] = chart_data["Gap"].abs()
        fig = px.scatter(
            chart_data,
            x="Gap %",
            y="Strategic Impact",
            size="Gap Size",
            color="Strategy",
            hover_name="Critical Role",
            animation_frame="Year",
            title="Strategic Gap Bubble Plot (4Bs)",
            size_max=50,
            range_x=[0, 100],
            range_y=[0.5, 5.5]
        )
        fig.update_layout(
             template="plotly_white",
             font=dict(family="Arial", size=12, color="#333"),
             margin=dict(l=40, r=20, t=50, b=40))

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Bubble plot failed: {e}")

    # 🔐 Save output
    st.session_state["gap_management_output"] = df_gap
    st.success("✅ Gap management analysis completed and saved.")

