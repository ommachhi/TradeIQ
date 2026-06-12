import streamlit as st
import pandas as pd
import numpy as np

def render(user: dict):
    st.title("Platform Analytics")
    st.caption("Detailed breakdown of user activity, predictions, and engagement.")
    
    st.markdown("### User Engagement Trends")
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30)
    data = pd.DataFrame({
        "Active Users": np.random.randint(100, 500, size=30),
        "Predictions Generated": np.random.randint(500, 2000, size=30)
    }, index=dates)
    st.line_chart(data, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Top Symbols Searched")
        symbol_data = pd.DataFrame({
            "Symbol": ["RELIANCE.NS", "AAPL", "TSLA", "HDFCBANK.NS", "MSFT"],
            "Queries": [1420, 1150, 980, 850, 720]
        })
        st.bar_chart(symbol_data.set_index("Symbol"), use_container_width=True)
        
    with c2:
        st.markdown("### User Demographics")
        demo_data = pd.DataFrame({
            "Region": ["North America", "India", "Europe", "Asia (Other)"],
            "Users": [450, 1200, 300, 150]
        })
        st.bar_chart(demo_data.set_index("Region"), use_container_width=True)
