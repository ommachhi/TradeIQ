from __future__ import annotations

import importlib

import streamlit as st

from auth.auth_manager import get_current_user, require_auth
from components.sidebar import render_sidebar
from db.database import initialize_database
from utils.constants import PAGE_DESCRIPTIONS
from utils.helpers import enable_auto_refresh, inject_app_css


def _set_auth_view(view_name: str) -> None:
    st.session_state["auth_view"] = view_name


def _set_reset_email(email: str) -> None:
    st.session_state["password_reset_email"] = email
    _set_auth_view("reset")


def _render_auth_shell() -> None:
    current_view = st.session_state.get("auth_view", "login")
    if current_view == "register":
        render_register_view(on_login=lambda: _set_auth_view("login"))
    else:
        render_login_view(
            on_register=lambda: _set_auth_view("register"),
            on_forgot=lambda: _set_auth_view("forgot"),
        )


def _page_registry() -> dict[str, str]:
    return {
        "Dashboard": "pages.dashboard",
        "Market": "pages.market",
        "Prediction": "pages.prediction",
        "Analytics": "pages.analytics",
        "Portfolio": "pages.portfolio",
        "Watchlist": "pages.watchlist",
        "Alerts": "pages.alerts",
        "Settings": "pages.settings",
        "Users": "pages.admin.users",
        "AI Models": "pages.admin.ai_models",
        "API Monitor": "pages.admin.api_monitor",
        "System Health": "pages.admin.system_health",
    }


def main() -> None:
    st.set_page_config(
        page_title="TREDALQ | AI Trading Intelligence Platform",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_database()

    user = get_current_user()
    if not user:
        st.switch_page("pages/login.py")
        return

    inject_app_css(auth_mode=False)

    selected_page = render_sidebar(user["role"], user["name"])
    if st.session_state.get("auto_refresh"):
        enable_auto_refresh(60)

    st.markdown(f'<div class="tredalq-section-title">{selected_page}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="tredalq-section-subtitle">{PAGE_DESCRIPTIONS.get(selected_page, "")}</div>',
        unsafe_allow_html=True,
    )

    if selected_page in {"Users", "AI Models", "API Monitor", "System Health"}:
        if user["role"] != "admin":
            st.error("Access denied.")
            st.stop()

    module_path = _page_registry().get(selected_page)
    if module_path is None:
        st.error("Requested page is not available.")
        return

    try:
        renderer = importlib.import_module(module_path).render
        renderer()
    except Exception as exc:
        st.error("The page could not be rendered.")
        st.exception(exc)


if __name__ == "__main__":
    main()

