import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import pickle
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# --- SYMBOLS LOGIC (Inlined for reliability) ---
SYMBOL_PATTERN = re.compile(r"^(?:[A-Z]{1,10}|[A-Z]{1,10}\.(?:NS|BO))$")

def is_valid_stock_symbol_format(symbol: str) -> bool:
    cleaned = (symbol or "").strip().upper()
    return bool(cleaned and SYMBOL_PATTERN.fullmatch(cleaned))

def _fetch_history(candidate: str, period: str):
    try:
        ticker = yf.Ticker(candidate)
        hist = ticker.history(period=period)
        if hist is not None and not hist.empty:
            return hist
    except:
        pass
    return None

def resolve_symbol_with_history(symbol: str, period: str = "2y"):
    cleaned = (symbol or "").strip().upper()
    if not is_valid_stock_symbol_format(cleaned):
        # Try a few common variants if not exactly matched
        candidates = [cleaned, f"{cleaned}.NS", f"{cleaned}.BO"]
    else:
        candidates = [cleaned] if "." in cleaned else [cleaned, f"{cleaned}.NS", f"{cleaned}.BO"]
    
    for candidate in candidates:
        hist = _fetch_history(candidate, period)
        if hist is not None and not hist.empty:
            return candidate, hist
    return None, None

# --- PREDICTOR LOGIC (Inlined for reliability) ---
def get_prediction(df, symbol=None):
    closes = df['Close'].dropna()
    if closes.empty: return None
    
    current_price = float(closes.iloc[-1])
    ma_5 = float(closes.rolling(window=5).mean().iloc[-1]) if len(closes) >= 5 else current_price
    ma_10 = float(closes.rolling(window=10).mean().iloc[-1]) if len(closes) >= 10 else current_price
    ma_20 = float(closes.rolling(window=20).mean().iloc[-1]) if len(closes) >= 20 else current_price

    # Trend Logic
    if ma_5 > ma_10 > ma_20: trend, rec = 'Uptrend', 'BUY'
    elif ma_5 < ma_10 < ma_20: trend, rec = 'Downtrend', 'SELL'
    else: trend, rec = 'Sideways', 'HOLD'

    # Simple forecast logic (similar to predictor.py)
    momentum_5 = 0.0
    if len(closes) >= 6 and closes.iloc[-6] != 0:
        momentum_5 = float((closes.iloc[-1] - closes.iloc[-6]) / closes.iloc[-6])
    
    daily_return = 0.0
    if len(closes) >= 2 and closes.iloc[-2] != 0:
        daily_return = float((closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2])

    momentum_target = current_price * (1.0 + 0.6 * momentum_5 + 0.4 * daily_return)
    predicted_price = (0.45 * current_price + 0.25 * ma_5 + 0.15 * ma_10 + 0.10 * ma_20 + 0.05 * momentum_target)
    
    # Refine recommendation based on predicted change
    change_pct = ((predicted_price - current_price) / current_price) * 100
    if change_pct > 2.0: rec = 'BUY'
    elif change_pct < -2.0: rec = 'SELL'
    
    return {
        'symbol': symbol,
        'current_price': current_price,
        'predicted_price': predicted_price,
        'trend': trend,
        'recommendation': rec,
        'change_percent': change_pct,
        'confidence': 'HIGH' if abs(change_pct) < 5 else 'MEDIUM',
    }

# --- PAGE CONFIG ---
st.set_page_config(page_title="TradeIQ | AI Stock Analysis", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .recommendation-buy { color: #00ff00; font-weight: bold; font-size: 24px; }
    .recommendation-sell { color: #ff0000; font-weight: bold; font-size: 24px; }
    .recommendation-hold { color: #ffff00; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# --- APP UI ---
st.sidebar.title("🚀 TradeIQ AI")
st.sidebar.info("Analyze stocks with real-time AI predictions.")
symbol_input = st.sidebar.text_input("Enter Stock Symbol", value="RELIANCE")
period_select = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

st.title("📈 TradeIQ Stock Dashboard")

with st.spinner("Fetching market data..."):
    resolved_symbol, df = resolve_symbol_with_history(symbol_input, period=period_select)

if df is not None:
    pred = get_prediction(df, resolved_symbol)
    
    st.markdown(f"### Analysis for **{resolved_symbol}**")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Current", f"₹{pred['current_price']:.2f}")
    with c2: st.metric("Predicted", f"₹{pred['predicted_price']:.2f}", f"{pred['change_percent']:.2f}%")
    with c3: st.metric("Trend", pred['trend'])
    with c4:
        st.markdown(f"**Signal:** <span class='recommendation-{pred['recommendation'].lower()}'>{pred['recommendation']}</span>", unsafe_allow_html=True)

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    t1, t2 = st.tabs(["📊 Stats", "📑 Data"])
    with t1:
        st.table(pd.DataFrame({
            "Indicator": ["52W High", "52W Low", "Avg Volume"],
            "Value": [f"₹{df['High'].max():.2f}", f"₹{df['Low'].min():.2f}", f"{int(df['Volume'].mean()):,}"]
        }))
    with t2:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.error(f"Could not find stock: {symbol_input}. Try RELIANCE, TCS, or AAPL.")
