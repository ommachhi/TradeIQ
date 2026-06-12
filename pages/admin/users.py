import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import User

def render(user: dict):
    st.title("User Management")
    st.caption("Manage user accounts, roles, and platform access.")
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### User Directory")
            if not users:
                st.info("No users found.")
            else:
                data = []
                for u in users:
                    data.append({
                        "ID": u.id,
                        "Name": u.name,
                        "Email": u.email,
                        "Role": u.role,
                        "Status": "Active" if u.is_active else "Inactive",
                        "Last Login": u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "Never"
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True)
                
        with c2:
            st.markdown("### Update User Role")
            with st.form("update_role_form"):
                user_id = st.number_input("User ID", min_value=1, step=1)
                new_role = st.selectbox("New Role", ["User", "Premium", "Admin"])
                is_active = st.checkbox("Account Active", value=True)
                
                if st.form_submit_button("Update User"):
                    target_user = db.query(User).filter(User.id == user_id).first()
                    if target_user:
                        if target_user.id == user["id"] and not is_active:
                            st.error("You cannot deactivate your own account.")
                        else:
                            target_user.role = new_role
                            target_user.is_active = is_active
                            db.commit()
                            st.success(f"Updated user ID {user_id}")
                            st.rerun()
                    else:
                        st.error("User not found.")
    finally:
        db.close()
