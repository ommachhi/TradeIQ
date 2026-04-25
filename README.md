# TradeIQ AI - Professional Stock SaaS

TradeIQ AI is a high-performance, Streamlit-powered SaaS application for stock market analysis, AI-driven predictions, and portfolio management.

## 🚀 Key Features
- **AI Predictions**: Real-time stock forecasting using machine learning.
- **Secure Authentication**: User registration and login with bcrypt password hashing.
- **Interactive Charts**: Professional candlestick charts with technical indicators.
- **Market Sentiment**: Trend detection and confidence scoring.
- **Portfolio Tracking**: (Coming Soon) Manage your assets and watchlists.

## 🛠️ Tech Stack
- **Frontend/UI**: Streamlit
- **Backend**: Python
- **Database**: SQLAlchemy (SQLite for local, PostgreSQL ready)
- **Data Source**: Yahoo Finance (yfinance)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ommachhi/TradeIQ.git
   cd TradeIQ
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🌐 Deployment to Streamlit Cloud
1. Push your code to GitHub.
2. Connect your repo to [Streamlit Cloud](https://share.streamlit.io).
3. Set the Main file path to `streamlit_app.py`.
4. Deploy!

---
Developed by TradeIQ Team
