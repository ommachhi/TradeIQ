import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add backend to path to reuse logic
backend_path = os.path.join(os.getcwd(), 'tradeiq_backend')
sys.path.append(backend_path)

try:
    from prediction.symbols import resolve_symbol_with_history
    from ai.predictor import make_prediction
    HAS_BACKEND = True
except ImportError as e:
    st.error(f"Backend modules not found: {e}")
    HAS_BACKEND = False

# Page Configuration
st.set_page_config(
    page_title="TradeIQ | AI Stock Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .recommendation-buy { color: #00ff00; font-weight: bold; font-size: 24px; }
    .recommendation-sell { color: #ff0000; font-weight: bold; font-size: 24px; }
    .recommendation-hold { color: #ffff00; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🚀 TradeIQ Pro")
st.sidebar.markdown("---")
symbol_input = st.sidebar.text_input("Enter Stock Symbol", value="RELIANCE")
period_select = st.sidebar.selectbox("Select History Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

st.sidebar.markdown("---")
st.sidebar.info("""
**Advanced Stock Analysis**
- Real-time resolution (NSE/BSE/US)
- Technical Indicator Analysis
- AI-Powered Price Prediction
""")

# Main Content
st.title("📈 TradeIQ AI Stock Dashboard")

if not HAS_BACKEND:
    st.warning("Running in standalone mode. Backend logic is limited.")

# Fetch and Predict
with st.spinner("Analyzing market data..."):
    if HAS_BACKEND:
        try:
            resolved_symbol, df = resolve_symbol_with_history(symbol_input, period=period_select)
            if df is not None and not df.empty:
                # Prepare data for predictor
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
                pred = None
        except Exception as e:
            st.error(f"Error: {e}")
            pred = None
    else:
        # Fallback basic logic
        resolved_symbol = symbol_input
        df = yf.Ticker(symbol_input).history(period=period_select)
        pred = None # Basic fallback would go here

if pred and df is not None:
    st.markdown(f"### Analysis for **{resolved_symbol}**")
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"₹{pred['current_price']:.2f}", f"{df['Close'].pct_change().iloc[-1]*100:.2f}%")
    with col2:
        st.metric("AI Predicted", f"₹{pred['predicted_price']:.2f}", f"{pred['change_percent']:.2f}%")
    with col3:
        st.metric("Market Trend", pred['trend'])
    with col4:
        rec = pred['recommendation']
        st.markdown(f"**Signal:** <span class='recommendation-{rec.lower()}'>{rec}</span>", unsafe_allow_html=True)

    # Main Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price'
    ))
    
    # Add MAs if available
    if 'technical_indicators' in pred:
        tis = pred['technical_indicators']
        # Note: These are single values, we might want to plot the lines
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], name='MA 5', line=dict(color='yellow', width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA 20', line=dict(color='cyan', width=1.5)))

    fig.update_layout(
        template="plotly_dark", height=600,
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Analysis
    t1, t2, t3 = st.tabs(["📊 Technicals", "🤖 AI Insight", "📑 Historical Data"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.write("#### Price Statistics")
            st.table(pd.DataFrame({
                "Metric": ["Day High", "Day Low", "52W High", "52W Low", "Avg Volume"],
                "Value": [
                    f"₹{df['High'].iloc[-1]:.2f}",
                    f"₹{df['Low'].iloc[-1]:.2f}",
                    f"₹{df['High'].max():.2f}",
                    f"₹{df['Low'].min():.2f}",
                    f"{int(df['Volume'].mean()):,}"
                ]
            }))
        with c2:
            st.write("#### Technical Indicators")
            if 'technical_indicators' in pred:
                ti_df = pd.DataFrame([
                    {"Indicator": "MA 5", "Value": f"{pred['technical_indicators'].get('ma_5', 0):.2f}"},
                    {"Indicator": "MA 10", "Value": f"{pred['technical_indicators'].get('ma_10', 0):.2f}"},
                    {"Indicator": "MA 20", "Value": f"{pred['technical_indicators'].get('ma_20', 0):.2f}"},
                ])
                st.table(ti_df)

    with t2:
        st.write("#### AI Prediction Reasoning")
        conf_color = "green" if pred['confidence'] == "HIGH" else "orange" if pred['confidence'] == "MEDIUM" else "red"
        st.markdown(f"**Confidence Level:** <span style='color:{conf_color}'>{pred['confidence']}</span>", unsafe_allow_html=True)
        
        if not pred.get('is_reliable', True):
            st.warning(f"⚠️ {pred.get('warning', 'Unreliable Prediction')}")
        
        st.info(f"""
        Our AI model analyzed the recent volatility and price action. 
        The expected change for the next session is **{pred['change_percent']:.2f}%**.
        This prediction is based on a blend of Random Forest regression and Moving Average convergence.
        """)

    with t3:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

elif symbol_input:
    st.error(f"Could not find data for '{symbol_input}'. Please try a different symbol (e.g. AAPL, RELIANCE, TCS).")

# Footer
st.markdown("---")
st.caption("TradeIQ AI Terminal | Data provided by Yahoo Finance | For educational purposes only.")
