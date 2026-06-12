import streamlit as st
import pandas as pd
from services.market_data import get_all_quotes, get_historical_data
from utils.formatting import format_inr, format_change
from utils.charts import indicator_chart, rsi_chart, macd_chart

def render(user: dict):
    st.title("Market")
    st.caption("Global and Indian market overview.")
    
    search_q = st.text_input("🔍 Search symbol or company")
    
    with st.spinner("Fetching market data..."):
        quotes = get_all_quotes()
        
    if not quotes:
        st.warning("Could not fetch live data.")
        return
        
    df = pd.DataFrame(quotes)
    if search_q:
        df = df[df['symbol'].str.contains(search_q, case=False) | df['company'].str.contains(search_q, case=False)]
        
    def style_table(row):
        return ['color: #22c55e' if v > 0 else 'color: #ef4444' if v < 0 else '' for v in row]

    display_df = pd.DataFrame({
        "Symbol": df['symbol'],
        "Company": df['company'],
        "Price": df['price'].apply(format_inr),
        "Change": df['change'].apply(lambda x: f"{'+' if x>0 else ''}{x:.2f}"),
        "Change%": df['change_pct'].apply(lambda x: f"{'+' if x>0 else ''}{x:.2f}%"),
        "Volume": df['volume'],
        "52W High": df['week52_high'].apply(format_inr),
        "52W Low": df['week52_low'].apply(format_inr)
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Select a stock for detailed view")
    selected_sym = st.selectbox("Symbol", options=df['symbol'].tolist())
    
    if selected_sym:
        try:
            hist = get_historical_data(selected_sym)
            if hist is None or hist.empty:
                st.warning("Could not fetch historical data.")
            else:
                st.plotly_chart(indicator_chart(hist, selected_sym), use_container_width=True)
            t1, t2, t3 = st.tabs(["RSI", "MACD", "Info"])
            with t1:
                from services.indicators import rsi
                st.plotly_chart(rsi_chart(rsi(hist)), use_container_width=True)
            with t2:
                from services.indicators import macd
                st.plotly_chart(macd_chart(macd(hist)), use_container_width=True)
            with t3:
                q = next(x for x in quotes if x["symbol"] == selected_sym)
                st.write(f"**Company:** {q['company']}")
                st.write(f"**Price:** {format_inr(q['price'])}")
                st.write(f"**52W Range:** {format_inr(q['week52_low'])} - {format_inr(q['week52_high'])}")
                st.write(f"**Volume:** {q['volume']}")
        except Exception as e:
            st.error(f"Error loading chart data: {str(e)}")
