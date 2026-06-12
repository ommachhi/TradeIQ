import streamlit as st
from database.db import SessionLocal
from database.models import User

def render(user: dict):
    st.title("My Profile")
    st.caption("Manage your personal details and preferences.")
    
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user["id"]).first()
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("### Personal Information")
            with st.form("profile_form"):
                name = st.text_input("Full Name", value=db_user.name)
                email = st.text_input("Email", value=db_user.email, disabled=True)
                
                if st.form_submit_button("Update Profile"):
                    db_user.name = name
                    db.commit()
                    st.success("Profile updated successfully. Please sign in again to reflect changes.")
                    
        with c2:
            st.markdown("### Security")
            with st.form("security_form"):
                st.text_input("New Password", type="password")
                st.text_input("Confirm New Password", type="password")
                if st.form_submit_button("Change Password"):
                    st.info("Password update mocked for safety.")
                    
    finally:
        db.close()
