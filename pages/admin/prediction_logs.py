import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import PredictionLog, User

def render(user: dict):
    st.title("Prediction Logs")
    st.caption("Monitor AI model predictions across all users.")
    
    db = SessionLocal()
    try:
        logs = db.query(PredictionLog, User).join(User, PredictionLog.user_id == User.id).order_by(PredictionLog.prediction_date.desc()).limit(100).all()
        
        if not logs:
            st.info("No prediction logs found.")
        else:
            data = []
            for log, u in logs:
                data.append({
                    "Date": log.prediction_date.strftime("%Y-%m-%d %H:%M"),
                    "User": u.email,
                    "Symbol": log.symbol,
                    "Recommendation": log.recommendation,
                    "Confidence": f"{log.confidence:.1f}%",
                    "Risk Level": log.risk_level
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
    finally:
        db.close()
