import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from database.db import SessionLocal
from database.models import PredictionLog

def fetch_historical_data(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1mo")
        return df
    except:
        return None

def mock_prediction(df):
    # Simulated ML prediction logic
    latest_close = df['Close'].iloc[-1]
    trend = df['Close'].iloc[-1] - df['Close'].iloc[0]
    
    if trend > 0:
        recommendation = "BUY"
        confidence = np.random.uniform(70, 95)
        risk = "Medium"
        predicted = latest_close * 1.05
    elif trend < 0:
        recommendation = "SELL"
        confidence = np.random.uniform(60, 85)
        risk = "High"
        predicted = latest_close * 0.95
    else:
        recommendation = "HOLD"
        confidence = np.random.uniform(50, 70)
        risk = "Low"
        predicted = latest_close
        
    return recommendation, confidence, risk, predicted, latest_close

def render(user: dict):
    st.title("AI Prediction Engine")
    st.caption("Advanced ML models to forecast stock movements with confidence intervals.")
    
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, RELIANCE.NS)", value="AAPL").upper()
    
    if st.button("Generate Prediction"):
        if not symbol:
            st.error("Please enter a valid symbol.")
            return
            
        with st.spinner("Analyzing historical data and running AI models..."):
            df = fetch_historical_data(symbol)
            if df is None or df.empty:
                st.error("Could not fetch data. Please check the symbol and try again.")
                return
            
            rec, conf, risk, pred, current = mock_prediction(df)
            
            # Save to DB
            db = SessionLocal()
            try:
                log = PredictionLog(
                    user_id=user["id"],
                    symbol=symbol,
                    recommendation=rec,
                    confidence=conf,
                    risk_level=risk,
                    predicted_price=pred
                )
                db.add(log)
                db.commit()
            except Exception as e:
                st.warning(f"Failed to log prediction to database: {e}")
            finally:
                db.close()
                
            # Display results
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Current Price", f"${current:.2f}")
            
            if rec == "BUY":
                rec_html = "<span class='badge-buy'>BUY</span>"
            elif rec == "SELL":
                rec_html = "<span class='badge-sell'>SELL</span>"
            else:
                rec_html = "<span class='badge-hold'>HOLD</span>"
                
            c2.markdown(f"**Recommendation**<br>{rec_html}", unsafe_allow_html=True)
            c3.metric("Confidence", f"{conf:.1f}%")
            c4.metric("Risk Level", risk)
            
            st.markdown(f"**Target Predicted Price (30 Days):** ${pred:.2f}")
            
            # Chart
            st.markdown("### Historical Comparison")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Historical Close', line=dict(color='#3B82F6')))
            
            # Predict next 5 days mock
            future_dates = pd.date_range(start=df.index[-1], periods=6, freq='D')[1:]
            future_prices = np.linspace(current, pred, 5)
            
            fig.add_trace(go.Scatter(x=future_dates, y=future_prices, mode='lines+markers', name='AI Forecast', line=dict(color='#10B981', dash='dash')))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E2E8F0'),
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(gridcolor='#1F2937'),
                yaxis=dict(gridcolor='#1F2937')
            )
            st.plotly_chart(fig, use_container_width=True)
