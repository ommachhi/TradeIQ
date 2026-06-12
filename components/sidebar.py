from __future__ import annotations

import streamlit as st

from auth.auth_manager import logout_user
from utils.constants import ADMIN_MENU, MENU_ICONS, PAGE_DESCRIPTIONS, USER_MENU


def render_sidebar(role: str, user_name: str) -> str:
    menu_items = ADMIN_MENU if role == "admin" else USER_MENU
    icons = [MENU_ICONS.get(item, "circle") for item in menu_items]
    default_page = st.session_state.get("nav_page") or menu_items[0]
    default_index = menu_items.index(default_page) if default_page in menu_items else 0

    with st.sidebar:
        st.markdown('<div class="tredalq-logo">TREDALQ</div>', unsafe_allow_html=True)
        st.markdown('<div class="tredalq-logo-sub">AI Trading Intelligence Platform</div>', unsafe_allow_html=True)
        st.caption(f"Signed in as {user_name} ({role.title()})")

        try:
            from streamlit_option_menu import option_menu  # type: ignore

            selection = option_menu(
                None,
                menu_items,
                icons=icons,
                default_index=default_index,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#A7B0C0", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "15px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "rgba(108, 99, 255, 0.14)",
                    },
                    "nav-link-selected": {"background-color": "rgba(108, 99, 255, 0.28)"},
                },
            )
        except Exception:
            selection = st.radio("Navigation", menu_items, index=default_index, label_visibility="collapsed")

        st.session_state["auto_refresh"] = st.toggle(
            "Auto-refresh live quotes",
            value=st.session_state.get("auto_refresh", True),
        )
        st.caption(PAGE_DESCRIPTIONS.get(selection, ""))
        if st.button("Logout", use_container_width=True):
            logout_user()

    st.session_state["nav_page"] = selection
    return selection
