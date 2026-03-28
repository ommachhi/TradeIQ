"""Utilities for resolving stock symbols against Yahoo Finance."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timedelta
import yfinance as yf

_CACHE: dict[tuple[str, str], tuple[str, object, datetime]] = {}
_CACHE_TTL_SECONDS = 120
_FETCH_TIMEOUT_SECONDS = 4

# US tickers: AAPL, TSLA, MSFT
# India tickers: RELIANCE.NS, TCS.BO
SYMBOL_PATTERN = re.compile(r"^(?:[A-Z]{1,10}|[A-Z]{1,10}\.(?:NS|BO))$")


def is_valid_stock_symbol_format(symbol: str) -> bool:
    cleaned = (symbol or "").strip().upper()
    return bool(cleaned and SYMBOL_PATTERN.fullmatch(cleaned))


def _cache_get(symbol: str, period: str):
    key = (symbol, period)
    cached = _CACHE.get(key)
    if not cached:
        return None, None
    resolved_symbol, hist, expires_at = cached
    if datetime.utcnow() >= expires_at:
        _CACHE.pop(key, None)
        return None, None
    return resolved_symbol, hist


def _cache_set(symbol: str, period: str, resolved_symbol: str, hist):
    key = (symbol, period)
    _CACHE[key] = (
        resolved_symbol,
        hist,
        datetime.utcnow() + timedelta(seconds=_CACHE_TTL_SECONDS),
    )


def _run_with_timeout(func, *args, timeout_seconds=_FETCH_TIMEOUT_SECONDS, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as exc:
            raise TimeoutError(f"Stock data provider timeout after {timeout_seconds}s") from exc


def _fetch_history(candidate: str, period: str):
    """Fetch history with fallback APIs used by different yfinance versions."""
    errors = []

    try:
        hist = _run_with_timeout(yf.Ticker(candidate).history, period=period)
        if hist is not None and not hist.empty:
            return hist
    except Exception as exc:  # pragma: no cover
        errors.append(exc)

    try:
        hist = _run_with_timeout(
            yf.download,
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
    cleaned = (symbol or "").strip().upper()
    if not is_valid_stock_symbol_format(cleaned):
        return None, None

    cached_symbol, cached_hist = _cache_get(cleaned, period)
    if cached_symbol and cached_hist is not None:
        return cached_symbol, cached_hist

    candidates = _candidate_symbols(cleaned)
    if not candidates:
        return None, None

    last_exception = None
    for candidate in candidates:
        for resolved_period in _candidate_periods(period):
            try:
                hist = _fetch_history(candidate, resolved_period)
                if hist is not None and not hist.empty:
                    _cache_set(cleaned, period, candidate, hist)
                    return candidate, hist
            except Exception as exc:  # pragma: no cover - network/data provider errors
                last_exception = exc

    if last_exception:
        raise last_exception
    return None, None
