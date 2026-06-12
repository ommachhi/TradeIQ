import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import Alert

def render(user: dict):
    st.title("Price & Prediction Alerts")
    st.caption("Never miss an opportunity with real-time market notifications.")
    
    db = SessionLocal()
    try:
        alerts = db.query(Alert).filter(Alert.user_id == user["id"]).all()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### Active Alerts")
            if not alerts:
                st.info("No active alerts. Create one to get notified.")
            else:
                data = []
                for a in alerts:
                    data.append({
                        "Symbol": a.symbol,
                        "Type": a.alert_type,
                        "Target Price": f"${a.target_price:.2f}",
                        "Status": a.status,
                        "Created": a.created_at.strftime("%Y-%m-%d")
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True)
                
        with c2:
            st.markdown("### Create New Alert")
            with st.form("create_alert_form"):
                symbol = st.text_input("Symbol (e.g., TSLA)")
                alert_type = st.selectbox("Alert Type", ["Price Above", "Price Below", "Stop-Loss", "Target Reached", "Prediction Change"])
                target_price = st.number_input("Trigger Price", min_value=0.0)
                
                # Mock email setting
                notify_email = st.checkbox("Email Notification", value=True)
                
                if st.form_submit_button("Set Alert"):
                    if symbol and target_price > 0:
                        new_alert = Alert(
                            user_id=user["id"],
                            symbol=symbol.upper(),
                            alert_type=alert_type,
                            target_price=target_price,
                            status="Active"
                        )
                        db.add(new_alert)
                        db.commit()
                        st.success(f"Alert set for {symbol.upper()} at ${target_price:.2f}")
                        st.rerun()
                    else:
                        st.error("Valid Symbol and Price are required.")
    finally:
        db.close()
