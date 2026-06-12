import streamlit as st
import re
from auth.auth_manager import login_user, register_user, get_current_user
from utils.helpers import inject_app_css

# Redirect if already logged in
if get_current_user():
    st.switch_page("streamlit_app.py")

# Page configuration
st.set_page_config(
    page_title="TREDALQ | Authentication",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply professional styling
inject_app_css(auth_mode=True)

# CSS for custom styling
st.markdown(
    """
    <style>
    /* Hide sidebar on login page */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
    .feature-bullet {
        margin-bottom: 20px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #6C63FF;
        border-radius: 4px 8px 8px 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Callbacks
def toggle_register():
    st.session_state["show_register"] = not st.session_state.get("show_register", False)
    st.session_state.pop("login_error", None)
    st.session_state.pop("reg_error", None)
    st.session_state.pop("reg_success", None)

# Layout columns
col1, col2 = st.columns([1.2, 1.0], gap="large")

with col1:
    # Left Side: Dark panel with branding & features
    st.markdown(
        """
        <div style="background: linear-gradient(180deg, #121623 0%, #0A0D14 100%); border: 1px solid rgba(108, 99, 255, 0.2); border-radius: 20px; padding: 40px; height: 100%; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);">
            <div style="font-size: 2.5rem; font-weight: 800; color: #FFFFFF; margin-bottom: 5px; letter-spacing: 1px;">📈 TREDALQ</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #6C63FF; margin-bottom: 35px; letter-spacing: 0.5px;">Trade Smarter with AI</div>
            <div style="color: #A7B0C0; font-size: 1.05rem; line-height: 1.7;">
                <div class="feature-bullet">
                    <span style="font-size: 1.2rem; margin-right: 8px;">🤖</span>
                    <b>AI-Powered Intelligence:</b> Access high-accuracy buy/sell signals and target prediction analytics.
                </div>
                <div class="feature-bullet">
                    <span style="font-size: 1.2rem; margin-right: 8px;">📊</span>
                    <b>Live Watchlists:</b> Monitor global and Indian markets with clean dashboards and real-time updates.
                </div>
                <div class="feature-bullet">
                    <span style="font-size: 1.2rem; margin-right: 8px;">🛡️</span>
                    <b>Portfolio Management:</b> Track execution metrics, capital gains, and key transaction histories securely.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    # Right Side: Form
    show_reg = st.session_state.get("show_register", False)
    
    if not show_reg:
        st.markdown("<h2 style='color: #FFFFFF; margin-top: 10px;'>Sign In</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #A7B0C0; margin-bottom: 25px;'>Access your automated trading dashboard</p>", unsafe_allow_html=True)
        
        # Display alerts if any
        if "reg_success" in st.session_state:
            st.success(st.session_state["reg_success"])
            # clear it so it doesn't linger
            st.session_state.pop("reg_success")
            
        if "login_error" in st.session_state:
            st.error(st.session_state["login_error"])
            
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="name@domain.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
        if submitted:
            email = email.strip()
            if not email or not password:
                st.session_state["login_error"] = "Please fill in all fields."
                st.rerun()
            else:
                res = login_user(email, password)
                if res["success"]:
                    st.session_state.pop("login_error", None)
                    st.switch_page("streamlit_app.py")
                else:
                    st.session_state["login_error"] = res["error"]
                    st.rerun()
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<span style='color: #A7B0C0;'>Don't have an account?</span>", unsafe_allow_html=True)
        st.button("Register Now", on_click=toggle_register)
        
    else:
        st.markdown("<h2 style='color: #FFFFFF; margin-top: 10px;'>Create Account</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #A7B0C0; margin-bottom: 25px;'>Get started with AI-driven market intelligence</p>", unsafe_allow_html=True)
        
        # Display alerts if any
        if "reg_error" in st.session_state:
            st.error(st.session_state["reg_error"])
            
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="name@domain.com")
            password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-type password")
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
        if submitted:
            name = name.strip()
            email = email.strip()
            if not name or not email or not password or not confirm_password:
                st.session_state["reg_error"] = "Please fill in all fields."
                st.rerun()
            elif password != confirm_password:
                st.session_state["reg_error"] = "Passwords do not match."
                st.rerun()
            elif len(password) < 8:
                st.session_state["reg_error"] = "Password must be at least 8 characters long."
                st.rerun()
            elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                st.session_state["reg_error"] = "Invalid email format."
                st.rerun()
            else:
                res = register_user(name, email, password)
                if res["success"]:
                    st.session_state.pop("reg_error", None)
                    st.session_state["reg_success"] = "Registration successful! Please login."
                    st.session_state["show_register"] = False
                    st.rerun()
                else:
                    st.session_state["reg_error"] = res["error"]
                    st.rerun()
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<span style='color: #A7B0C0;'>Already have an account?</span>", unsafe_allow_html=True)
        st.button("Sign In Here", on_click=toggle_register)
