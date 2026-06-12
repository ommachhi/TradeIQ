import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import Portfolio, Trade, Watchlist
from services.market_data import get_all_quotes
from utils.formatting import format_inr, signal_badge_html
from utils.charts import line_chart_portfolio
import yfinance as yf

@st.cache_data(ttl=300)
def fetch_current_price(symbol: str) -> float:
    try:
        t = yf.Ticker(symbol)
        price = t.info.get('regularMarketPrice') or t.info.get('currentPrice')
        return price if price else 0.0
    except:
        return 0.0

def render(user: dict):
    st.title("User Dashboard")
    st.caption("Live portfolio intelligence, price action, and the latest model-driven signals.")
    
    db = SessionLocal()
    try:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user["id"]).all()
        watchlists = db.query(Watchlist).filter(Watchlist.user_id == user["id"]).all()
        
        total_investment = 0
        current_value = 0
        for p in portfolio:
            total_investment += (p.quantity * p.avg_buy_price)
            cp = fetch_current_price(p.symbol)
            if cp > 0:
                current_value += (p.quantity * cp)
            else:
                current_value += (p.quantity * p.avg_buy_price)
                
        todays_pnl = current_value - total_investment
        pnl_pct = (todays_pnl / total_investment * 100) if total_investment else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Portfolio Value", f"${current_value:.2f}", f"{pnl_pct:.2f}%")
        c2.metric("Total P&L", f"${todays_pnl:.2f}", f"{pnl_pct:.2f}%")
        c3.metric("Active Positions", str(len(portfolio)))
        c4.metric("Watchlisted", str(len(watchlists)))
        
        st.markdown("### Portfolio Performance (30 Days)")
        # Mock 30 day data for charts if no real history exists
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30)
        start_val = current_value if current_value > 0 else 10000
        vals = [start_val * (1 + (i*0.002)) for i in range(30)]
        df_mock = pd.DataFrame({"value": vals}, index=dates)
        st.plotly_chart(line_chart_portfolio(df_mock), use_container_width=True)
        
        st.markdown("### Recent AI Signals")
        # Fetch mock signals for now
        top5 = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
        signals_data = []
        import random
        for s in top5:
            sig = random.choice(["BUY", "SELL", "HOLD"])
            cp = fetch_current_price(s) or 150.0
            t = cp * 1.05 if sig == "BUY" else cp * 0.95
            sl = cp * 0.98 if sig == "BUY" else cp * 1.02
            signals_data.append({
                "Symbol": s,
                "Signal": signal_badge_html(sig),
                "Target Price": f"${t:.2f}" if sig != "HOLD" else "-",
                "Stop Loss": f"${sl:.2f}" if sig != "HOLD" else "-",
                "Confidence": f"{random.randint(70, 95)}%",
                "Generated At": "Today"
            })
        
        st.markdown(pd.DataFrame(signals_data).to_html(escape=False, index=False), unsafe_allow_html=True)
        
    finally:
        db.close()
