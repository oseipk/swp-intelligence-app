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
import requests
import plotly.express as px
from modules import ui

# Constants
WBG_COUNTRY_LIST_URL = "https://api.worldbank.org/v2/country?format=json&per_page=300"
POP_IND = "SP.POP.TOTL"
UNEMP_IND = "SL.UEM.TOTL.ZS"
ADZUNA_SALARY_URL = "https://api.adzuna.com/v1/api/salaries"
APP_ID = st.secrets.get("ADZUNA_APP_ID")
APP_KEY = st.secrets.get("ADZUNA_APP_KEY")

@st.cache_data
def get_wb_countries():
    resp = requests.get(WBG_COUNTRY_LIST_URL).json()
    return [(c["id"], c["name"]) for c in resp[1]]

@st.cache_data
def fetch_worldbank(indicator, country_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=100"
    res = requests.get(url).json()
    data = res[1] if isinstance(res, list) else []
    return {d["date"]: d["value"] for d in data if d["value"] is not None}

@st.cache_data
def fetch_salary_role_country(role, country_code):
    """Query Adzuna API for average salary of a role in a country (USD)."""
    if not (APP_ID and APP_KEY):
        return None
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": role,
        "where": country_code,
        "content-type": "application/json"
    }
    res = requests.get(ADZUNA_SALARY_URL, params=params)
    if res.status_code != 200:
        return None
    data = res.json()
    avg = data.get("mean")
    return round(avg, 2) if isinstance(avg, (int, float)) else None

def render_external_benchmarking():
    inject_custom_styles()
    st.header("🌍 External Benchmarking & Critical Role Context")

    if "critical_workforce_forecast" not in st.session_state:
        st.warning("❗ Please complete the Critical Workforce Forecasting step first.")
        return

    roles = st.session_state["critical_workforce_forecast"]["Role"].unique().tolist()
    st.subheader("🧩 Critical Roles Selected")
    st.write(roles)

    # Choose geography
    countries = get_wb_countries()
    country_code, country_name = st.selectbox(
        "Select Country",
        options=countries,
        format_func=lambda x: x[1]
    )
    wb_pop = fetch_worldbank(POP_IND, country_code)
    wb_unemp = fetch_worldbank(UNEMP_IND, country_code)

    # Salary benchmarking
    bench_rows = []
    for role in roles:
        salary = fetch_salary_role_country(role, country_name)
        bench_rows.append({
            "Role": role,
            "Avg Salary (USD)": f"${salary:,}" if salary else ""
        })
    bench_df = pd.DataFrame(bench_rows)
    st.subheader(f"📊 Salary Benchmark in {country_name}")
    st.dataframe(bench_df, use_container_width=True)

    # Population & unemployment trend
    years = sorted(set(wb_pop.keys()) & set(wb_unemp.keys()))[-5:]
    if years:
        pop = [wb_pop[y] for y in years]
        unemployment_rate = [wb_unemp[y] for y in years]
        unemployment_pop = [pop[i] * unemployment_rate[i] / 100 for i in range(len(years))]

        st.subheader(f"📉 Population & Unemployment Trends for {country_name}")
        df_trend = pd.DataFrame({
            "Year": years,
            "Population": pop,
            "Unemployment Rate (%)": unemployment_rate,
            "Unemployed Population": unemployment_pop
        })
        fig = px.line(df_trend, x="Year", y=["Population", "Unemployed Population"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🗺️ Unemployment Map")
        map_df = df_trend[["Year", "Unemployment Rate (%)", "Unemployed Population"]]
        map_df["Country"] = country_name
        fig_map = px.choropleth(
            map_df,
            locations=[country_code]*len(years),
            color="Unemployed Population",
            locationmode="ISO-3",
            hover_name="Country",
            animation_frame="Year",
            color_continuous_scale="Blues",
            title="Country Unemployed Population Across Years"
        )
        fig_map.update_layout(
            template="plotly_white",
            font=dict(family="Arial", size=12, color="#333"),
            margin=dict(l=40, r=20, t=50, b=40))

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No recent population/unemployment data available.")

    st.success("✅ External benchmarking loaded successfully.")
    st.session_state["external_benchmark_data"] = bench_df
