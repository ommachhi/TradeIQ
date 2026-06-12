from __future__ import annotations

import pandas as pd
import streamlit as st

from auth.session import require_login
from db.queries import get_api_usage_summary, get_symbol_api_usage


@require_login
def render() -> None:
    summary = pd.DataFrame(get_api_usage_summary(7))
    symbols = pd.DataFrame(get_symbol_api_usage(7))

    left, right = st.columns(2, gap="large")
    with left:
        if summary.empty:
            st.info("No API usage logged yet.")
        else:
            st.dataframe(summary, use_container_width=True, hide_index=True)
            st.bar_chart(summary.set_index("endpoint")["calls"], use_container_width=True)
    with right:
        if symbols.empty:
            st.info("No symbol-level API activity recorded yet.")
        else:
            st.dataframe(symbols, use_container_width=True, hide_index=True)
            st.bar_chart(symbols.set_index("symbol")["calls"], use_container_width=True)
