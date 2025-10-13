import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon=":material/dashboard:")

# --- Welcome Header ---
st.title("👋 Welcome to the Data Insight App")

st.markdown(
    """
    ### 🚀 Get Started
    This application helps you **analyze your datasets instantly**.

    You can:
    - 📂 **Upload your dataset** (CSV or Excel)
    - 📊 **View your data** in a clean, interactive table
    - 📈 **Generate an initial data analysis report** automatically — including insights like missing values, column types, and summary statistics

    ---
    #### 💡 Why use this app?
    Whether you’re a **data analyst**, **researcher**, or **student**, this platform gives you a quick start for exploring your data before deeper analysis or modeling.

    Navigate to the **Data section** from the sidebar to upload and explore your dataset.
    """
)

st.info("➡️ Go to the **Data → Upload Dataset** page to begin your analysis.")
