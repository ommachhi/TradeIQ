import streamlit as st
from database.db import init_db
from auth.auth import register_user, login_user
from utils.security import verify_jwt

st.set_page_config(page_title="TREDALQ AI Platform", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* Modern SaaS Styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp { background-color: #0B0F19; color: #E2E8F0; }
section[data-testid="stSidebar"] { 
    background-color: #111827; 
    border-right: 1px solid #1F2937; 
}
.tredalq-card { 
    background: linear-gradient(145deg, #1F2937 0%, #111827 100%); 
    border: 1px solid #374151; 
    border-radius: 12px; 
    padding: 24px; 
    margin-bottom: 20px; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease-in-out;
}
.tredalq-card:hover {
    transform: translateY(-2px);
    border-color: #4B5563;
}
.metric-positive { color: #10B981; font-weight: 600; }
.metric-negative { color: #EF4444; font-weight: 600; }
.badge-buy { background: rgba(16, 185, 129, 0.2); color: #10B981; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-sell { background: rgba(239, 68, 68, 0.2); color: #EF4444; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-hold { background: rgba(245, 158, 11, 0.2); color: #F59E0B; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; border: 1px solid rgba(245, 158, 11, 0.3); }
.stButton > button { 
    background: linear-gradient(to right, #4F46E5, #3B82F6); 
    color: white; 
    border: none; 
    border-radius: 8px; 
    padding: 10px 24px; 
    font-weight: 600; 
    width: 100%;
    transition: all 0.3s ease;
}
.stButton > button:hover { 
    background: linear-gradient(to right, #4338CA, #2563EB); 
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.stTextInput > div > div > input, .stSelectbox > div > div, .stNumberInput > div > div > input { 
    background: #1F2937 !important; 
    border: 1px solid #374151 !important; 
    color: #F9FAFB !important; 
    border-radius: 8px !important; 
    padding: 12px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}
.auth-container { max-width: 400px; margin: 0 auto; padding-top: 50px; }
.logo-title { font-size: 32px; font-weight: 800; background: -webkit-linear-gradient(#3B82F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
/* Skeleton loader */
.skeleton {
    animation: skeleton-loading 1s linear infinite alternate;
    border-radius: 4px;
    height: 20px;
    margin-bottom: 8px;
}
@keyframes skeleton-loading {
    0% { background-color: #1F2937; }
    100% { background-color: #374151; }
}
</style>
""", unsafe_allow_html=True)

init_db()

if "user" not in st.session_state:
    st.session_state["user"] = None
if "auth_view" not in st.session_state:
    st.session_state["auth_view"] = "login"

def check_auth():
    user = st.session_state.get("user")
    if user and user.get("token"):
        payload = verify_jwt(user["token"])
        if "error" in payload:
            st.error(payload["error"])
            st.session_state["user"] = None
            st.rerun()
        return True
    return False

def auth_layout():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<div align="center"><h1 class="logo-title">📈 TREDALQ AI</h1><p style="color: #9CA3AF; margin-bottom: 30px;">Institutional Grade Trading Intelligence</p></div>', unsafe_allow_html=True)
    
    if st.session_state["auth_view"] == "login":
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="name@company.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign In Securely")
            if submit:
                with st.spinner("Authenticating..."):
                    u, msg = login_user(email, password)
                    if u:
                        st.session_state["user"] = u
                        st.session_state["page"] = "Dashboard"
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create Account"):
                st.session_state["auth_view"] = "register"
                st.rerun()
        with c2:
            if st.button("Forgot Password?"):
                st.info("Password reset link sent! (Mocked)")

    else:
        with st.form("reg_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="name@company.com")
            password = st.text_input("Password", type="password", help="Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character.")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Create Free Account")
            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Provisioning workspace..."):
                        ok, msg = register_user(name, email, password)
                        if ok:
                            st.success(msg)
                            st.session_state["auth_view"] = "login"
                            st.rerun()
                        else:
                            st.error(msg)
        
        if st.button("Back to Sign In"):
            st.session_state["auth_view"] = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if not check_auth():
    auth_layout()
else:
    u = st.session_state["user"]
    is_admin = u.get("role", "").lower() == "admin"
    
    with st.sidebar:
        st.markdown('<h2 class="logo-title" style="font-size: 24px;">📈 TREDALQ</h2>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background: #1F2937; padding: 12px; border-radius: 8px; margin-bottom: 20px;'>
            <div style='font-weight: 600; color: #F3F4F6;'>{u['name']}</div>
            <div style='font-size: 12px; color: #9CA3AF;'>{u['role']} • {u['email']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='font-size: 12px; color: #6B7280; font-weight: 700; margin-bottom: 10px; text-transform: uppercase;'>Main Menu</div>", unsafe_allow_html=True)
        
        # Role-Based Routing
        if is_admin:
            pages = ["Dashboard", "User Management", "Analytics", "Prediction Logs", "AI Monitoring", "System Settings", "Audit Logs"]
        else:
            pages = ["Dashboard", "Market", "Prediction", "Portfolio", "Watchlist", "Alerts", "Profile"]
            
        selected = st.radio("Navigation", pages, label_visibility="collapsed")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Sign Out"):
            st.session_state["user"] = None
            st.rerun()
            
    # Breadcrumbs & Header
    st.markdown(f"<div style='color: #9CA3AF; font-size: 14px; margin-bottom: 15px;'>TREDALQ / {u['role']} / <b>{selected}</b></div>", unsafe_allow_html=True)
    
    # Route Handler
    try:
        if selected == "Dashboard":
            if is_admin:
                from pages.admin import dashboard as admin_dash
                admin_dash.render(u)
            else:
                from pages import dashboard
                dashboard.render(u)
        elif selected == "Market":
            from pages import market
            market.render(u)
        elif selected == "Prediction":
            from pages import prediction
            prediction.render(u)
        elif selected == "Portfolio":
            from pages import portfolio
            portfolio.render(u)
        elif selected == "Watchlist":
            from pages import watchlist
            watchlist.render(u)
        elif selected == "Alerts":
            from pages import alerts
            alerts.render(u)
        elif selected == "Profile":
            from pages import profile
            profile.render(u)
        # Admin Routes
        elif selected == "User Management":
            from pages.admin import users
            users.render(u)
        elif selected == "Analytics":
            from pages.admin import analytics
            analytics.render(u)
        elif selected == "Prediction Logs":
            from pages.admin import prediction_logs
            prediction_logs.render(u)
        elif selected == "AI Monitoring":
            from pages.admin import ai_models
            ai_models.render(u)
        elif selected == "System Settings":
            from pages.admin import system_health
            system_health.render(u)
        elif selected == "Audit Logs":
            from pages.admin import audit_logs
            audit_logs.render(u)
    except Exception as e:
        st.error(f"Error rendering page '{selected}': {str(e)}")
