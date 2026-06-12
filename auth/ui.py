from __future__ import annotations

import streamlit as st


AUTH_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding: 0 !important; max-width: 100% !important;}
[data-testid="stAppViewContainer"] {
    background: #0B0F1A;
}
[data-testid="stHeader"] {display: none;}
[data-testid="stSidebar"] {display: none;}
.auth-page {
    min-height: 100vh;
    background: #0B0F1A;
}
.auth-panel-left {
    min-height: 100vh;
    background:
        radial-gradient(circle at top right, rgba(108, 99, 255, 0.12), transparent 28%),
        linear-gradient(180deg, #0D1321 0%, #0B0F1A 100%);
    padding: 3rem 3rem 2.5rem;
    color: #E8EEFF;
}
.auth-panel-right {
    min-height: 100vh;
    background: linear-gradient(180deg, #0B0F1A 0%, #09101A 100%);
    padding: 2.5rem;
    color: #E8EEFF;
}
.auth-brand-row {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 1.5rem;
}
.auth-logo-box {
    width: 3rem;
    height: 3rem;
    border-radius: 16px;
    background: linear-gradient(180deg, #6C63FF, #4F46E5);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    letter-spacing: 0.04em;
    box-shadow: 0 16px 32px rgba(108, 99, 255, 0.28);
}
.auth-brand-name {
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: 0.12em;
}
.auth-brand-subtitle {
    color: #6B7A9E;
    font-size: 0.9rem;
    margin-top: 0.15rem;
}
.auth-live-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    border: 1px solid rgba(32, 214, 141, 0.22);
    background: rgba(32, 214, 141, 0.08);
    color: #A9F6D0;
    font-size: 0.82rem;
    margin-bottom: 1.25rem;
}
.auth-live-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #20D68D;
    box-shadow: 0 0 0 4px rgba(32, 214, 141, 0.14);
}
.auth-headline {
    font-size: clamp(2.2rem, 5vw, 4rem);
    line-height: 0.98;
    letter-spacing: -0.04em;
    font-weight: 900;
    max-width: 14ch;
    margin-bottom: 1rem;
}
.auth-subtext {
    color: #A7B0C0;
    font-size: 1rem;
    line-height: 1.7;
    max-width: 36rem;
    margin-bottom: 2rem;
}
.auth-stats-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
    max-width: 34rem;
}
.auth-stat-card {
    border: 1px solid rgba(30, 39, 64, 1);
    background: rgba(19, 25, 41, 0.9);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    min-height: 6.6rem;
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.14);
}
.auth-stat-label {
    color: #E8EEFF;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.55rem;
}
.auth-stat-value {
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    color: #FFFFFF;
}
.auth-stat-note {
    margin-top: 0.35rem;
    color: #6B7A9E;
    font-size: 0.82rem;
}
.auth-form-shell {
    max-width: 34rem;
    margin: 0 auto;
    min-height: 100vh;
    display: flex;
    align-items: center;
}
.auth-form-card {
    width: 100%;
    background: rgba(19, 25, 41, 0.78);
    border: 1px solid rgba(30, 39, 64, 1);
    border-radius: 26px;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
    padding: 1.6rem;
}
.auth-form-card .stTextInput,
.auth-form-card .stSelectbox,
.auth-form-card .stRadio {
    margin-bottom: 0.9rem;
}
.auth-form-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 0.35rem;
}
.auth-form-subtitle {
    color: #6B7A9E;
    margin-bottom: 1.1rem;
}
.auth-tabs {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
    margin-bottom: 1.2rem;
}
.auth-form-card div[data-testid="stRadio"] {
    margin-bottom: 1rem;
}
.auth-form-card div[role="radiogroup"] {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.auth-form-card div[role="radiogroup"] label {
    border-radius: 999px;
    border: 1px solid #1E2740;
    background: #131929;
    padding: 0.35rem 0.75rem;
    color: #A7B0C0;
}
.auth-form-card div[role="radiogroup"] label span {
    color: inherit;
}
.auth-tab {
    display: block;
    border-radius: 999px;
    padding: 0.75rem 1rem;
    text-align: center;
    border: 1px solid rgba(30, 39, 64, 1);
    background: rgba(11, 15, 26, 0.9);
    color: #A7B0C0;
    font-weight: 700;
}
.auth-tab-active {
    background: linear-gradient(180deg, rgba(108, 99, 255, 0.24), rgba(108, 99, 255, 0.12));
    color: #FFFFFF;
    border-color: rgba(108, 99, 255, 0.5);
}
.auth-tab-link {
    cursor: pointer;
    text-decoration: none;
}
.auth-divider {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    color: #6B7A9E;
    margin: 1rem 0;
}
.auth-divider::before,
.auth-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(30, 39, 64, 1);
}
.auth-google-button {
    border: 1px solid rgba(30, 39, 64, 1);
    background: transparent;
    color: #E8EEFF;
}
.auth-link-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-top: 0.6rem;
}
.auth-link {
    color: #A9A4FF;
    text-decoration: none;
    font-weight: 700;
    font-size: 0.9rem;
}
.auth-footer-text {
    margin-top: 1rem;
    color: #6B7A9E;
    text-align: center;
}
.auth-error {
    color: #ff7b7b;
    font-size: 0.82rem;
    margin-top: 0.3rem;
}
.auth-success {
    color: #7cf0b7;
}
div[data-testid="stTextInputRootElement"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] > div,
textarea {
    background: #131929 !important;
    border-color: #1E2740 !important;
    color: #E8EEFF !important;
    border-radius: 14px !important;
}
div[data-testid="stForm"] {
    background: transparent;
    border: 0;
    padding: 0;
}
div[data-testid="stForm"] input,
div[data-testid="stForm"] textarea {
    background: #131929 !important;
}
div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 14px;
    border: 1px solid rgba(108, 99, 255, 0.5);
    background: linear-gradient(180deg, rgba(108, 99, 255, 1), rgba(92, 84, 235, 1));
    color: white;
    font-weight: 700;
    min-height: 2.9rem;
}
div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(180deg, rgba(128, 120, 255, 1), rgba(108, 99, 255, 1));
}
.auth-right-note {
    color: #4A5568;
    font-size: 0.85rem;
    text-align: center;
    margin-top: 0.5rem;
}
@media (max-width: 980px) {
    .auth-panel-left,
    .auth-panel-right {
        min-height: auto;
        padding: 1.5rem;
    }
    .auth-form-shell {
        min-height: auto;
        padding: 1rem 0;
    }
    .auth-stats-grid {
        max-width: 100%;
    }
}
</style>
"""


def inject_auth_css() -> None:
    st.markdown(AUTH_CSS, unsafe_allow_html=True)


def render_left_panel() -> None:
    st.markdown(
        """
        <div class="auth-brand-row">
            <div class="auth-logo-box">TQ</div>
            <div>
                <div class="auth-brand-name">TREDALQ</div>
                <div class="auth-brand-subtitle">AI Trading Intelligence</div>
            </div>
        </div>
        <div class="auth-live-badge"><span class="auth-live-dot"></span>Live market data active</div>
        <div class="auth-headline">Predict smarter. Trade with confidence.</div>
        <div class="auth-subtext">AI-powered stock predictions, real-time analytics, and portfolio intelligence.</div>
        <div class="auth-stats-grid">
            <div class="auth-stat-card">
                <div class="auth-stat-label">LSTM Accuracy</div>
                <div class="auth-stat-value">92.4%</div>
                <div class="auth-stat-note">Time-series trend validation</div>
            </div>
            <div class="auth-stat-card">
                <div class="auth-stat-label">Stocks Tracked</div>
                <div class="auth-stat-value">5,000+</div>
                <div class="auth-stat-note">Indian and global symbols</div>
            </div>
            <div class="auth-stat-card">
                <div class="auth-stat-label">Prediction Speed</div>
                <div class="auth-stat-value">12ms</div>
                <div class="auth-stat-note">Optimized inference pipeline</div>
            </div>
            <div class="auth-stat-card">
                <div class="auth-stat-label">Platform Uptime</div>
                <div class="auth-stat-value">99.9%</div>
                <div class="auth-stat-note">Reliable market sessions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tab_tabs(active: str) -> None:
    sign_in_class = "auth-tab auth-tab-active" if active == "login" else "auth-tab auth-tab-link"
    register_class = "auth-tab auth-tab-active" if active == "register" else "auth-tab auth-tab-link"
    st.markdown(
        f"""
        <div class="auth-tabs">
            <a class="{sign_in_class}" href="#">Sign In</a>
            <a class="{register_class}" href="#">Create Account</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
