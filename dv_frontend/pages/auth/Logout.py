import streamlit as st
import requests

st.set_page_config(page_title="Logout", page_icon="🚪")

LOGOUT_API_URL = "https://your-api-endpoint.com/logout"  # 🔸 Replace with your logout API URL

if "logged_in" in st.session_state and st.session_state.logged_in:
    try:
        # Optional: if your API expects a token in headers
        headers = {}
        if "token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.token}"

        response = requests.post(LOGOUT_API_URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                st.success("Logged out successfully!")
            else:
                st.warning(data.get("message", "Logout API returned a warning."))
        else:
            st.error(f"Logout API error: {response.status_code}")
    except Exception as e:
        st.error(f"Error calling logout API: {e}")

    # Clear session
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.token = None
    st.switch_page("pages/auth/login.py")
else:
    st.info("You are already logged out.")
    st.switch_page("pages/auth/login.py")
