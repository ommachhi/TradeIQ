# TradeIQ AI - Professional Stock SaaS

TradeIQ AI is a high-performance, Streamlit-powered SaaS application for stock market analysis, AI-driven predictions, and portfolio management.

## 🚀 Key Features
- **AI Predictions**: Real-time stock forecasting using machine learning with confidence scores.
- **Strict RBAC & Admin Panel**: Secure routing for Users and Admins. Manage users, monitor AI models, view audit logs, and more.
- **Secure Authentication**: User registration and login with bcrypt password hashing, JWT validation, and password strength checks.
- **Interactive Dashboards**: Professional real-time portfolio dashboards, live market data, and interactive Plotly charts.
- **Market Alerts**: Set price, stop-loss, and target alerts.
- **Portfolio Tracking**: Manage your assets, calculate P/L dynamically, and manage watchlists securely.

## 🔑 Admin Credentials (Seeded)
To access the Admin Dashboards and manage the platform, use the following default credentials:
- **Email:** `admin@tredalq.com`
- **Password:** `Admin@123!`

*(Make sure to change the admin password in production!)*

## 🛠️ Tech Stack
- **Frontend/UI**: Streamlit
- **Backend**: Python 3.13
- **Database**: SQLite / SQLAlchemy ORM (PostgreSQL ready)
- **Data Source**: Yahoo Finance (yfinance)
- **Security**: PyJWT, bcrypt

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

4. **Initialize the Database**:
   ```bash
   python reset_db.py
   python insert_admin.py
   ```

5. **Run the App**:
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
