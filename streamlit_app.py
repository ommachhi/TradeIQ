import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import traceback

# Add backend to path to reuse logic
try:
    # Try multiple ways to find the backend
    possible_paths = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'tradeiq_backend'),
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tradeiq_backend')
    ]
    
    for p in possible_paths:
        if p not in sys.path:
            sys.path.append(p)
            
    # Try importing
    from prediction.symbols import resolve_symbol_with_history
    from ai.predictor import make_prediction
    HAS_BACKEND = True
except Exception as e:
    st.error(f"Backend Initialization Error: {e}")
    st.code(traceback.format_exc())
    HAS_BACKEND = False

# Page Configuration
st.set_page_config(
    page_title="TradeIQ | AI Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .recommendation-buy { color: #00ff00; font-weight: bold; font-size: 24px; }
    .recommendation-sell { color: #ff0000; font-weight: bold; font-size: 24px; }
    .recommendation-hold { color: #ffff00; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🚀 TradeIQ AI")
st.sidebar.markdown("---")
symbol_input = st.sidebar.text_input("Enter Stock Symbol", value="RELIANCE")
period_select = st.sidebar.selectbox("Select History Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

st.sidebar.markdown("---")
st.sidebar.info("Analyze stocks with real-time AI predictions.")

# Main Content
st.title("📈 TradeIQ Stock Dashboard")

if not HAS_BACKEND:
    st.stop()

# Fetch and Predict
with st.spinner("Analyzing market data..."):
    try:
        resolved_symbol, df = resolve_symbol_with_history(symbol_input, period=period_select)
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            input_data = {
                'symbol': resolved_symbol,
                'open': latest['Open'],
                'high': latest['High'],
                'low': latest['Low'],
                'close': latest['Close'],
                'volume': latest['Volume']
            }
            pred = make_prediction(input_data)
        else:
            st.error(f"Could not fetch data for {symbol_input}")
            st.stop()
    except Exception as e:
        st.error(f"Prediction Error: {e}")
        st.code(traceback.format_exc())
        st.stop()

if pred:
    st.markdown(f"### Analysis for **{resolved_symbol}**")
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Current", f"₹{pred['current_price']:.2f}")
    with c2: st.metric("Predicted", f"₹{pred['predicted_price']:.2f}", f"{pred['change_percent']:.2f}%")
    with c3: st.metric("Trend", pred['trend'])
    with c4:
        rec = pred['recommendation']
        st.markdown(f"**Signal:** <span class='recommendation-{rec.lower()}'>{rec}</span>", unsafe_allow_html=True)

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Details
    t1, t2 = st.tabs(["📊 Technicals", "📑 Data"])
    with t1:
        st.table(pd.DataFrame({
            "Indicator": ["52W High", "52W Low", "Confidence"],
            "Value": [f"₹{df['High'].max():.2f}", f"₹{df['Low'].min():.2f}", pred['confidence']]
        }))
    with t2:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
