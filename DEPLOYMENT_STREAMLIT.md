# Streamlit Deployment Guide for TradeIQ

This guide explains how to deploy the TradeIQ prediction dashboard to Streamlit Cloud.

## Prerequisites
1. A GitHub account.
2. The project code pushed to a GitHub repository.
3. A Streamlit Cloud account (sign up at [streamlit.io/cloud](https://streamlit.io/cloud)).

## Step-by-Step Deployment

### 1. Prepare your Repository
Ensure the following files are in the root of your GitHub repository:
- `streamlit_app.py`: The main entry point for the Streamlit dashboard.
- `requirements.txt`: Contains all necessary Python dependencies (including `streamlit`, `plotly`, `yfinance`, etc.).
- `tradeiq_backend/`: The backend folder (if needed for model loading).

### 2. Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Click **"New app"**.
3. Select your GitHub repository, branch (e.g., `main`), and the main file path: `streamlit_app.py`.

### 3. Deploy
1. Click **"Deploy!"**.
2. Streamlit will start building the environment and installing dependencies from `requirements.txt`.
3. Once finished, your app will be live at a URL like `https://tradeiq-analysis.streamlit.app`.

## Local Running Instructions
If you want to run the dashboard locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## Troubleshooting
- **Missing Dependencies**: If the app fails to start, check the logs in Streamlit Cloud. Ensure all packages used in `streamlit_app.py` are listed in `requirements.txt`.
- **Model Loading**: If you are using a saved model (like `model.pkl`), ensure the path in `streamlit_app.py` or your predictor logic correctly points to the file in the repository.
