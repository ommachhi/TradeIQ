"""Utilities for resolving stock symbols against Yahoo Finance."""

from __future__ import annotations

import yfinance as yf


def _candidate_symbols(symbol: str) -> list[str]:
    cleaned = (symbol or "").strip().upper()
    if not cleaned:
        return []

    # If user already provided an exchange suffix/index symbol, try as-is first.
    if "." in cleaned or cleaned.startswith("^"):
        return [cleaned]

    # Default fallback order: raw symbol, then Indian exchanges.
    return [cleaned, f"{cleaned}.NS", f"{cleaned}.BO"]


def resolve_symbol_with_history(symbol: str, period: str = "2y"):
    """Return (resolved_symbol, history_df) using Yahoo Finance fallback candidates."""
    candidates = _candidate_symbols(symbol)
    if not candidates:
        return None, None

    last_exception = None
    for candidate in candidates:
        try:
            hist = yf.Ticker(candidate).history(period=period)
            if not hist.empty:
                return candidate, hist
        except Exception as exc:  # pragma: no cover - network/data provider errors
            last_exception = exc

    if last_exception:
        raise last_exception
    return None, None
