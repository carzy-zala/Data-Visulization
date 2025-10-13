import streamlit as st

st.set_page_config(page_title="View Dataset", page_icon="📊")

st.title("📊 View Uploaded Dataset")

df = st.session_state.get("uploaded_df")

if df is not None:
    st.success("✅ Data loaded from session.")
    st.dataframe(df)
else:
    st.warning("⚠️ No dataset found. Please upload one first from the **Upload Dataset** page.")
