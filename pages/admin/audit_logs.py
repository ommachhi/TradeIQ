import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import AdminActivityLog, User

def render(user: dict):
    st.title("Audit Logs")
    st.caption("Track administrative actions and system events for security.")
    
    db = SessionLocal()
    try:
        logs = db.query(AdminActivityLog, User).join(User, AdminActivityLog.admin_id == User.id).order_by(AdminActivityLog.created_at.desc()).limit(100).all()
        
        if not logs:
            st.info("No audit logs found.")
        else:
            data = []
            for log, admin in logs:
                data.append({
                    "Timestamp": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Admin": admin.name,
                    "Action": log.action,
                    "IP Address": log.ip_address or "Unknown"
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            
    finally:
        db.close()
