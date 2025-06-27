# modules/pdf_parser.py
import streamlit as st
import fitz

def render_pdf_upload():
    st.header("📄 Upload Nestlé Annual Report (PDF)")
    file = st.file_uploader("Upload PDF", type="pdf")
    
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        full_text = "\n".join([page.get_text() for page in doc])
        st.session_state["annual_text"] = full_text
        st.success("PDF uploaded and text extracted.")

        with st.expander("Preview Extracted Text"):
            st.text(full_text[:3000])
