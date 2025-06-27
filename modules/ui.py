import streamlit as st

def page_container(title: str, help_text: str = None):
    st.markdown(f"## {title}")
    if help_text:
        with st.expander("ℹ️ Help & Guidance"):
            st.write(help_text)
    st.markdown("---")
