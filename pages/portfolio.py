import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import Portfolio, Trade
import yfinance as yf

def fetch_current_price(symbol: str) -> float:
    try:
        t = yf.Ticker(symbol)
        price = t.info.get('regularMarketPrice') or t.info.get('currentPrice')
        return price if price else 0.0
    except:
        return 0.0

def render(user: dict):
    st.title("My Portfolio")
    st.caption("Manage your holdings and track performance in real-time.")
    
    db = SessionLocal()
    try:
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user["id"]).all()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### Active Positions")
            if not portfolios:
                st.info("Your portfolio is empty. Add a position to get started.")
            else:
                data = []
                total_value = 0
                total_cost = 0
                for p in portfolios:
                    cp = fetch_current_price(p.symbol)
                    val = cp * p.quantity if cp else p.avg_buy_price * p.quantity
                    cost = p.avg_buy_price * p.quantity
                    pnl = val - cost
                    pnl_pct = (pnl / cost * 100) if cost else 0
                    
                    total_value += val
                    total_cost += cost
                    
                    data.append({
                        "Symbol": p.symbol,
                        "Quantity": p.quantity,
                        "Avg Price": f"${p.avg_buy_price:.2f}",
                        "Current Price": f"${cp:.2f}" if cp else "N/A",
                        "Total Value": f"${val:.2f}",
                        "P/L": f"<span class='{'metric-positive' if pnl >= 0 else 'metric-negative'}'>${pnl:.2f} ({pnl_pct:.2f}%)</span>"
                    })
                
                st.markdown(pd.DataFrame(data).to_html(escape=False, index=False), unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### Summary")
                total_pnl = total_value - total_cost
                total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Investment", f"${total_cost:.2f}")
                m2.metric("Current Value", f"${total_value:.2f}")
                m3.metric("Total P/L", f"${total_pnl:.2f}", f"{total_pnl_pct:.2f}%")
                
        with c2:
            st.markdown("### Add New Position")
            with st.form("add_position_form"):
                symbol = st.text_input("Symbol (e.g., AAPL)")
                quantity = st.number_input("Quantity", min_value=1, step=1)
                buy_price = st.number_input("Average Buy Price", min_value=0.01, step=0.1)
                sector = st.text_input("Sector (Optional)")
                
                if st.form_submit_button("Add to Portfolio"):
                    if symbol and quantity and buy_price:
                        existing = db.query(Portfolio).filter(Portfolio.user_id == user["id"], Portfolio.symbol == symbol.upper()).first()
                        if existing:
                            # Update existing
                            total_qty = existing.quantity + quantity
                            avg_p = ((existing.quantity * existing.avg_buy_price) + (quantity * buy_price)) / total_qty
                            existing.quantity = total_qty
                            existing.avg_buy_price = avg_p
                        else:
                            new_pos = Portfolio(
                                user_id=user["id"],
                                symbol=symbol.upper(),
                                quantity=quantity,
                                avg_buy_price=buy_price,
                                sector=sector
                            )
                            db.add(new_pos)
                        db.commit()
                        st.success(f"Added {quantity} shares of {symbol.upper()}")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields.")
    finally:
        db.close()
