import streamlit as st

# -------------------- Session State --------------------
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "auth_message" not in st.session_state:
    st.session_state["auth_message"] = ""

# -------------------- Centered Login Form --------------------
if st.session_state["current_user"] is None:
    # Hide sidebar completely
    st.set_page_config(page_title="Data Analyst To-Do List", layout="centered")

    # Create a centered container
    login_container = st.container()
    with login_container:
        st.markdown("<h1 style='text-align:center'>🧠 Login / Register</h1>", unsafe_allow_html=True)
        action = st.radio("Action:", ["Login", "Register"], horizontal=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if action == "Register":
            confirm_password = st.text_input("Confirm Password", type="password")

        submit = st.button("Submit")

        if submit:
            if not username.strip() or not password:
                st.session_state["auth_message"] = "⚠️ Enter both username and password."
            elif action == "Register" and password != confirm_password:
                st.session_state["auth_message"] = "⚠️ Passwords do not match."
            else:
                # Here, do your user validation/registration
                # On success:
                st.session_state["current_user"] = username.lower()
                st.session_state["auth_message"] = f"✅ {action} successful!"

        if st.session_state["auth_message"]:
            st.info(st.session_state["auth_message"])

# -------------------- Show Sidebar + App after Login --------------------
if st.session_state["current_user"] is not None:
    st.set_page_config(page_title="Data Analyst To-Do List", layout="wide")
    st.sidebar.header("Welcome, " + st.session_state["current_user"])
    # Here, add your sidebar and full app code (task board, analytics, motivational quotes, etc.)
