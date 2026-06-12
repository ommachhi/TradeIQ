from __future__ import annotations

from functools import wraps

import streamlit as st

from auth.utils import create_token, decode_token
from db.queries import get_user_by_id
from utils.constants import AUTH_COOKIE_NAME


SESSION_DEFAULTS = {
    "authenticated": False,
    "logged_in": False,
    "user_id": None,
    "name": None,
    "user_name": None,
    "email": None,
    "user_email": None,
    "role": None,
    "auth_token": None,
    "auth_view": "login",
    "nav_page": None,
    "auto_refresh": False,
    "clear_auth_cookie": False,
}


def initialize_session_state() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def _cookie_token() -> str | None:
    try:
        cookie_value = st.context.cookies.get(AUTH_COOKIE_NAME)
    except Exception:
        cookie_value = None
    if not cookie_value:
        return None
    return str(cookie_value)


def restore_session_from_token() -> None:
    if st.session_state.get("clear_auth_cookie"):
        return
    token = st.session_state.get("auth_token") or _cookie_token()
    if not token:
        return
    payload = decode_token(token)
    if not payload:
        reset_auth_state(clear_browser_token=True)
        return
    user = get_user_by_id(int(payload["sub"]))
    if not user:
        reset_auth_state(clear_browser_token=True)
        return
    _set_user_state(user, token)


def _set_user_state(user: dict, token: str) -> None:
    full_name = user.get("full_name") or user.get("name") or ""
    email = user.get("email")
    st.session_state["authenticated"] = True
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["name"] = full_name
    st.session_state["user_name"] = full_name
    st.session_state["email"] = email
    st.session_state["user_email"] = email
    st.session_state["role"] = user["role"]
    st.session_state["auth_token"] = token


def start_session(user: dict) -> None:
    token = create_token(user)
    _set_user_state(user, token)
    st.session_state["clear_auth_cookie"] = False


def reset_auth_state(clear_browser_token: bool = False) -> None:
    st.session_state["authenticated"] = False
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["name"] = None
    st.session_state["user_name"] = None
    st.session_state["email"] = None
    st.session_state["user_email"] = None
    st.session_state["role"] = None
    st.session_state["auth_token"] = None
    st.session_state["nav_page"] = None
    st.session_state["auth_view"] = "login"
    if clear_browser_token:
        st.session_state["clear_auth_cookie"] = True


def clear_session(rerun: bool = True) -> None:
    auto_refresh = st.session_state.get("auto_refresh", False)
    reset_auth_state(clear_browser_token=True)
    st.session_state["auto_refresh"] = auto_refresh
    if rerun:
        st.rerun()


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("logged_in") and not st.session_state.get("authenticated"):
            st.warning("Please sign in to continue.")
            st.session_state["auth_view"] = "login"
            st.stop()
        return func(*args, **kwargs)

    return wrapper


def require_role(role: str) -> None:
    if st.session_state.get("role") != role:
        st.error("Access denied.")
        st.stop()


def logout() -> None:
    clear_session(rerun=False)
    st.rerun()
