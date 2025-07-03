import streamlit as st
import pandas as pd
import plotly.express as px

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

def section_header(title: str):
    st.markdown(f"""
        <div style="background-color:#e8f1fa;padding:12px 18px;border-radius:8px;margin-bottom:10px;">
            <h3 style='color:#0A5A9C;margin:0;'>{title}</h3>
        </div>
    """, unsafe_allow_html=True)

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

    df_gap["Strategic Impact"] = df_gap["Critical Role"].map(strategic_scores)
    df_gap["Auto Strategy"] = df_gap.apply(
        lambda row: assign_strategy(row["Gap %"], row["Strategic Impact"]), axis=1
    )

    # Manual override
    st.subheader("🛠️ Optional Manual Strategy Override")
    strategy_options = ["Buy", "Build", "Borrow", "Boost"]
    strategy_overrides = {}

    for role in df_gap["Critical Role"].unique():
        strategy_overrides[role] = st.selectbox(
            f"Override Strategy for **{role}**",
            options=["(Use Auto)"] + strategy_options,
            key=f"{role}_manual_strategy"
        )

    df_gap["Final Strategy"] = df_gap.apply(
        lambda row: strategy_overrides.get(row["Critical Role"])
        if strategy_overrides.get(row["Critical Role"]) != "(Use Auto)"
        else row["Auto Strategy"],
        axis=1
    )

    # Filter
    st.subheader("🔎 Filter by Strategy")
    selected_strategies = st.multiselect(
        "Select Strategy Type(s) to View",
        options=strategy_options,
        default=strategy_options
    )
    filtered_df = df_gap[df_gap["Final Strategy"].isin(selected_strategies)]

    # Display detailed table
    st.subheader("📋 Final Strategy Assignment Table")
    st.dataframe(
        filtered_df[[
            "Critical Role", "Year", "Scenario Demand", "Projected Supply",
            "Gap", "Gap %", "Strategic Impact", "Final Strategy"
        ]],
        use_container_width=True
    )

    # Strategy Distribution Summary (WITH critical roles)
    st.subheader("📊 Strategy Distribution Summary")

    summary_rows = []
    grouped = filtered_df.groupby(["Final Strategy", "Year"])
    for (strategy, year), group in grouped:
        roles = group["Critical Role"].unique().tolist()
        summary_rows.append({
            "Strategy": strategy,
            "Year": year,
            "Roles": len(roles),
            "Total_Gap": round(group["Gap"].sum(), 1),
            "Critical Roles": ", ".join(roles)
        })

    strategy_summary = pd.DataFrame(summary_rows)
    st.dataframe(strategy_summary, use_container_width=True)

    # Strategic Quadrant View
    st.subheader("📈 Strategic - Gap")

    try:
        chart_data = df_gap.copy()
        chart_data["Gap"] = chart_data["Gap"].abs().clip(upper=10) 


        def classify_quadrant(row):
            if row["Gap %"] < 50 and row["Strategic Impact"] < 4:
                return "Boost"
            elif row["Gap %"] < 50 and row["Strategic Impact"] >= 4:
                return "Build"
            elif row["Gap %"] >= 50 and row["Strategic Impact"] >= 4:
                return "Buy"
            elif row["Gap %"] >= 50 and row["Strategic Impact"] < 4:
                return "Borrow"
            return "Other"

        chart_data["Quadrant"] = chart_data.apply(classify_quadrant, axis=1)
        chart_data["Size"] = chart_data["Gap"].abs().clip(lower=1)

        fig = px.scatter(
            chart_data,
            x="Gap",
            y="Strategic Impact",
            color="Quadrant",
            size="Size",
            hover_name="Critical Role",
            text="Critical Role",
            animation_frame="Year",
            title="Strategic Workforce Gap (4Bs)",
            size_max=40,
            category_orders={"Quadrant": ["Boost", "Build", "Buy", "Borrow"]}
        )

        fig.update_layout(
            xaxis=dict(title="Workforce Gap", range=[0, 10], zeroline=False),
            yaxis=dict(title="Strategic Impact (1–5)", range=[0.5, 5.5], dtick=1),
            template="plotly_white",
            font=dict(family="Arial", size=12),
            margin=dict(l=40, r=20, t=60, b=40),
            legend_title_text="Strategy"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Bubble plot failed: {e}")

    # Save final gap table
    st.session_state["gap_management_output"] = df_gap
