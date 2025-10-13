import streamlit as st

def get_nav():
    # ------------------------- Dashboard ---------------------------
    dashboard_page = st.Page(
        "pages/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=True,
    )

    # ------------------------- Data ---------------------------
    upload_dataset = st.Page(
        "pages/data/upload_dataset.py",
        title="Upload Dataset",
        icon=":material/upload_file:",
    )
    view_dataset = st.Page(
        "pages/data/view_dataset.py",
        title="View Dataset",
        icon=":material/table_view:",
    )

    # ------------------------- Navigation ---------------------------
    return ( st.navigation(
        {
            "Dashboard": [dashboard_page],
            "Data": [upload_dataset, view_dataset],
        }
    ))
