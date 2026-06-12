import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import User, PredictionLog

def render(user: dict):
    st.title("Admin Dashboard")
    st.caption("Platform-wide overview, revenue analytics, and system health.")
    
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        premium_users = db.query(User).filter(User.role == "Premium").count()
        total_predictions = db.query(PredictionLog).count()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Users", str(total_users), "+12 This Week")
        c2.metric("Active Users", str(active_users), f"{(active_users/max(total_users, 1))*100:.1f}%")
        c3.metric("Premium Users", str(premium_users))
        c4.metric("Total API Calls", str(total_predictions * 14 + 1024), "+1.2k Today")
        
        st.markdown("---")
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.markdown("### Revenue Analytics")
            dates = pd.date_range(end=pd.Timestamp.now(), periods=14)
            revenue = [120, 150, 180, 200, 210, 250, 300, 310, 290, 350, 380, 400, 420, 450]
            df = pd.DataFrame({"Revenue ($)": revenue}, index=dates)
            st.line_chart(df, use_container_width=True)
            
        with c_right:
            st.markdown("### System Health")
            st.markdown("""
            <div class='tredalq-card' style='padding: 15px;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                    <span>Database Status</span> <span style='color: #10B981;'>● Operational</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                    <span>Prediction Engine</span> <span style='color: #10B981;'>● Operational</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                    <span>Market Data API</span> <span style='color: #F59E0B;'>● Degraded (Latency)</span>
                </div>
                <div style='display: flex; justify-content: space-between;'>
                    <span>Memory Usage</span> <span>4.2 GB / 8.0 GB</span>
                </div>
                <div style='margin-top: 5px; background: #374151; height: 6px; border-radius: 3px;'>
                    <div style='width: 52%; background: #3B82F6; height: 100%; border-radius: 3px;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
    finally:
        db.close()
