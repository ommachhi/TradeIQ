import streamlit as st
from database.db import SessionLocal
from database.models import User
from auth.auth import hash_password, verify_password

def render(user: dict):
    st.title("Settings")
    st.caption("Manage your account and preferences.")
    
    st.subheader("👤 Profile")
    with st.form("profile_form"):
        name = st.text_input("Full Name", value=user['name'])
        email = st.text_input("Email", value=user['email'], disabled=True)
        if st.form_submit_button("Save Changes"):
            db = SessionLocal()
            try:
                u = db.query(User).get(user['id'])
                u.name = name
                db.commit()
                st.session_state["user"]["name"] = name
                st.success("Profile updated successfully.")
            finally:
                db.close()
                
    st.subheader("⚙️ Preferences")
    with st.form("prefs_form"):
        st.toggle("Auto-refresh Live Quotes", value=st.session_state.get("auto_refresh", True), key="pref_ar")
        st.toggle("Email Notifications", value=st.session_state.get("email_notif", True), key="pref_en")
        st.info("🌙 Dark mode is always enabled in TREDALQ.")
        mkt = st.selectbox("Default Market", ["NSE", "BSE", "Global"])
        if st.form_submit_button("Save Preferences"):
            st.session_state["auto_refresh"] = st.session_state["pref_ar"]
            st.session_state["email_notif"] = st.session_state["pref_en"]
            st.session_state["default_market"] = mkt
            st.success("Preferences saved.")

    st.subheader("🔒 Security")
    with st.form("sec_form"):
        curr_p = st.text_input("Current Password", type="password")
        new_p = st.text_input("New Password", type="password")
        conf_p = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("Change Password"):
            if new_p != conf_p:
                st.error("New passwords do not match.")
            else:
                db = SessionLocal()
                try:
                    u = db.query(User).get(user['id'])
                    if not verify_password(curr_p, u.password_hash):
                        st.error("Incorrect current password.")
                    else:
                        u.password_hash = hash_password(new_p)
                        db.commit()
                        st.success("Password changed successfully.")
                finally:
                    db.close()
