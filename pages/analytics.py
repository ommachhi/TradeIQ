import streamlit as st
from utils.charts import pie_chart_signals, monthly_pnl_chart

def render(user: dict):
    st.title("Analytics")
    st.caption("Deep performance analytics and trade insights.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(pie_chart_signals(58, 42), use_container_width=True)
    with c2:
        st.plotly_chart(monthly_pnl_chart(["Jan", "Feb", "Mar", "Apr", "May", "Jun"], [-8900, 15400, 42300, 21500, -3200, 18700]), use_container_width=True)
        
    st.markdown("### Statistics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", "124")
    c2.metric("Profitable", "84 (67.7%)")
    c3.metric("Avg Profit", "₹1,340")
    c4.metric("Max Drawdown", "-8.2%")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sharpe Ratio", "1.84")
    c2.metric("Avg Hold", "2.3 days")
    c3.metric("Best Month", "Mar +₹42,300")
    c4.metric("Worst Month", "Jan -₹8,900")
