import streamlit as st
import requests

st.set_page_config(page_title="Login", page_icon="🔐")

API_URL = "https://your-api-endpoint.com/login"  # 🔸 Replace with your real API endpoint

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("🔐 Login")

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            try:
                response = requests.post(API_URL, json={"username": username, "password": password})
                
                if response.status_code == 200:
                    data = response.json()
                    # Example expected API response: {"success": true, "user": {"name": "Admin"}}

                    if data.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.username = data["user"]["name"] if "user" in data else username
                        st.success("Login successful!")
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error(data.get("message", "Invalid credentials."))
                else:
                    st.error(f"Server returned status {response.status_code}")
            except Exception as e:
                st.error(f"Error calling API: {e}")
else:
    st.info("You are already logged in.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
