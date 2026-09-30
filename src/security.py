import hmac
import os

import streamlit as st


def get_access_password():
    value = os.getenv("APP_ACCESS_PASSWORD")
    if value:
        return value
    try:
        return st.secrets.get("APP_ACCESS_PASSWORD")
    except Exception:
        return None


def require_login():
    expected = get_access_password()
    if not expected:
        return True
    if st.session_state.get("authenticated"):
        return True
    st.title("🔐 NexaRAG Access")
    supplied = st.text_input("Access password", type="password")
    if st.button("Sign in", type="primary"):
        if hmac.compare_digest(supplied, expected):
            st.session_state.authenticated = True
            st.rerun()
        st.error("Invalid access password.")
    return False
