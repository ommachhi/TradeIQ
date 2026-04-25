import streamlit as st
import streamlit_authenticator as stauth
from database.connection import init_db, SessionLocal
from services.auth_service import AuthService
from database.models import User
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import re

# Initialize Database
init_db()

# --- AUTHENTICATION LOGIC ---
def login_ui():
    st.title("🔐 TradeIQ SaaS Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                db = SessionLocal()
                user = AuthService.authenticate_user(db, username, password)
                db.close()
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user_id"] = user.id
                    st.session_state["username"] = user.username
                    st.session_state["role"] = user.role
                    st.success(f"Welcome back, {user.username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("New Username")
            new_email = st.text_input("Email")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            reg_submitted = st.form_submit_button("Register")
            
            if reg_submitted:
                if new_pass != confirm_pass:
                    st.error("Passwords do not match")
                else:
                    db = SessionLocal()
                    success, result = AuthService.register_user(db, new_user, new_email, new_pass)
                    db.close()
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Error: {result}")

# --- DASHBOARD LOGIC (Restored from previous version) ---
def main_dashboard():
    st.sidebar.title(f"👋 Hello, {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # Original Dashboard Code...
    st.title("📈 TradeIQ AI Terminal Pro")
    symbol_input = st.sidebar.text_input("Enter Stock Symbol", value="RELIANCE")
    period_select = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

    # (Previous Dashboard Implementation goes here)
    st.info("SaaS Dashboard loaded. You are now logged in securely.")
    
    # Placeholder for the rest of the logic
    from streamlit_app_core import render_dashboard
    render_dashboard(symbol_input, period_select)

# --- MAIN ENTRY POINT ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_ui()
else:
    main_dashboard()
