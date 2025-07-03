import streamlit as st
import pandas as pd

# ========== UI STYLING ========== #
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

# === Strategy-based Action Suggestions (Manual Rule-Based) === #
def suggest_action(role, strategy):
    if strategy == "Buy":
        return f"Initiate targeted external recruitment campaign for {role}."
    elif strategy == "Build":
        return f"Launch internal upskilling or cross-training programs to develop {role}."
    elif strategy == "Borrow":
        return f"Engage external contractors or temporary consultants for {role}."
    elif strategy == "Boost":
        return f"Implement retention strategies or job redesign to maximize current {role} capacity."
    return f"Reassess strategic plan for {role}."

def recommend_owner(strategy):
    return {
        "Buy": "Talent Acquisition",
        "Build": "L&D Team",
        "Borrow": "HRBP",
        "Boost": "People & Culture"
    }.get(strategy, "HR Strategy")

def estimate_duration(impact):
    if impact >= 4:
        return "3–6 months"
    elif impact >= 2:
        return "6–9 months"
    else:
        return "9–12+ months"

# ========== MAIN RENDER FUNCTION ========== #
def render_action_planning():
    inject_custom_styles()
    section_header("🛠️ Action Planning Based on Gap Strategy")

    if "gap_strategy_output" not in st.session_state:
        st.warning("❗ Please complete the Gap Strategy module first.")
        return

    df_strategy = st.session_state["gap_strategy_output"].copy()

    st.subheader("📋 Strategy-Driven Recommendations")

    action_rows = []
    for _, row in df_strategy.iterrows():
        role = row["Critical Role"]
        strategy = row["Final Strategy"]
        impact = row["Strategic Impact"]
        gap = round(row["Total Gap"], 1)
        year = row["Peak Year"]
        feasibility = "High" if impact >= 4 else "Medium" if impact >= 2 else "Low"

        suggestion = suggest_action(role, strategy)

        action_rows.append({
            "Role": role,
            "Peak Year": year,
            "Total Gap": gap,
            "Strategy": strategy,
            "Recommended Action": suggestion,
            "Feasibility": feasibility,
            "Owner": recommend_owner(strategy),
            "Expected Duration": estimate_duration(impact),
            "Priority Score": row["Priority Score"]
        })

    df_plan = pd.DataFrame(action_rows).sort_values(by="Priority Score", ascending=False)

    st.dataframe(df_plan, use_container_width=True)

    # Save to session
    st.session_state["action_plan_table"] = df_plan
    
