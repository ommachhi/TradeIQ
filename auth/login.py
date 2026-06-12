from __future__ import annotations

from typing import Callable

import streamlit as st

from auth.session import start_session
from auth.ui import inject_auth_css, render_left_panel
from auth.utils import validate_email, verify_password
from db.queries import count_recent_failed_logins, get_user_by_email, record_login_attempt, touch_last_login
from utils.constants import LOGIN_RATE_LIMIT_ATTEMPTS, LOGIN_RATE_LIMIT_WINDOW_MINUTES


def _render_tabs(active: str) -> None:
    tab_label = "Sign In" if active == "login" else "Create Account"
    selected = st.radio(
        "",
        ["Sign In", "Create Account"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    if selected == "Create Account":
        st.session_state["auth_view"] = "register"
        st.rerun()
    st.markdown(f"<div class='auth-right-note'>{tab_label}</div>", unsafe_allow_html=True)


def _login_form(on_register: Callable[[], None]) -> None:
    st.markdown("<div class='auth-form-title'>Welcome back</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-form-subtitle'>Sign in to your trading account</div>", unsafe_allow_html=True)
    _render_tabs("login")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email address", placeholder="you@example.com").strip().lower()
        show_password = st.checkbox("👁 Show password")
        password_type = "default" if show_password else "password"
        password = st.text_input("Password", type=password_type)
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        field_errors: dict[str, str] = {}
        if not validate_email(email):
            field_errors["email"] = "Enter a valid email address."
        if not password.strip():
            field_errors["password"] = "Password is required."

        if field_errors:
            if field_errors.get("email"):
                st.markdown(f"<div class='auth-error'>{field_errors['email']}</div>", unsafe_allow_html=True)
            if field_errors.get("password"):
                st.markdown(f"<div class='auth-error'>{field_errors['password']}</div>", unsafe_allow_html=True)
            return

        failed_attempts = count_recent_failed_logins(email, LOGIN_RATE_LIMIT_WINDOW_MINUTES)
        if failed_attempts >= LOGIN_RATE_LIMIT_ATTEMPTS:
            st.error("Too many failed login attempts. Try again in a few minutes.")
            return

        with st.spinner("Signing you in..."):
            user = get_user_by_email(email)
            if not user or not verify_password(password, user["password_hash"]):
                record_login_attempt(email, success=False)
                st.error("Invalid email or password")
                return

            record_login_attempt(email, success=True)
            touch_last_login(int(user["id"]))
            start_session(user)

        st.session_state["auth_view"] = "login"
        st.rerun()

    st.markdown("<div class='auth-divider'>or continue with</div>", unsafe_allow_html=True)
    google_clicked = st.button("Continue with Google", type="secondary", use_container_width=True)
    if google_clicked:
        st.info("Google sign-in is not configured yet.")

    st.markdown("<div class='auth-footer-text'>Don't have an account? Create one free</div>", unsafe_allow_html=True)
    if st.button("Create Account", use_container_width=True):
        on_register()


def _forgot_view(on_back: Callable[[], None]) -> None:
    st.markdown("<div class='auth-form-title'>Forgot password?</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-form-subtitle'>Verify your email and mobile number.</div>", unsafe_allow_html=True)
    with st.form("forgot_password_form", clear_on_submit=False):
        email = st.text_input("Email address", placeholder="you@example.com").strip().lower()
        mobile = st.text_input("Mobile number", placeholder="9876543210").strip()
        submitted = st.form_submit_button("Verify account", use_container_width=True)

    if submitted:
        user = get_user_by_email(email)
        if not user or (user.get("mobile") or "") != mobile:
            st.error("We could not verify that account.")
        else:
            st.session_state["password_reset_email"] = email
            st.session_state["auth_view"] = "reset"
            st.success("Identity verified. You can now reset your password.")
            st.rerun()

    if st.button("Back to login", use_container_width=True):
        on_back()


def _reset_view(on_back: Callable[[], None]) -> None:
    email = st.session_state.get("password_reset_email", "")
    if not email:
        st.info("Start from the forgot-password flow to verify your account.")
        if st.button("Back to login", use_container_width=True):
            on_back()
        return

    st.markdown("<div class='auth-form-title'>Reset password</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-form-subtitle'>Choose a stronger password and confirm it below.</div>", unsafe_allow_html=True)
    with st.form("reset_password_form", clear_on_submit=True):
        password = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Reset password", use_container_width=True)

    if submitted:
        from auth.utils import hash_password, validate_password

        if not validate_password(password):
            st.error("Password must be at least 8 characters with 1 uppercase letter, 1 number, and 1 special character.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            from db.queries import update_user_password

            update_user_password(email, hash_password(password))
            st.session_state.pop("password_reset_email", None)
            st.success("Password updated. Please sign in with your new password.")
            on_back()
            st.rerun()

    if st.button("Back to login", use_container_width=True):
        on_back()


def render_login_view(on_register: Callable[[], None], on_forgot: Callable[[], None]) -> None:
    inject_auth_css()
    left, right = st.columns([0.6, 0.4], gap="large")

    with left:
        render_left_panel()

    with right:
        current_view = st.session_state.get("auth_view", "login")
        if current_view == "forgot":
            _forgot_view(on_back=lambda: st.session_state.__setitem__("auth_view", "login") or st.rerun())
            return
        if current_view == "reset":
            _reset_view(on_back=lambda: st.session_state.__setitem__("auth_view", "login") or st.rerun())
            return
        _login_form(on_register=on_register)
        if st.button("Forgot password?", type="secondary", use_container_width=False):
            st.session_state["auth_view"] = "forgot"
            st.rerun()


def render_forgot_view(on_back: Callable[[], None], on_reset_ready: Callable[[str], None]) -> None:
    del on_reset_ready
    inject_auth_css()
    left, right = st.columns([0.6, 0.4], gap="large")
    with left:
        render_left_panel()
    with right:
        _forgot_view(on_back=on_back)


def render_reset_view(email: str, on_back: Callable[[], None]) -> None:
    del email
    inject_auth_css()
    left, right = st.columns([0.6, 0.4], gap="large")
    with left:
        render_left_panel()
    with right:
        _reset_view(on_back=on_back)
