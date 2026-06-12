from __future__ import annotations

import streamlit as st

from utils.helpers import format_currency, format_percent, render_badge


def render_metric_card(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label=label, value=value, delta=delta)


def render_prediction_card(symbol: str, result: dict) -> None:
    st.markdown(
        f"""
        <div class="tredalq-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;">
                <div>
                    <div style="font-size:0.85rem; color:#A7B0C0;">{symbol}</div>
                    <div style="font-size:1.7rem; font-weight:700; margin:0.2rem 0;">{format_currency(result["predicted_price"], symbol)}</div>
                    <div style="color:#A7B0C0;">{result["model"]} forecast for the selected horizon</div>
                </div>
                <div>{render_badge(result["signal"])}</div>
            </div>
            <div style="display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:0.8rem; margin-top:1rem;">
                <div>
                    <div style="color:#A7B0C0; font-size:0.82rem;">Confidence</div>
                    <div style="font-size:1.05rem; font-weight:700;">{format_percent(result["confidence"])}</div>
                </div>
                <div>
                    <div style="color:#A7B0C0; font-size:0.82rem;">Trend</div>
                    <div style="font-size:1.05rem; font-weight:700;">{result["trend"]}</div>
                </div>
                <div>
                    <div style="color:#A7B0C0; font-size:0.82rem;">Current</div>
                    <div style="font-size:1.05rem; font-weight:700;">{format_currency(result["current_price"], symbol)}</div>
                </div>
                <div>
                    <div style="color:#A7B0C0; font-size:0.82rem;">Volatility</div>
                    <div style="font-size:1.05rem; font-weight:700;">{format_percent(result["volatility"])}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
