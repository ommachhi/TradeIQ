from __future__ import annotations

import streamlit as st


def clear_data_caches() -> None:
    st.cache_data.clear()
