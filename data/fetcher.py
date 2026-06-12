from __future__ import annotations

import re
import time

import pandas as pd
import streamlit as st
import yfinance as yf

from db.queries import log_api_usage
from utils.helpers import safe_float


SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9.^-]{1,15}(?:\.(?:NS|BO))?$")


def _candidate_symbols(symbol: str) -> list[str]:
    cleaned = (symbol or "").strip().upper()
    if not cleaned:
        return []
    if "." in cleaned:
        return [cleaned]
    return [cleaned, f"{cleaned}.NS", f"{cleaned}.BO"]


def normalize_symbol(symbol: str) -> str:
    return (symbol or "").strip().upper()


def validate_symbol(symbol: str) -> bool:
    return bool(SYMBOL_PATTERN.fullmatch(normalize_symbol(symbol)))


def _first_value(mapping, *keys):
    for key in keys:
        try:
            value = mapping.get(key)
        except Exception:
            value = None
        if value is not None:
            return value
    return None


@st.cache_data(ttl=900, show_spinner=False)
def get_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    last_error = None
    for candidate in _candidate_symbols(symbol):
        started = time.perf_counter()
        try:
            ticker = yf.Ticker(candidate)
            history = ticker.history(period=period, interval=interval, auto_adjust=False)
            response_ms = (time.perf_counter() - started) * 1000
            log_api_usage("history", candidate, 200 if not history.empty else 404, response_ms)
            if history is not None and not history.empty:
                history = history.reset_index()
                history["Date"] = pd.to_datetime(history["Date"]).dt.tz_localize(None)
                history = history.set_index("Date")
                history.index.name = "Date"
                return history
        except Exception as exc:
            last_error = exc
            response_ms = (time.perf_counter() - started) * 1000
            log_api_usage("history", candidate, 500, response_ms)
    if last_error:
        raise ValueError(f"Unable to fetch market data for '{symbol}': {last_error}") from last_error
    raise ValueError(f"Unable to fetch market data for '{symbol}'.")


@st.cache_data(ttl=60, show_spinner=False)
def get_live_price(symbol: str) -> float:
    for candidate in _candidate_symbols(symbol):
        started = time.perf_counter()
        try:
            ticker = yf.Ticker(candidate)
            fast_info = getattr(ticker, "fast_info", {}) or {}
            price = _first_value(
                fast_info,
                "lastPrice",
                "last_price",
                "regularMarketPrice",
                "currentPrice",
                "close",
            )
            if price is None:
                info = {}
                try:
                    info = ticker.info or {}
                except Exception:
                    info = {}
                price = _first_value(
                    info,
                    "regularMarketPrice",
                    "currentPrice",
                    "ask",
                    "bid",
                    "previousClose",
                )
            if price is None:
                history = ticker.history(period="1d", interval="1m", auto_adjust=False)
                if not history.empty:
                    price = history["Close"].dropna().iloc[-1]
            if price is None:
                history = ticker.history(period="5d", interval="1d", auto_adjust=False)
                if not history.empty:
                    price = history["Close"].dropna().iloc[-1]
            response_ms = (time.perf_counter() - started) * 1000
            log_api_usage("quote", candidate, 200 if price is not None else 404, response_ms)
            if price is not None and safe_float(price) > 0:
                return safe_float(price)
        except Exception:
            response_ms = (time.perf_counter() - started) * 1000
            log_api_usage("quote", candidate, 500, response_ms)
    return 0.0


@st.cache_data(ttl=60, show_spinner=False)
def get_price_snapshot(symbol: str) -> dict:
    history = get_stock_data(symbol, period="3mo", interval="1d")
    if history.empty:
        raise ValueError("No price history returned.")

    close = history["Close"].dropna()
    latest = safe_float(close.iloc[-1])
    prev_day = safe_float(close.iloc[-2]) if len(close) > 1 else latest
    prev_week = safe_float(close.iloc[-6]) if len(close) > 5 else prev_day
    prev_month = safe_float(close.iloc[0]) if len(close) > 20 else prev_day

    return {
        "symbol": normalize_symbol(symbol),
        "last_price": latest,
        "change_1d": ((latest - prev_day) / prev_day * 100) if prev_day else 0.0,
        "change_1w": ((latest - prev_week) / prev_week * 100) if prev_week else 0.0,
        "change_1m": ((latest - prev_month) / prev_month * 100) if prev_month else 0.0,
        "volume": safe_float(history["Volume"].iloc[-1]) if "Volume" in history else 0.0,
        "high": safe_float(history["High"].iloc[-1]),
        "low": safe_float(history["Low"].iloc[-1]),
    }


@st.cache_data(ttl=86400, show_spinner=False)
def get_company_profile(symbol: str) -> dict:
    for candidate in _candidate_symbols(symbol):
        started = time.perf_counter()
        try:
            ticker = yf.Ticker(candidate)
            info = ticker.info or {}
            response_ms = (time.perf_counter() - started) * 1000
            log_api_usage("profile", candidate, 200 if info else 404, response_ms)
            if info:
                return {
                    "symbol": candidate,
                    "name": info.get("longName") or info.get("shortName") or candidate,
                    "sector": info.get("sector") or "Unknown",
                    "industry": info.get("industry") or "Unknown",
                    "market_cap": safe_float(info.get("marketCap")),
                    "currency": info.get("currency") or ("INR" if candidate.endswith((".NS", ".BO")) else "USD"),
                }
        except Exception:
            response_ms = (time.perf_counter() - started) * 1000
            log_api_usage("profile", candidate, 500, response_ms)
    return {
        "symbol": normalize_symbol(symbol),
        "name": normalize_symbol(symbol),
        "sector": "Unknown",
        "industry": "Unknown",
        "market_cap": 0.0,
        "currency": "INR" if normalize_symbol(symbol).endswith((".NS", ".BO")) else "USD",
    }


def get_multi_price_snapshots(symbols: list[str]) -> list[dict]:
    snapshots = []
    for symbol in symbols:
        try:
            snapshots.append(get_price_snapshot(symbol))
        except Exception:
            continue
    return snapshots
