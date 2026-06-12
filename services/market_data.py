import yfinance as yf
import pandas as pd
import streamlit as st
import time
from tenacity import retry, stop_after_attempt, wait_exponential

INDIAN_STOCKS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "BAJFINANCE.NS": "Bajaj Finance",
    "WIPRO.NS": "Wipro Ltd",
    "TATAMOTORS.NS": "Tata Motors",
    "SUNPHARMA.NS": "Sun Pharmaceutical",
    "MARUTI.NS": "Maruti Suzuki",
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_stock_quote(symbol: str) -> dict:
    tkr = yf.Ticker(symbol)
    info = tkr.fast_info
    
    price = info.last_price
    prev_close = info.previous_close
    change = price - prev_close
    change_pct = (change / prev_close) * 100 if prev_close else 0
    volume = getattr(info, 'last_volume', 0)
    
    vol_str = f"{volume/1000000:.1f}M" if volume >= 1000000 else str(volume)
    
    return {
        "symbol": symbol,
        "company": INDIAN_STOCKS.get(symbol, symbol),
        "price": price,
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "volume": vol_str,
        "week52_high": getattr(info, 'year_high', 0),
        "week52_low": getattr(info, 'year_low', 0)
    }

@st.cache_data(ttl=300)
def get_all_quotes() -> list:
    quotes = []
    for sym in INDIAN_STOCKS.keys():
        try:
            q = get_stock_quote(sym)
            if q:
                quotes.append(q)
        except Exception as e:
            pass # Skip failed quotes after retries
    return quotes

@st.cache_data(ttl=3600)
@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
def get_historical_data(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    tkr = yf.Ticker(symbol)
    df = tkr.history(period=period, interval=interval)
    if df.empty:
        raise ValueError("Empty DataFrame returned")
    return df

def get_intraday_data(symbol: str) -> pd.DataFrame:
    try:
        tkr = yf.Ticker(symbol)
        df = tkr.history(period="1d", interval="5m")
        return df
    except:
        return pd.DataFrame()
