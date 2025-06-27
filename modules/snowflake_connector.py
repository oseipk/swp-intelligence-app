from dotenv import load_dotenv
import os
import snowflake.connector
import pandas as pd
import streamlit as st

# ✅ Load environment variables
load_dotenv()

# ✅ Fail early if missing
def validate_env_vars():
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA"
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"❌ Missing environment variables: {', '.join(missing)}")

def get_connection():
    validate_env_vars()
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        authenticator='externalbrowser',
        user=os.getenv("SNOWFLAKE_USER"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

@st.cache_data(ttl=3600)
def fetch_workforce_data():
    query = """
    SELECT DISTINCT 
        EMPLOYEE_PERSONNEL_NUMBER AS employee_personnel_number,
        CALENDAR_YEAR AS calendar_year,
        ZONE_NIM_GEO AS zone_nim_geo,
        FUNCTION_UNIT AS function,
        REASON_FOR_ACTION AS reason_for_action,
        TECHNICAL_ENTRY_DATE AS technical_entry_date,
        ACTION_DATE AS action_date,
        EMPLOYMENT_STATUS AS employment_status
    FROM edw.prshrtpms.pd_headcount_v
    WHERE CALENDAR_YEAR BETWEEN EXTRACT(YEAR FROM CURRENT_DATE) - 4 
    AND EXTRACT(YEAR FROM CURRENT_DATE) - 1
    ORDER BY CALENDAR_YEAR, FUNCTION
    """
    conn = get_connection()
    df_raw = pd.read_sql(query, conn)
    conn.close()
    return df_raw