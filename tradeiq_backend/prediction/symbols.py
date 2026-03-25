"""Utilities for resolving stock symbols against Yahoo Finance."""

from __future__ import annotations

import yfinance as yf


def _fetch_history(candidate: str, period: str):
    """Fetch history with fallback APIs used by different yfinance versions."""
    errors = []

    try:
        hist = yf.Ticker(candidate).history(period=period)
        if hist is not None and not hist.empty:
            return hist
    except Exception as exc:  # pragma: no cover
        errors.append(exc)

    try:
        hist = yf.download(
            candidate,
            period=period,
            progress=False,
            auto_adjust=False,
            threads=False,
        )
        if hist is not None and not hist.empty:
            return hist
    except Exception as exc:  # pragma: no cover
        errors.append(exc)

    if errors:
        raise errors[-1]
    return None


def _candidate_periods(period: str) -> list[str]:
    # If provider rejects requested period or returns empty data, retry with sane fallbacks.
    order = [period or "2y", "1y", "6mo"]
    unique = []
    for item in order:
        if item not in unique:
            unique.append(item)
    return unique


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
        for resolved_period in _candidate_periods(period):
            try:
                hist = _fetch_history(candidate, resolved_period)
                if hist is not None and not hist.empty:
                    return candidate, hist
            except Exception as exc:  # pragma: no cover - network/data provider errors
                last_exception = exc

    if last_exception:
        raise last_exception
    return None, None
