import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload Dataset", page_icon="📂")

st.title("📂 Upload Dataset")

st.markdown(
    """
    **💡 Tip:** For best performance, please upload datasets **no larger than 150 MB**.  
    Larger files may slow down processing or exceed browser memory limits.
    """
)

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state["uploaded_df"] = df
        st.success(f"✅ {uploaded_file.name} uploaded and stored in session!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Upload a CSV or Excel file to continue.")
