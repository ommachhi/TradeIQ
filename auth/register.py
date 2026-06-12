from __future__ import annotations

import time
from typing import Callable

import streamlit as st

from auth.ui import inject_auth_css, render_left_panel
from auth.utils import hash_password, validate_email, validate_mobile, validate_password
from db.queries import create_user, get_user_by_email

COUNTRY_OPTIONS = ["India", "USA", "UK", "UAE", "Singapore", "Other"]
EXPERIENCE_OPTIONS = ["Beginner", "Intermediate", "Expert"]


def _render_tabs() -> None:
    selected = st.radio(
        "",
        ["Sign In", "Create Account"],
        index=1,
        horizontal=True,
        label_visibility="collapsed",
    )
    if selected == "Sign In":
        st.session_state["auth_view"] = "login"
        st.rerun()


def _register_form(on_login: Callable[[], None]) -> None:
    st.markdown("<div class='auth-form-title'>Create your account</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-form-subtitle'>Join TREDALQ and start predicting</div>", unsafe_allow_html=True)
    _render_tabs()

    with st.form("register_form", clear_on_submit=False):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address", placeholder="you@example.com").strip().lower()
        password_col, confirm_col = st.columns(2)
        with password_col:
            password = st.text_input("Password", type="password")
        with confirm_col:
            confirm_password = st.text_input("Confirm Password", type="password")
        mobile_col, country_col = st.columns(2)
        with mobile_col:
            mobile = st.text_input("Mobile Number", placeholder="9876543210")
        with country_col:
            country = st.selectbox("Country", COUNTRY_OPTIONS)
        experience = st.radio("Trading Experience", EXPERIENCE_OPTIONS, horizontal=True)
        submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        errors: dict[str, str] = {}
        if not full_name.strip() or len(full_name.strip()) < 3:
            errors["full_name"] = "Full name must be at least 3 characters."
        if not validate_email(email):
            errors["email"] = "Enter a valid email address."
        if len(password) < 8 or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password) or not any(not char.isalnum() for char in password):
            errors["password"] = "Password must be 8+ chars with 1 uppercase, 1 number, and 1 special character."
        if password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."
        if not validate_mobile(mobile):
            errors["mobile"] = "Mobile number must be exactly 10 digits."
        if not country:
            errors["country"] = "Select a country."
        if not experience:
            errors["experience"] = "Select your trading experience."
        if not errors and get_user_by_email(email):
            errors["email_exists"] = "Email already registered."

        if errors:
            for message in errors.values():
                st.markdown(f"<div class='auth-error'>{message}</div>", unsafe_allow_html=True)
            return

        with st.spinner("Creating your account..."):
            create_user(
                full_name=full_name,
                email=email,
                password_hash=hash_password(password),
                mobile=mobile,
                country=country,
                experience=experience,
            )

        st.success("Account created! Please sign in.")
        time.sleep(2)
        st.session_state["auth_view"] = "login"
        st.rerun()

    st.markdown("<div class='auth-footer-text'>Already have an account? Sign in</div>", unsafe_allow_html=True)
    if st.button("Sign In", use_container_width=True):
        on_login()


def render_register_view(on_login: Callable[[], None]) -> None:
    inject_auth_css()
    left, right = st.columns([0.6, 0.4], gap="large")

    with left:
        render_left_panel()

    with right:
        _register_form(on_login=on_login)
