import streamlit as st

def get_nav():
    # Ensure the key exists
    if "uploaded_df" not in st.session_state:
        st.session_state["uploaded_df"] = None

    # ------------------------- Pages ---------------------------
    dashboard_page = st.Page(
        "pages/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=True,
    )

    upload_dataset = st.Page(
        "pages/data/upload_dataset.py",
        title="Upload Dataset",
        icon=":material/upload_file:",
    )

    view_dataset = st.Page(
        "pages/data/view_dataset.py",
        title="Dataset Matrix",
        icon=":material/table_view:",
    )

    bar_chart = st.Page(
        "pages/visualization/bar_chart.py",
        title="Bar Charts",
        icon=":material/bar_chart:",
    )
    
    distribution = st.Page(
    "pages/visualization/distribution.py",
    title="Data Distribution",
    icon=":material/insights:",
    )
    
    line_chart = st.Page(
    "pages/visualization/line_chart.py",
    title="Line Charts",
    icon=":material/insights:",
    )
    
    # ------------------------- Conditional Nav ---------------------------
    has_data = st.session_state["uploaded_df"] is not None

    if has_data:
        # Full app once data exists
        sections = {
            "Dashboard": [dashboard_page],
            "Data": [upload_dataset, view_dataset],
            "Visualization": [distribution,bar_chart,line_chart],
        }
    else:
        # Only allow Dashboard + Upload until data is available
        sections = {
            "Dashboard": [dashboard_page],
            "Data": [upload_dataset],
        }

    return st.navigation(sections)
