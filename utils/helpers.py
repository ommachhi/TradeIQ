from __future__ import annotations

import json
from datetime import datetime, timezone
from math import isnan

import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from utils.constants import AUTH_COOKIE_NAME, JWT_EXPIRY


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso() -> str:
    return utc_now().isoformat()


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if isnan(number):
        return default
    return number


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def currency_symbol_for_ticker(symbol: str) -> str:
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return "₹"
    return "$"


def format_currency(value: float, symbol: str = "") -> str:
    return f"{currency_symbol_for_ticker(symbol)}{safe_float(value):,.2f}"


def format_percent(value: float) -> str:
    return f"{safe_float(value):.2f}%"


def compute_signal(current_price: float, predicted_price: float, buy_threshold: float = 1.5) -> str:
    if current_price <= 0:
        return "HOLD"
    delta_pct = ((predicted_price - current_price) / current_price) * 100
    if delta_pct >= buy_threshold:
        return "BUY"
    if delta_pct <= -buy_threshold:
        return "SELL"
    return "HOLD"


def compute_trend(current_price: float, predicted_price: float) -> str:
    return "Up" if predicted_price >= current_price else "Down"


def annualized_volatility(close_series) -> float:
    if close_series is None or len(close_series) < 3:
        return 0.0
    returns = np.log(close_series / close_series.shift(1)).dropna()
    if returns.empty:
        return 0.0
    return float(returns.std() * np.sqrt(252) * 100)


def confidence_from_metrics(r2: float | None, error_ratio: float | None) -> float:
    r2_component = 50.0 if r2 is None else max(0.0, min(100.0, (safe_float(r2) + 1) * 50))
    if error_ratio is None:
        return round(r2_component, 1)
    penalty = max(0.0, min(40.0, safe_float(error_ratio) * 100))
    return round(max(5.0, min(99.0, r2_component + 20 - penalty)), 1)


def inject_app_css(auth_mode: bool = False) -> None:
    top_padding = "2rem" if auth_mode else "1.2rem"
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: {top_padding};
            padding-bottom: 2rem;
        }}
        [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at top left, rgba(108, 99, 255, 0.14), transparent 28%),
                radial-gradient(circle at top right, rgba(0, 194, 255, 0.10), transparent 26%),
                linear-gradient(180deg, #0E1117 0%, #0A0D14 100%);
        }}
        .tredalq-card {{
            background: linear-gradient(180deg, rgba(26,31,46,0.96), rgba(18,22,35,0.96));
            border: 1px solid rgba(108, 99, 255, 0.18);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22);
        }}
        .tredalq-auth-shell {{
            min-height: calc(100vh - 5rem);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .tredalq-auth-panel {{
            background: linear-gradient(180deg, rgba(18, 22, 35, 0.98), rgba(13, 17, 27, 0.98));
            border: 1px solid rgba(108, 99, 255, 0.16);
            border-radius: 24px;
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.28);
            padding: 1.15rem 1.15rem 1.25rem;
            max-width: 560px;
            width: 100%;
        }}
        .tredalq-badge {{
            display: inline-block;
            border-radius: 999px;
            padding: 0.22rem 0.7rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .tredalq-badge-buy {{
            background: rgba(24, 196, 123, 0.16);
            color: #6BE3A8;
        }}
        .tredalq-badge-sell {{
            background: rgba(255, 107, 107, 0.16);
            color: #FF9B9B;
        }}
        .tredalq-badge-hold {{
            background: rgba(255, 194, 72, 0.14);
            color: #FFD166;
        }}
        .tredalq-section-title {{
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }}
        .tredalq-section-subtitle {{
            color: #A7B0C0;
            margin-bottom: 1rem;
        }}
        .tredalq-logo {{
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }}
        .tredalq-logo-sub {{
            color: #A7B0C0;
            font-size: 0.88rem;
        }}
        div[data-testid="stForm"] {{
            background: rgba(255,255,255,0.015);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 20px;
            padding: 1.1rem 1rem 1rem;
        }}
        div[data-testid="stTextInputRootElement"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div {{
            background: rgba(30, 36, 54, 0.82);
            border-color: rgba(255, 255, 255, 0.08);
            border-radius: 14px;
        }}
        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {{
            border-radius: 14px;
            min-height: 2.8rem;
            border: 1px solid rgba(255,255,255,0.1);
            background: linear-gradient(180deg, rgba(108,99,255,0.18), rgba(108,99,255,0.08));
        }}
        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {{
            border-color: rgba(108,99,255,0.45);
            color: #FFFFFF;
        }}
        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(26,31,46,0.96), rgba(18,22,35,0.96));
            border: 1px solid rgba(108, 99, 255, 0.18);
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }}
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
            border-radius: 16px;
            overflow: hidden;
        }}
        @media (max-width: 980px) {{
            .tredalq-auth-panel {{
                max-width: 100%;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_badge(label: str) -> str:
    css_class = {
        "BUY": "tredalq-badge-buy",
        "SELL": "tredalq-badge-sell",
    }.get(label.upper(), "tredalq-badge-hold")
    return f'<span class="tredalq-badge {css_class}">{label}</span>'


def enable_auto_refresh(seconds: int = 60) -> None:
    components.html(
        f"""
        <script>
            const intervalMs = {int(seconds) * 1000};
            if (!window.__tredalqRefresh) {{
                window.__tredalqRefresh = setTimeout(() => window.parent.location.reload(), intervalMs);
            }}
        </script>
        """,
        height=0,
    )


def sync_auth_cookie() -> None:
    clear_cookie = bool(st.session_state.get("clear_auth_cookie"))
    token = st.session_state.get("auth_token")

    if clear_cookie:
        components.html(
            f"""
            <script>
                window.parent.document.cookie = "{AUTH_COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax";
            </script>
            """,
            height=0,
        )
        st.session_state["clear_auth_cookie"] = False
        return

    if not token:
        return

    max_age = int(JWT_EXPIRY.total_seconds())
    token_json = json.dumps(str(token))
    components.html(
        f"""
        <script>
            const token = {token_json};
            window.parent.document.cookie =
                "{AUTH_COOKIE_NAME}=" + encodeURIComponent(token) +
                "; max-age={max_age}; path=/; SameSite=Lax";
        </script>
        """,
        height=0,
    )
